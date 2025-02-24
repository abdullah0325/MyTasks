
import os
import uuid
from langchain_community.document_loaders import PyMuPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
import pinecone

# Load API Key securely
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")  # Ensure API key is set in env variables

# Initialize Pinecone
pinecone.init(api_key=PINECONE_API_KEY, environment="us-west4-gcp")  # Change env as needed

# Generate a random index name
INDEX_NAME = f"rag-index-{uuid.uuid4().hex[:8]}"  # Unique name with 8 random characters

def process_pdf(file_path: str):
    """Load, split, embed using Pinecone, and store document chunks."""
    loader = PyMuPDFLoader(file_path)
    pages = loader.load_and_split()
    
    all_text = "\n".join([page.page_content for page in pages])
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=00, chunk_overlap=20)
    text_chunks = text_splitter.split_text(all_text)
    
    # Create a new Pinecone index dynamically
    pinecone.create_index(INDEX_NAME, dimension=1024, metric="cosine", spec=pinecone.ServerlessSpec(cloud="aws", region="us-west-2"))  # Adjust dimension if needed
    
    index = pinecone.Index(INDEX_NAME)

    # Generate embeddings using Pinecone’s API
    embeddings = index.inference.embed(
        model="huggingface/sentence-transformers/all-MiniLM-L6-v2",
        inputs=text_chunks,
        parameters={"input_type": "passage", "truncate": "END"}
    )
    
    # Upsert embeddings
    vectors = [(str(i), embeddings[i].tolist(), {"text": text_chunks[i]}) for i in range(len(embeddings))]
    index.upsert(vectors)
    
    return f"Document processed and stored in Pinecone index: {INDEX_NAME}"

   