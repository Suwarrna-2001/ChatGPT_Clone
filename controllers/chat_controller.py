import os
import logging
from fastapi import APIRouter, Request, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import SQLAlchemyError
from models.user import User
from models.session import Session
from langchain_components.replier import prepare_prompt_and_chain, get_context, behavior_configs
from database import get_db
import pdb
from typing import List, Dict, Union

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)
from langchain_core.messages import HumanMessage, AIMessage
router = APIRouter()

#ans to query
@router.post("/talk-to-bot")
async def give_ans_to_query(request: Request, db: AsyncSession = Depends(get_db)):
    try:
        body = await request.json()
        session_id = body.get("session_id")
        user_query = body.get("query")
        tone = body.get("tone", "default")
        behavior_config = behavior_configs.get(tone, behavior_configs.get("default"))
        chain = prepare_prompt_and_chain(session_id=session_id, behavior_config=behavior_config)
        result = chain.invoke({"input": user_query}, config={"configurable": {"session_id": session_id}})
        
        return {"session_id": session_id, "response": result.content}
    
    except SQLAlchemyError as e:
        logger.error(f"Database error while processing query: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")
    
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")



  
### yha per session id ki jageh tone store ho rhi hai to ise sahi kerna hai 4 column bane to 
# thik hai verna tone ko store kerne ki jaroorat nhi hai
#session id ko session id me hi store kerna hai