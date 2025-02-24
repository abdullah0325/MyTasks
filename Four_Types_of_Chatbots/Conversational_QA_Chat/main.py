from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from util import get_response

app = FastAPI()

# Allow CORS for frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/chat/")
def chat_bot(user_query: str = Query(..., description="User's query to the chatbot")):
    response = get_response(user_query)
    return {"response": response}
