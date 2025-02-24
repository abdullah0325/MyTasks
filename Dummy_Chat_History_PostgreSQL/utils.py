from pydantic import BaseModel
import psycopg2
from psycopg2.extras import RealDictCursor
from typing import Optional, List
import os 
from dotenv import load_dotenv
load_dotenv()

DB_url = os.getenv("DB_url")


# Database connection configuration
def get_db_connection():
    return psycopg2.connect(
        DB_url,
        cursor_factory=RealDictCursor
    )

# Pydantic model for data validation
class ChatHistoryModel(BaseModel):
    id: Optional[int]
    user_question: str
    ai_response: str


def response(user_question: str):
    if not user_question:
        return "Please enter a valid question"
    
    ai_response = "I am here to help you"
    
    # Store in database
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO new_chat_history (user_question, ai_response)
        VALUES (%s, %s)
        RETURNING id, user_question, ai_response
        """,
        (user_question, ai_response)
    )
    conn.commit()
    result = cur.fetchone()
    cur.close()
    conn.close()
    
    return ai_response




def get_chat_history(id: Optional[int] = None):
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    if id:
        cur.execute(
            """
            SELECT id, user_question, ai_response 
            FROM new_chat_history 
            WHERE id = %s
            """,
            (id,)
        )
        result = cur.fetchone()
        cur.close()
        conn.close()
        if not result:
            return "Chat history not found"
        return result
    else:
        cur.execute(
            """
            SELECT id, user_question, ai_response 
            FROM new_chat_history
            """
        )
        results = cur.fetchall()
        cur.close()
        conn.close()
        return results


def update_chat_history(id: int, user_question: str, ai_response: str):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        """
        UPDATE new_chat_history 
        SET user_question = %s, ai_response = %s
        WHERE id = %s
        RETURNING id, user_question, ai_response
        """,
        (user_question, ai_response, id)
    )
    conn.commit()
    result = cur.fetchone()
    cur.close()
    conn.close()
    
    if not result:
        raise ValueError("Chat history not found")
    
    return result



def delete_chat_history(id: int):
    conn= get_db_connection()
    cur= conn.cursor()
    cur.execute(
        """
        DELETE FROM new_chat_history
        WHERE id = %s
        RETURNING id, user_question, ai_response 
        """,
        (id,)
    )
    conn.commit()
    deleted_record= cur.fetchone()
    cur.close()
    conn.close()
    if not deleted_record:
        return "Chat history not found"
    return "Chat history deleted successfully", deleted_record