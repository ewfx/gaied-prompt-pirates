from typing import Dict
from PyPDF2 import PdfReader
from email import message_from_bytes
from docx import Document
import io
from fastapi import UploadFile

def read_pdf(file: UploadFile) -> str:
    reader = PdfReader(file.file)
    text = "\n".join(page.extract_text() for page in reader.pages if page.extract_text())
    return text or "No readable text found."

def read_eml(file: UploadFile) -> str:
    msg = message_from_bytes(file.file.read())
    return msg.get_payload() if isinstance(msg.get_payload(), str) else "Cannot parse email content."

def read_docx(file: UploadFile) -> str:
    doc = Document(io.BytesIO(file.file.read()))
    return "\n".join(para.text for para in doc.paragraphs)

def read_generic(file: UploadFile) -> str:
    try:
        return file.file.read().decode(errors='ignore')
    except Exception:
        return "Binary file content cannot be displayed."
    
def read_file(file: UploadFile) -> str:
    if file.filename.endswith(".pdf"):
        content = read_pdf(file)
    elif file.filename.endswith(".eml"):
        content = read_eml(file)
    elif file.filename.endswith(".docx"):
        content = read_docx(file)
    else:
        content = read_generic(file)

    return content;