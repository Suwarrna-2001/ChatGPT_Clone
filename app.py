import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import engine, Base
from fastapi.staticfiles import StaticFiles

from controllers.chat_controller import router as chats_router
from controllers.session_form_controller import router as session_router
from controllers.history_show_controller import router as history_router
from controllers.register_user_controller import router as register_router
from controllers.login_controller import router as login_router
from controllers.all_user_controller import router as user_router
from controllers.all_session_controller import router as sessions_router
from controllers.all_session_User_controller import router as user_sessions_router
from langchain_components.qaRAG import router as pdf_router
from controllers.protected_route_controller import router as protected_route
from controllers.query_context_ans_controller import router as ans_pdf

import pdb

app = FastAPI()
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

app.mount("/static", StaticFiles(directory="static"), name="static")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)
@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

app.include_router(chats_router)
app.include_router(session_router)
app.include_router(history_router)
app.include_router(register_router)
app.include_router(login_router)
app.include_router(user_router)
app.include_router(sessions_router)
app.include_router(user_sessions_router)
app.include_router(pdf_router)
app.include_router(protected_route)
app.include_router(ans_pdf)