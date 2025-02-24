from fastapi import FastAPI
from fastapi import Depends
from utils import response, get_chat_history, update_chat_history, delete_chat_history

app = FastAPI()

@app.post("/chatbot/")
def chat(user_question:str):
    return response(user_question)

@app.get("/chatbot/history")
def chat_history(id: int = None):
    return get_chat_history(id)


@app.put("/chatbot/update")
def update_history(id:int, user_question:str, ai_response:str):
    return update_chat_history(id, user_question, ai_response)


@app.delete("/chatbot/delete")
def delete_history(id:int):
    return delete_chat_history(id)