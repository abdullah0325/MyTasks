import logging
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv
load_dotenv()

# Load environment variables
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY
DB_URL= os.getenv("DB_URL")

# Configure logging
logging.basicConfig(
    filename='app.log',
    filemode='a',
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Database connection
def get_db_connection():
    return psycopg2.connect(
        DB_URL,
        cursor_factory=RealDictCursor
    )

# Fetch chat history to maintain context
def get_chat_history():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT user_question, ai_response 
            FROM new_chat_history 
            ORDER BY id ASC
        """)
        chat_history = cur.fetchall()
        cur.close()
        conn.close()
        
        # Format chat history for prompt
        history = ""
        for chat in chat_history:
            history += f"User: {chat['user_question']}\nAI: {chat['ai_response']}\n"
        return history
    except Exception as e:
        logging.error("Error fetching chat history: %s", e)
        return ""
    


# Store chat in history
def save_chat_history(question, response):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO new_chat_history (user_question, ai_response)
            VALUES (%s, %s)
            RETURNING id
            """,
            (question, response)
        )
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        logging.error("Error saving chat history: %s", e)

# Get AI response with conversation context
def get_response(question):
    if question:
        try:
            # Get chat history for context
            chat_history = get_chat_history()
            context = f"{chat_history}User: {question}\nAI:"

            model = ChatOpenAI(model="gpt-4o-mini", openai_api_key=OPENAI_API_KEY)
            prompt = ChatPromptTemplate.from_template("Answer the question: {context}")
            output_parser = StrOutputParser()
            qa_chain = prompt | model | output_parser

            response = qa_chain.invoke({"context": context})

            # Save the current conversation to history
            save_chat_history(question, response)

            logging.info("Response generated successfully.")
            return response
        except Exception as e:
            logging.error("Error occurred: %s", e)
            return "An error occurred. Please try again later."
    else:
        logging.warning("No question provided.")
        return "Please ask a question."


if __name__ == "__main__":
    user_query = input("Enter your query: ")    
    while user_query.lower() != "exit":
        user_query = input("Enter your query: ")
        resoponse = get_response(user_query)
        print(resoponse)

    print("Goodbye!")