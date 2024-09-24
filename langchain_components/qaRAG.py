from fastapi import UploadFile, File, HTTPException, APIRouter
from pypdf import PdfReader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores.pgvector import PGVector
from fastapi.responses import JSONResponse
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import logging


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)
from langchain_openai import AzureOpenAIEmbeddings
router = APIRouter()
#text-embedding-3-small

# Environment variables
AZURE_OPENAI_API_KEY = os.getenv('AZURE_OPENAI_API_KEY')
AZURE_OPENAI_ENDPOINT = os.getenv('AZURE_OPENAI_ENDPOINT')
CONNECTION_STRING = os.getenv('CONNECTION_STRING')

# Initialize OpenAI embeddings
embedding_model = AzureOpenAIEmbeddings(azure_endpoint=AZURE_OPENAI_ENDPOINT, api_key=AZURE_OPENAI_API_KEY, api_version="2024-02-15-preview",deployment_name="text-embedding-3-small")

# PostgreSQL connection and session setup
engine = create_engine(CONNECTION_STRING)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@router.post("/up")
async def upload_pdf(file: UploadFile = File(...)):
    print("Uploaded file:", file.filename)
    
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Invalid file format. Only PDFs are allowed.")

    # Step 1: Load the PDF document
    pdf_reader = PdfReader(file.file)
    text = ""
    for page in pdf_reader.pages:
        page_text = page.extract_text()
        if page_text:  # Check if text was extracted
            text += page_text

    print("Extracted text:", text)

    if not text:
        raise HTTPException(status_code=400, detail="Could not extract text from PDF")

    # Step 2: Split the text into chunks
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    splits = text_splitter.split_text(text)

    # Step 3: Store the chunks with embeddings in pgvector
    try:
        with SessionLocal() as session:
            pg_embedding_store = PGVector(
                connection_string=CONNECTION_STRING,
                embedding_function=embedding_model,
                collection_name="pdf_embeddings"  # Customize as needed
            )

            # Store each chunk in pgvector with embeddings
            pg_embedding_store.add_texts(splits)

        return JSONResponse(content={"message": "PDF processed and stored successfully"})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error storing embeddings: {str(e)}")



@router.post("/query-pdf/")
async def query_pdf(question: str):
    try:
        # Step 4: Load the vector store and use the retriever
        with SessionLocal() as session:
            pg_embedding_store = PGVector(
                connection_string=CONNECTION_STRING,
                embedding_function=embedding_model,
                collection_name="pdf_embeddings"
            )

            # Retrieve the most relevant documents based on the query
            docs_with_scores = pg_embedding_store.similarity_search_with_score(question, k=3)
            
            # Compile the most relevant information
            if not docs_with_scores:
                return JSONResponse(content={"message": "No relevant information found"}, status_code=404)
            
            answer = " ".join([doc.page_content for doc, _ in docs_with_scores])
            return JSONResponse(content={"answer": answer})

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving embeddings: {str(e)}")




'''
{
    "detail": "Error storing embeddings: Error code: 404 - {'error': {'code': 'DeploymentNotFound', 
    'message': 'The API deployment for this resource does not exist. 
    If you created the deployment within the last 5 minutes, please wait a moment and try again.'}}"
}
'''