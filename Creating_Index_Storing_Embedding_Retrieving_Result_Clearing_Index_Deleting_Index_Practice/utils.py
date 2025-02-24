
import os
import random
import string
import pinecone
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import CharacterTextSplitter
from pinecone import ServerlessSpec
from langchain_pinecone import PineconeEmbeddings, PineconeVectorStore
from getpass import getpass
import logging
from dotenv import load_dotenv

load_dotenv()

PINECONE_API_KEY=os.getenv("PINECONE_API_KEY")
# Initialize Pinecone
pc=pinecone.Pinecone(api_key=PINECONE_API_KEY)
embeddings = PineconeEmbeddings(model="multilingual-e5-large")

def generate_random_index_name(length=8):
    return "index-" + ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))

def load_file(file):
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
    try:
        pages = load_file(file)
        text_splitter = CharacterTextSplitter(chunk_size=200, chunk_overlap=10, separator="\n")
        chunks = text_splitter.split_documents(pages)
        return chunks
    except Exception as e:
        logging.error(f"Error splitting text: {str(e)}")
        raise

def create_index():
    try:
        index_name = generate_random_index_name()
        if index_name not in pc.list_indexes().names():
            pc.create_index(
                name=index_name, 
                dimension=1024, 
                metric="cosine", 
                spec=ServerlessSpec(cloud="aws", region="us-east-1")
            )
        return index_name
    except Exception as e:
        logging.error(f"Error creating index: {str(e)}")
        raise

def create_store_embedding(file, index_name: str):
    try:
        if index_name not in pc.list_indexes().names():
            pc.create_index(
                name=index_name, 
                dimension=1024, 
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

def semantic_search(query: str, index_name: str):
    try:
        if index_name not in pc.list_indexes().names():
            return {"response": "Index not found."}

        vector_store = PineconeVectorStore(index_name=index_name, embedding=embeddings)
        results = vector_store.similarity_search(query, k=5)

        response = [result.page_content for result in results]
        string_response="\n".join(response)
        return string_response
    except Exception as e:
        logging.error(f"Error in semantic search: {str(e)}")
        raise

def delete_index(index_name: str):
    try:
        if index_name in pc.list_indexes().names():
            pc.delete_index(index_name)
            return {"message": "Index deleted successfully."}
        else:
            return {"message": "Index not found."}
    except Exception as e:
        logging.error(f"Error deleting index: {str(e)}")
        raise
