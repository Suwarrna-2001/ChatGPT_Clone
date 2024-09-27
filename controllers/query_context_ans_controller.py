from fastapi import APIRouter, Request, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
import requests
from models.user import User
from langchain_components.replier import prepare_prompt_and_chain, behavior_configs
from database import get_db
from dotenv import load_dotenv
import os
import logging

load_dotenv()


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)
router = APIRouter()


BASE_URL = os.getenv('BASE_URL', 'http://localhost:3003') 

@router.post("/query-and-respond")
async def query_and_respond(request: Request, db: AsyncSession = Depends(get_db)):
    try:
        body = await request.json()
        session_id = body.get("session_id")
        user_query = body.get("query")
        tone = body.get("tone", "default")
        
        query_pdf_payload = {
            "session_id": session_id,
            "tone": tone,
            "question": user_query
        }

        pdf_response = requests.post(f"{BASE_URL}/query-pdf/", json=query_pdf_payload)

        if pdf_response.status_code == 200:
            context_from_pdf = pdf_response.json().get("answer", "")
            
            final_query = f"{user_query}\n\nContext from your PDF: {context_from_pdf}" if context_from_pdf else user_query
            
            bot_payload = {
                "session_id": session_id,
                "query": final_query,
                "tone": tone
            }
            bot_response = requests.post(f"{BASE_URL}/talk-to-bot", json=bot_payload)

            if bot_response.status_code == 200:
                return bot_response.json()
            else:
                raise HTTPException(status_code=bot_response.status_code, detail="Error from talk-to-bot API")
        else:
            raise HTTPException(status_code=pdf_response.status_code, detail="Error from query-pdf API")

    except Exception as e:
        logger.error(f"Error processing the query: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")
