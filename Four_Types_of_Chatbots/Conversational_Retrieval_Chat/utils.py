import os
import logging
import pinecone
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import CharacterTextSplitter
from pinecone import ServerlessSpec
from langchain_pinecone import PineconeEmbeddings, PineconeVectorStore
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
import psycopg2
from langchain.embeddings import HuggingFaceEmbeddings
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv
load_dotenv()

PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
DB_URL= os.getenv("DB_URL")

MODEL_NAME = "gpt-4o-mini"
# Initialize Pinecone
pc = pinecone.Pinecone(api_key=PINECONE_API_KEY)

# Initialize embeddings
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

def get_db_connection():
    return psycopg2.connect(
        DB_URL,
        cursor_factory=RealDictCursor
    )

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


# ... rest of your code ...
def load_file(file):
    """Load a PDF file and return its pages as documents."""
    try:
        os.makedirs("temp", exist_ok=True)
        file_path = os.path.join("temp", file.filename)
        
        with open(file_path, "wb") as f:
            f.write(file.file.read())
        
        loader = PyPDFLoader(file_path)
        pages = loader.load()
        
        os.remove(file_path)
        return pages
    except Exception as e:
        logging.error(f"Error loading file: {str(e)}")
        raise

def split_text(file):
    """Split the text of a PDF file into manageable chunks."""
    try:
        pages = load_file(file)
        text_splitter = CharacterTextSplitter(chunk_size=200, chunk_overlap=10, separator="\n")
        chunks = text_splitter.split_documents(pages)
        return chunks
    except Exception as e:
        logging.error(f"Error splitting text: {str(e)}")
        raise

def create_store_embedding(file, index_name: str):
    """Create a Pinecone index and store embeddings of the document chunks."""
    try:
        if index_name not in pc.list_indexes().names():
            pc.create_index(
                name=index_name, 
                dimension=384, 
                metric="cosine", 
                spec=ServerlessSpec(cloud="aws", region="us-east-1")
            )

        chunks = split_text(file)
        vector_store = PineconeVectorStore(index_name=index_name, embedding=embeddings)
        vector_store.add_documents(chunks)

        return "The data is stored successfully."
    except Exception as e:
        logging.error(f"Error storing embedding: {str(e)}")
        raise

def generate_response(question):
    """Retrieve context from Pinecone and generate a response using an LLM."""
    try:
        index_name="chat-index"
        chat_history = get_chat_history()
        
        # Check if the specified index exists
        if index_name not in pc.list_indexes().names():
            return {"response": "Index not found."}

        # Initialize the Pinecone vector store
        vector_store = PineconeVectorStore(index_name=index_name, embedding=embeddings)

        # Set up the retriever
        retriever = vector_store.as_retriever(search_type="similarity", search_kwargs={"k": 3})

        # Create a prompt template
        prompt_template = PromptTemplate.from_template(
            "Answer the question based on the context:\n\n{context}\n\nQuestion: {question}\n\n and Chat History:{chat_history}"
        )

        # Create the LLM
        chat_llm = ChatOpenAI(model=MODEL_NAME, openai_api_key=OPENAI_API_KEY, temperature=0)

        # Function to format retrieved documents
        def format_docs(docs):
            return "\n\n".join(doc.page_content for doc in docs)

        # Construct the LCEL chain
        rag_chain = (
            {"context": retriever | format_docs, "question": RunnablePassthrough(),"chat_history": RunnablePassthrough()}
            | prompt_template
            | chat_llm
        )

        # Invoke the chain and return the content
        response = rag_chain.invoke(question)
        save_chat_history(question, response.content)
        return response.content

    except Exception as e:
        logging.error(f"Error in generate_response: {str(e)}")
        raise

# if __name__ == "__main__":
#     while True:
#         user_query = input("You: ")
#         if user_query.lower() in ["exit", "quit"]:
#             print("Ending conversation.")
#             break
#         ai_response = generate_response(user_query)
#         print(f"AI: {ai_response}")
        