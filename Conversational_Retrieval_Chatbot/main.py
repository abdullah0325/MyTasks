from fastapi import FastAPI
app = FastAPI()
from utils import get_response,get_all_users

@app.get("/chat_1")
def chat(user_id, user_name, question):
    return get_response(user_id, user_name, question)

@app.get("/chat_2")
def chat(user_id, user_name, question):
    return get_response(user_id, user_name, question)

@app.get("/chat_3")
def chat(user_id, user_name, question):
    return get_response(user_id, user_name, question)

@app.get("/users")
def show_users():
    try :
        all_users = get_all_users()
        return all_users
    except Exception as e:
        return "Failed to fetch users."