from fastapi import FastAPI
from utils import get_response

app = FastAPI()

@app.get("/")
def chat(prompt):
    return get_response(prompt)


