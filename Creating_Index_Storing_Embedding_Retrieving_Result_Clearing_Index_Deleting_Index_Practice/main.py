
from fastapi import FastAPI, UploadFile, File
import uvicorn
from utils import create_store_embedding, create_index, delete_index, semantic_search
import logging

# Configure logging
logging.basicConfig(
    filename='app.log', 
    level=logging.INFO, 
    format='%(asctime)s - %(levelname)s - %(message)s'
)



app = FastAPI()

@app.post("/index")
def index():

    try:
        index_name = create_index()
        logging.info(f"Index created: {index_name}")
        return {"index_name": index_name}
    except Exception as e:
        logging.error(f"Error creating index: {str(e)}")
        return {"detail": "Failed to create index"}


@app.post("/store")
def store(index_name: str, file: UploadFile = File(...)):

    try:
        vector_store = create_store_embedding(file, index_name)
        logging.info(f"Data stored in index: {index_name}")
        return {"response": vector_store}
    except Exception as e:
        logging.error(f"Error storing data in index {index_name}: {str(e)}")
        return {"detail": "Failed to store embeddings"}
    
   

@app.get("/search")
def search(query: str, index_name: str):
 
    try:
        results = semantic_search(query, index_name)
        logging.info(f"Search completed in index: {index_name}")
        return {"response": results}
    except Exception as e:
        logging.error(f"Error during search in index {index_name}: {str(e)}")
        return {"detail": "Search failed"}


@app.delete("/delete/")
def delete(index_name: str):

    try:
        result = delete_index(index_name)
        logging.info(f"Index deleted: {index_name}")
        return result
    except Exception as e:
        logging.error(f"Error deleting index {index_name}: {str(e)}")
        return {"detail": "Failed to delete index"}


if __name__ == "__main__":
    uvicorn.run('main:app', host="0.0.0.0", port=4949)
