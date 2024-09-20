import os
import logging
from fastapi import APIRouter, Request, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db
from typing import List, Dict, Union
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)
from langchain_community.chat_message_histories import (PostgresChatMessageHistory)
from langchain_core.messages import HumanMessage
router = APIRouter()
from dotenv import load_dotenv

load_dotenv()

CONNECTION_STRING = os.getenv('CONNECTION_STRING')

#message history of a particular session_id
@router.get("/messages/{session_id}")
async def get_history_of_a_session(session_id: str, request: Request, db: AsyncSession = Depends(get_db)) -> List[Dict[str, Union[str, Dict[str, str]]]]:
    try:
        history = PostgresChatMessageHistory(
           connection_string=CONNECTION_STRING,
           session_id=str(session_id)
        )
        msgs = []
        for message in history.messages:
            if isinstance(message, HumanMessage):
               msgs.append({"human": message.content})
            else:
               msgs.append({"ai": message.content})
        
        if not session_id:
            raise HTTPException(status_code=400, detail="session_id is required")
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    return msgs