import os
import re
import email
import logging
import tempfile
import pytesseract
from email import policy
from email.parser import BytesParser
from email.message import EmailMessage
from typing import Dict, List, Tuple, Any, Optional, Union
import fitz  # PyMuPDF for PDF processing
import docx2txt  # for Word document processing
from PIL import Image
import numpy as np
import requests

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class EmailProcessor:
    """
    Class for processing emails and their attachments from various input formats.
    Supports .eml files, PDFs containing email content, and .doc/.docx files.
    """
    
    def __init__(self, ocr_enabled: bool = True, ocr_lang: str = 'eng'):
        """
        Initialize the email processor.
        
        Args:
            ocr_enabled: Whether to use OCR for image-based content in PDFs
            ocr_lang: Language for OCR processing
        """
        self.ocr_enabled = ocr_enabled
        self.ocr_lang = ocr_lang
        # Define allowed attachment types for processing
        self.allowed_attachment_types = {
            'pdf': self.process_pdf_file,
            'doc': self.process_word_file,
            'docx': self.process_word_file,
            'txt': self.process_text_file,
            'xlsx': self.process_excel_file,
            'xls': self.process_excel_file,
            'png': self.process_image_file,
            'jpg': self.process_image_file,
            'jpeg': self.process_image_file,
        }
        logger.info("Email processor initialized")
    
    def process_input(self, file_path: str) -> Dict[str, Any]:
        """
        Determines file type and routes to appropriate processor.
        
        Args:
            file_path: Path to the input file
            
        Returns:
            Dict containing processed email data with attachments
        """
        file_extension = os.path.splitext(file_path)[1].lower().replace('.', '')
        
        logger.info(f"Processing input file: {file_path} (type: {file_extension})")
        
        if file_extension == 'eml':
            return self.process_eml_file(file_path)
        elif file_extension == 'pdf':
            # For PDFs, it is either email content or a regular document
            email_data = self.extract_email_from_pdf(file_path)
            if email_data:
                return email_data
            else:
                # Process as attachment
                text_content = self.process_pdf_file(file_path)
                return {
                    'email_body': text_content,
                    'subject': os.path.basename(file_path),
                    'from': '',
                    'to': '',
                    'date': '',
                    'attachments': []
                }
        elif file_extension in ['doc', 'docx']:
            # For Word docs, check if it contains email content
            text_content = self.process_word_file(file_path)
            email_data = self.extract_email_from_text(text_content)
            if email_data:
                return email_data
            else:
                return {
                    'email_body': text_content,
                    'subject': os.path.basename(file_path),
                    'from': '',
                    'to': '',
                    'date': '',
                    'attachments': []
                }
        else:
            logger.warning(f"Unsupported file type: {file_extension}")
            return {
                'email_body': f"Unsupported file type: {file_extension}",
                'subject': os.path.basename(file_path),
                'from': '',
                'to': '',
                'date': '',
                'attachments': []
            }
    
    def process_eml_file(self, file_path: str) -> Dict[str, Any]:
        """
        Process .eml file and extract email content and attachments.
        
        Args:
            file_path: Path to the .eml file
            
        Returns:
            Dict containing email data and processed attachments
        """
        try:
            logger.info(f"Processing .eml file: {file_path}")
            with open(file_path, 'rb') as f:
                msg = BytesParser(policy=policy.default).parse(f)
            
            # Extract basic email metadata
            email_data = {
                'subject': msg.get('Subject', ''),
                'from': msg.get('From', ''),
                'to': msg.get('To', ''),
                'date': msg.get('Date', ''),
                'email_body': '',
                'attachments': []
            }
            
            def extract_text_from_part(part):
                """Extract text content from an email part."""
                if part.get_content_type() == 'text/plain':
                    return part.get_content()
                elif part.get_content_type() == 'text/html':
                    # convert HTML to plain text if no plain text found
                    return part.get_content()
                return ''

            def process_nested_multipart(multipart_msg):
                """Extract mail body when attachment is present"""
                body_text = ''
        
                for part in multipart_msg.iter_parts():
                    content_type = part.get_content_type()
                    
                    # Check for text parts
                    if content_type.startswith('text/'):
                        part_text = extract_text_from_part(part)
                        if part_text and not body_text:
                            body_text = part_text
                    
                    # Handle nested multipart
                    elif content_type.startswith('multipart/'):
                        nested_body = process_nested_multipart(part)
                        if nested_body and not body_text:
                            body_text = nested_body

                    return body_text

            if msg.is_multipart():
                email_data['email_body'] = process_nested_multipart(msg)
            else:
                email_data['email_body'] = msg.get_content()
            
            # Process attachments
            with tempfile.TemporaryDirectory() as temp_dir:
                for part in msg.iter_attachments():
                    try:
                        attachment_name = part.get_filename()
                        if not attachment_name:
                            continue
                            
                        attachment_ext = os.path.splitext(attachment_name)[1].lower().replace('.', '')
                        
                        if attachment_ext not in self.allowed_attachment_types:
                            continue
                        
                        # Save attachment to temp file
                        temp_attachment_path = os.path.join(temp_dir, attachment_name)
                        with open(temp_attachment_path, 'wb') as f:
                            f.write(part.get_payload(decode=True))
                        
                        process_func = self.allowed_attachment_types.get(attachment_ext)
                        if process_func:
                            attachment_text = process_func(temp_attachment_path)
                            
                            email_data['attachments'].append({
                                'filename': attachment_name,
                                'content_type': part.get_content_type(),
                                'extracted_text': attachment_text
                            })
                    except Exception as e:
                        logger.error(f"Error processing attachment {attachment_name}: {str(e)}")
            
            return email_data
        
        except Exception as e:
            logger.error(f"Error processing .eml file {file_path}: {str(e)}")
            return {
                'error': f"Failed to process email: {str(e)}",
                'email_body': '',
                'subject': '',
                'from': '',
                'to': '',
                'date': '',
                'attachments': []
            }
    
    def extract_email_from_pdf(self, file_path: str) -> Optional[Dict[str, Any]]:
        """
        Extract email content from a PDF.
        Uses regex to identify email components.
        
        Args:
            file_path: Path to PDF file
            
        Returns:
            Dict with email data if email format detected, None otherwise
        """
        try:
            # Extract text from PDF
            pdf_text = self.process_pdf_file(file_path)
            
            # Try to extract email components from the text
            return self.extract_email_from_text(pdf_text)
        
        except Exception as e:
            logger.error(f"Error extracting email from PDF {file_path}: {str(e)}")
            return None
    
    def extract_email_from_text(self, text: str) -> Optional[Dict[str, Any]]:
        """
        Try to extract email components from text using regex patterns.
        
        Args:
            text: Text content to analyze
            
        Returns:
            Dict with email data if email format detected, None otherwise
        """
        # Common patterns for email headers
        from_pattern = re.compile(r'From:[\s]*(.*?)[\r\n]', re.IGNORECASE)
        to_pattern = re.compile(r'To:[\s]*(.*?)[\r\n]', re.IGNORECASE)
        subject_pattern = re.compile(r'Subject:[\s]*(.*?)[\r\n]', re.IGNORECASE)
        date_pattern = re.compile(r'Date:[\s]*(.*?)[\r\n]', re.IGNORECASE)
        
        # Try to find matches
        from_match = from_pattern.search(text)
        to_match = to_pattern.search(text)
        subject_match = subject_pattern.search(text)
        date_match = date_pattern.search(text)
        
        # Consider it an email if at least 2 email header patterns match
        matches = [m for m in [from_match, to_match, subject_match, date_match] if m]
        if len(matches) >= 2:
            # Extract the body (everything after the headers)
            headers_end = max(m.end() for m in matches) if matches else 0
            body = text[headers_end:].strip()
            
            return {
                'subject': subject_match.group(1).strip() if subject_match else '',
                'from': from_match.group(1).strip() if from_match else '',
                'to': to_match.group(1).strip() if to_match else '',
                'date': date_match.group(1).strip() if date_match else '',
                'email_body': body,
                'attachments': []
            }
        return None
    
    def process_pdf_file(self, file_path: str) -> str:
        """
        Extract text from PDF file, using OCR if needed.
        
        Args:
            file_path: Path to PDF file
            
        Returns:
            Extracted text content
        """
        try:
            logger.info(f"Processing PDF file: {file_path}")
            
            if not os.path.exists(file_path):
                logger.error(f"PDF file does not exist: {file_path}")
                return f"Error: PDF file does not exist"
            
            if os.path.getsize(file_path) == 0:
                logger.error(f"PDF file is empty: {file_path}")
                return f"Error: PDF file is empty"
        
            text_content = []
            
            # Open the PDF
            try:
                pdf_document = fitz.open(file_path)
            except fitz.FileDataError:
                logger.error(f"Not a valid PDF file: {file_path}")
                return "Error: Not a valid PDF file"
            except fitz.EmptyFileError:
                logger.error(f"PDF file is empty: {file_path}")
                return "Error: PDF file is empty"
            except Exception as e:
                logger.error(f"PyMuPDF error opening file {file_path}: {str(e)}")
            
            for page_num in range(len(pdf_document)):
                page = pdf_document[page_num]
                
                # Try to extract text directly
                page_text = page.get_text()
                
                # If page has little or no text, try OCR if enabled
                if len(page_text.strip()) < 50 and self.ocr_enabled:
                    logger.info(f"Using OCR for page {page_num} of {file_path}")
                    # Convert page to image
                    pix = page.get_pixmap(matrix=fitz.Matrix(300/72, 300/72))
                    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                    
                    # Apply OCR
                    page_text = pytesseract.image_to_string(img, lang=self.ocr_lang)
                
                text_content.append(page_text)
            
            return "\n".join(text_content)
        
        except Exception as e:
            logger.error(f"Error processing PDF file {file_path}: {str(e)}")
            return f"Error extracting text from PDF: {str(e)}"
    
    def process_word_file(self, file_path: str) -> str:
        """
        Extract text from Word document.
        
        Args:
            file_path: Path to Word file (.doc or .docx)
            
        Returns:
            Extracted text content
        """
        try:
            logger.info(f"Processing Word file: {file_path}")
            text = docx2txt.process(file_path)
            return text
        except Exception as e:
            logger.error(f"Error processing Word file {file_path}: {str(e)}")
            return f"Error extracting text from Word document: {str(e)}"
    
    def process_text_file(self, file_path: str) -> str:
        """
        Extract text from plain text file.
        
        Args:
            file_path: Path to text file
            
        Returns:
            File content
        """
        try:
            logger.info(f"Processing text file: {file_path}")
            with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                return f.read()
        except Exception as e:
            logger.error(f"Error processing text file {file_path}: {str(e)}")
            return f"Error extracting text from file: {str(e)}"
    
    def process_excel_file(self, file_path: str) -> str:
        """
        Extract text from Excel file.
        
        Args:
            file_path: Path to Excel file
            
        Returns:
            Extracted text representation of spreadsheet
        """
        try:
            logger.info(f"Processing Excel file: {file_path}")
            
            return f"[Excel content extracted from {os.path.basename(file_path)}]"
        except Exception as e:
            logger.error(f"Error processing Excel file {file_path}: {str(e)}")
            return f"Error extracting text from Excel file: {str(e)}"
    
    def process_image_file(self, file_path: str) -> str:
        """
        Extract text from image using OCR.
        
        Args:
            file_path: Path to image file
            
        Returns:
            Extracted text from image
        """
        url = 'https://api.ocr.space/parse/image'
        payload = {
            'apikey': "K85757301188957",
            'isOverlayRequired': 'false'
        }
        try:
            
            with open(file_path, 'rb') as f:
                files = {'file': f}
                response = requests.post(url, files=files, data=payload)
            response.raise_for_status()
            result = response.json()
            if result['IsErroredOnProcessing']:
                return f"Error: {result['ErrorMessage']}"
            else:
                return result['ParsedResults'][0]['ParsedText']
            
        except Exception as e:
            logger.error(f"Error processing image file {file_path}: {str(e)}")
            return f"Error extracting text from image: {str(e)}"


class DocumentProcessor:
    """
    Class for pre-processing extracted text before passing to LLM.
    """
    
    def __init__(self, max_chunk_size: int = 4000):
        """
        Initialize document processor.
        
        Args:
            max_chunk_size: Maximum size of text chunks for LLM processing
        """
        self.max_chunk_size = max_chunk_size
        logger.info("Document processor initialized")
    
    def preprocess_text(self, text: str) -> str:
        """
        Preprocess text for better quality extraction.
        
        Args:
            text: Raw text content
            
        Returns:
            Preprocessed text
        """
        text = re.sub(r'\s+', ' ', text)
        
        text = text.replace('\r\n', '\n').replace('\r', '\n')
        
        text = re.sub(r'\n{3,}', '\n\n', text)
        
        return text.strip()
    
    def combine_email_with_attachments(self, email_data: Dict[str, Any]) -> str:
        """
        Combine email body with attachment content in a structured format.
        
        Args:
            email_data: Dict containing email body and attachments
            
        Returns:
            Combined text ready for LLM processing
        """
        combined_text = []
        
        # Add email metadata
        combined_text.append("=== EMAIL METADATA ===")
        combined_text.append(f"From: {email_data.get('from', 'Unknown')}")
        combined_text.append(f"To: {email_data.get('to', 'Unknown')}")
        combined_text.append(f"Date: {email_data.get('date', 'Unknown')}")
        combined_text.append(f"Subject: {email_data.get('subject', 'Unknown')}")
        combined_text.append("\n=== EMAIL BODY ===")
        combined_text.append(self.preprocess_text(email_data.get('email_body', '')))
        
        # Add attachment content
        if email_data.get('attachments'):
            for i, attachment in enumerate(email_data['attachments']):
                combined_text.append(f"\n=== ATTACHMENT {i+1}: {attachment.get('filename', 'Unnamed')} ===")
                combined_text.append(self.preprocess_text(attachment.get('extracted_text', '')))
        
        return "\n".join(combined_text)
    
    def chunk_text(self, text: str) -> List[str]:
        """
        Split text into manageable chunks if it exceeds max size.
        
        Args:
            text: Input text
            
        Returns:
            List of text chunks
        """
        if len(text) <= self.max_chunk_size:
            return [text]
        
        chunks = []
        current_pos = 0
        
        while current_pos < len(text):
            end_pos = current_pos + self.max_chunk_size
            if end_pos >= len(text):
                chunks.append(text[current_pos:])
                break
            
            paragraph_break = text.rfind('\n\n', current_pos, end_pos)
            if paragraph_break != -1 and paragraph_break > current_pos + self.max_chunk_size // 2:
                end_pos = paragraph_break
            else:
                sentence_break = text.rfind('. ', current_pos, end_pos)
                if sentence_break != -1 and sentence_break > current_pos + self.max_chunk_size // 2:
                    end_pos = sentence_break + 1
            
            chunks.append(text[current_pos:end_pos])
            current_pos = end_pos
        
        return chunks
    
    def prepare_for_llm(self, email_data: Dict[str, Any]) -> List[str]:
        """
        Prepare email data for LLM processing.
        
        Args:
            email_data: Processed email data with attachments
            
        Returns:
            List of text chunks ready for LLM
        """
        # Combine email and attachments
        combined_text = self.combine_email_with_attachments(email_data)
        
        # Chunk if necessary (shouldn't be needed for email mostly)
        chunks = self.chunk_text(combined_text)
        
        return chunks


# This is the function that will be called in router
def process_email_file(file_path: str) -> List[str]:
    """
    Process an email file and prepare it for LLM processing.
    
    Args:
        file_path: Path to the email file (.eml, .pdf, .doc)
        
    Returns:
        List of text chunks ready for LLM processing
    """
    email_processor = EmailProcessor(ocr_enabled=True)
    document_processor = DocumentProcessor()
    
    # Extract email content and attachments
    email_data = email_processor.process_input(file_path)
    
    # Prepare for LLM processing
    text_chunks = document_processor.prepare_for_llm(email_data)
    
    return text_chunks