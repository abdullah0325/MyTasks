
import logging
import os
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
db_url = os.getenv("POSTGRES_URL")

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
        db_url,
        cursor_factory=RealDictCursor
    )

# Check if user exists in the users table, if not, add the user
def check_and_add_user(user_id, user_name):
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        # Check if user exists
        cur.execute("SELECT * FROM users WHERE user_id = %s", (user_id,))
        user = cur.fetchone()

        # If user does not exist, add user to the users table
        if not user:
            cur.execute(
                "INSERT INTO users (user_id, user_name) VALUES (%s, %s)",
                (user_id, user_name)
            )
            conn.commit()

        cur.close()
        conn.close()

    except Exception as e:
        logging.error("Error managing user: %s", e)
        raise

# Fetch chat history for a user from chat_history_m table
def get_chat_history(user_id):
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        # Fetch chat history for the user
        cur.execute("""
            SELECT user_question, ai_response 
            FROM chat_history_m 
            WHERE user_id = %s 
            ORDER BY id ASC
        """, (user_id,))
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
        raise Exception("Failed to fetch chat history.")

# Store chat history for a specific user in chat_history_m table
def save_chat_history(user_id, question, response):
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        # Insert user chat history into chat_history_m table
        cur.execute(
            """
            INSERT INTO chat_history_m (user_id, user_question, ai_response)
            VALUES (%s, %s, %s)
            RETURNING id
            """,
            (user_id, question, response)
        )
        conn.commit()
        cur.close()
        conn.close()

    except Exception as e:
        logging.error("Error saving chat history: %s", e)
        raise Exception("Failed to save chat history.")
    

def get_all_users():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM users")
        users = cur.fetchall()
        cur.close()
        conn.close()
        return users
    except Exception as e:
        logging.error("Error fetching users: %s", e)
        raise Exception("Failed to fetch users.")

# Get AI response with conversation context
def get_response(user_id, user_name, question):
    if question:
        try:
            # Check and add user if not exists
            check_and_add_user(user_id, user_name)

            # Get chat history for context
            chat_history = get_chat_history(user_id)
            context = f"{chat_history}User: {question}\nAI:"

            model = ChatOpenAI(model="gpt-4o-mini", openai_api_key=OPENAI_API_KEY)
            prompt = ChatPromptTemplate.from_template("Answer the question: {context}")
            output_parser = StrOutputParser()
            qa_chain = prompt | model | output_parser

            response = qa_chain.invoke({"context": context})

            # Save the current conversation to history
            save_chat_history(user_id, question, response)

            logging.info("Response generated successfully.")
            return response
        except Exception as e:
            logging.error("Error occurred: %s", e)
            return "An error occurred. Please try again later."
    else:
        logging.warning("No question provided.")
        return "Please ask a question."

# Uncomment this section to run the script in terminal
# if __name__ == "__main__":
#     user_query = ""
#     user_id = input("Enter user ID: ")
#     user_name = input("Enter user name: ")
#     
#     while user_query.lower() != "exit":
#         user_query = input("Enter your query: ")
#         response = get_response(user_id, user_name, user_query)
#         print(response)
#
#     print("Goodbye!")
