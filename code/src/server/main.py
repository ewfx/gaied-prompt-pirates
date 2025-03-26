from fastapi import FastAPI, UploadFile, File,Request
import os
import shutil
import json
from llm.LLMService import model
import llm.DataStore as DataStore
from utils import jsonconverter
from services.document_processing_service import process_email_file
from filereader.FileReaderAPI import read_file
from fastapi.middleware.cors import CORSMiddleware

UPLOAD_DIR = "uploads"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # Get current script's directory
REQUEST_TYPES_FILE_PATH = os.path.join(BASE_DIR, "request_types.json")
os.makedirs(UPLOAD_DIR, exist_ok=True)

origins = [
    "http://localhost:3000",  # React dev server
    "http://localhost:8080",  # If running on same port
]


# getting instance of FastAPI
app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Allow only specified origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],  # Allow all headers
)

if os.path.exists(REQUEST_TYPES_FILE_PATH):
    with open(REQUEST_TYPES_FILE_PATH, "r") as f:
        DataStore.REQUEST_TYPES = json.load(f)
        print("set")
else:
    print("hnkjnjkni")
    DataStore.REQUEST_TYPES=REQUEST_TYPES = {}

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


# route to add/update request types
@app.post("/updateRequestTypes")
async def add_request_type(req:Request):
    new_request=await req.json()
    DataStore.REQUEST_TYPES.update(new_request)
    save_request_types()
    return {"message":"Request Type Succesfully updated"}


# route to delete a request type
@app.delete("/delete/{request_type}")
async def add_request_type(request_type:str):
    request_type.lower()
    del DataStore.REQUEST_TYPES[request_type]
    save_request_types()
    return {"message":"Request Type Succesfully deleted"}

@app.get("/getRequestTypes")
async def get_request_types():
    return DataStore.REQUEST_TYPES


def save_request_types():
    with open(REQUEST_TYPES_FILE_PATH, "w") as f:
        json.dump(DataStore.REQUEST_TYPES, f, indent=4)