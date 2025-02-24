
from fastapi import FastAPI, UploadFile, File

from utils import generate_response, create_store_embedding

app = FastAPI()
@app.post ("/store_embedding")
def store_embedding( index_name: str ,file: UploadFile=File(...)):
    return create_store_embedding(file, index_name)


@app.post("/generate_response")
def get_response(question, index_name: str):
    return generate_response(question, index_name)
