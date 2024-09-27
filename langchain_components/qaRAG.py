import os
import logging
from fastapi import APIRouter, Request, HTTPException, Depends, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import SQLAlchemyError
from models.user import User
from models.session import Session
from langchain_components.replier import prepare_prompt_and_chain, get_context, behavior_configs
from database import get_db  # Import your async session dependency
from pypdf import PdfReader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores.pgvector import PGVector
from fastapi.responses import JSONResponse
from langchain_openai import AzureOpenAIEmbeddings
from pydantic import BaseModel
from dotenv import load_dotenv
from langchain_components.replier import test_invoke
import uuid

load_dotenv()

AZURE_OPENAI_API_KEY = os.getenv('AZURE_OPENAI_API_KEY')
AZURE_OPENAI_ENDPOINT = os.getenv('AZURE_OPENAI_ENDPOINT')
CONNECTION_STRING = os.getenv('CONNECTION_STRING')

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)
router = APIRouter()

embeddings = AzureOpenAIEmbeddings(
    model="text-embedding-3-small",
    azure_endpoint=AZURE_OPENAI_ENDPOINT, 
    api_key=AZURE_OPENAI_API_KEY
)

@router.post("/up")
async def upload_pdf(file: UploadFile = File(...), db: AsyncSession = Depends(get_db)):
    logger.info("Uploaded file: %s", file.filename)

    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Invalid file format. Only PDFs are allowed.")

    pdf_reader = PdfReader(file.file)
    text = ""
    for page in pdf_reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text

    if not text:
        raise HTTPException(status_code=400, detail="Could not extract text from PDF")

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    splits = text_splitter.split_text(text)

    try:
        pg_embedding_store = PGVector(
            connection_string=CONNECTION_STRING,
            embedding_function=embeddings,
            collection_name="pdf_embedding"
        )
        
        pg_embedding_store.add_texts(splits)

        return JSONResponse(content={"message": "PDF processed and stored successfully"})
    
    except Exception as e:
        logger.error(f"Error storing embeddings: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error storing embeddings: {str(e)}")




# Model for querying the PDF
class QueryPDFRequest(BaseModel):
    session_id: str  # Take session_id from the payload
    tone: str = "default"  # Optionally take tone from the payload
    question: str



# API for querying PDF based on stored embeddings
@router.post("/query-pdf/")
async def query_pdf(
    request: QueryPDFRequest, 
    db: AsyncSession = Depends(get_db)
):
    session_id = request.session_id
    tone = request.tone
    question = request.question
    
    try:
        # Retrieve relevant documents based on the query
        pg_embedding_store = PGVector(
            connection_string=CONNECTION_STRING,
            embedding_function=embeddings,
            collection_name="pdf_embedding"
        )
        docs_with_scores = pg_embedding_store.similarity_search_with_score(question, k=3)

        if not docs_with_scores:
            logger.warning(f"No relevant information found for question: {question}")
            return JSONResponse(content={"message": "No relevant information found"}, status_code=404)

        # Join the retrieved context from the PDFs
        context = " ".join([doc.page_content for doc, _ in docs_with_scores])

        return JSONResponse(content={"session_id": session_id, "answer": context})
    
    except Exception as e:
        logger.error(f"Error retrieving embeddings for question '{question}': {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Error retrieving embeddings. Please try again later.")