from fastapi import FastAPI, UploadFile, File
import os
import shutil
from llm.LLMService import model
from utils import jsonconverter
from services.document_processing_service import process_email_file
from filereader.FileReaderAPI import read_file

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# getting instance of FastAPI
app = FastAPI()

# hello world route
@app.get("/")
async def root():
    return {"message": "Hello World"}

# route to handle call to ai model
@app.post("/classify")
async def classify_document(file: UploadFile = File(...)):
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    
    # temporarily saving the file in a folder
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # reading the content passed from input file
    decoded_content = "".join(process_email_file(file_path))
    # decoded_content = read_file(file)

    resp = model._call_gemini(decoded_content)

    # passing the decoded file conten to our LLM model
    response = "JSON response could not be parsed"
    try:
        response = jsonconverter.get_response_string(resp)
    except:
        print("error occured while processing json response")
    return {"filename": file.filename, "content": decoded_content, "response": response}