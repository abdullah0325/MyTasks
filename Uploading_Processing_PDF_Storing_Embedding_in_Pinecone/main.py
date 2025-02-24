import os
from fastapi import FastAPI, UploadFile, File, HTTPException
from utils import process_pdf

app = FastAPI()

# Directory where uploaded files will be stored
UPLOAD_DIRECTORY = "./uploaded_files"

# Ensure the upload directory exists
os.makedirs(UPLOAD_DIRECTORY, exist_ok=True)

@app.post("/upload/")
async def process_file(file: UploadFile = File(...)):
    try:
        # Construct the file path
        file_path = os.path.join(UPLOAD_DIRECTORY, file.filename)
        # Save the uploaded file
        with open(file_path, "wb") as buffer:
            buffer.write(await file.read())
        return process_pdf(file_path)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred while uploading the file: {str(e)}")

