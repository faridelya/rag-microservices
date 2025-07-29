from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from fastapi.responses import JSONResponse
from fastapi.responses import StreamingResponse , FileResponse
from starlette.background import BackgroundTask
from pydantic import UUID4
from requests import session
from db.db_connection import get_db
from db.chat_memory import get_history
from sqlalchemy.orm import Session, joinedload
from db_models import models
import tempfile
from typing import List, Dict
from schemas.chat_schemas import (
    ChatCreate,
    Chat,
    Message,
    MessageCreate,

    ChatWithMessages,
    User_Message
)
import json, os
from sqlalchemy import and_
from core.jwt_utils import get_current_user
from core.api_key_auth import validate_api_key
from services.chat_service import generate_customer_response
from ai.retriever import get_azure_search_client
from langchain.memory import ConversationBufferWindowMemory
from ai.gen_models import openai_gpt_model1
from core.config import Settings
import logging



router = APIRouter()
vector_store_instance = get_azure_search_client("nbsknowledgeindex")


os.environ["LANGSMITH_TRACING"] = "true"
os.environ["LANGSMITH_PROJECT"] =   "NBS Task"
os.environ["LANGSMITH_ENDPOINT"] = "https://api.smith.langchain.com"
os.environ['LANGSMITH_API_KEY'] = Settings().LANGSMITH_KEY
os.environ["OPENAI_API_KEY"] = Settings().OPENAI_API_KEY


# vector_store_instance = get_azure_search_client(index_name = "team"  )
llm = openai_gpt_model1()

@router.get("/chat", response_model=List[ChatWithMessages])
def get_chat(
    current_user: dict = Depends(validate_api_key),
    db: Session = Depends(get_db),
):
    # print(current_user)
    user_email = current_user["email"]
    # print(user_email)
    chat_sessions = (
        db.query(models.Chat)
        .join(models.User)
        .options(joinedload(models.Chat.messages))
        .filter(
            and_(
                models.Chat.user_email == user_email, models.Chat.is_active
            )  # Note: use True instead of "true"
        )
        .order_by(models.Chat.created_at.desc())
        .all()
    )
    # print(chat_sessions)
    return chat_sessions



@router.post("/chat", response_model=Chat, description="Create new Chat and return chat id for session",)
def create_chat(
    chat: ChatCreate,
    current_user: dict = Depends(validate_api_key),
    db: Session = Depends(get_db),
):
    logging.info("get chat")
    
    user_email = current_user['email']

    new_chat = models.Chat(
        user_email=user_email,
        title="",
        created_at=chat.created_at,
        last_message_at=chat.last_message_at,
        is_active=chat.is_active,
        favourite=chat.favourite,
        index_name=chat.index_name,
        chat_type=chat.chat_type,
    )
    db.add(new_chat)
    db.commit()
    db.refresh(new_chat)
    return new_chat


@router.get("/chat/{chat_id}", response_model=list[Message],
             description="Returns conversation history by using the provided session (chat) ID.",)  
def geting_chat(
    chat_id: UUID4,
    skip: int = 0,
    limit: int = 20,
    current_user: dict = Depends(validate_api_key),
    db: Session = Depends(get_db),
):
    chat_sessions = (
        db.query(models.Messages)
        .filter(models.Messages.chat_id == chat_id)
        .order_by(models.Messages.message_time.asc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    for item in chat_sessions:
        uuid_str = str(item.message_id)
        messageid = uuid_str.split(":")[-1]
        message_action = db.query(models.ReactionLog.action).\
        join(models.Messages, models.Messages.message_id == models.ReactionLog.message_id).\
        filter(models.Messages.message_id == messageid).\
        first()
        if message_action:
            item.message_action = message_action.action
        else:
            item.message_action = ""
    return chat_sessions


@router.post("/chat/{chat_id}/messages",  description="Chat based on Rag method with documents",)
async def chating_with_doc(
    message: MessageCreate,
    chat_id: UUID4,
    current_user: dict = Depends(validate_api_key),
    db: Session = Depends(get_db),
):   #-> StreamingResponse:
    
    try:
        # email = current_user["email"]
        email = current_user['email']
        

        chat_to_update = (
            db.query(
                models.Chat) .filter(
                and_(
                    models.Chat.chat_id == chat_id,
                    models.Chat.user_email == email)) .first())

        if not chat_to_update:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="chat not found"
            )
        chat_history, limit_histmemory = get_history(str(chat_id))
        if chat_to_update and chat_to_update.first_question_asked:
            chat_to_update.title = message.question[:75]
            chat_to_update.first_question_asked = False
            db.commit()
        # res = llm.invoke(message.question)
        # return res.content
        response = await generate_customer_response(
            sqlchat_history=chat_history,
            limit_histmemory=limit_histmemory,
            prompt=message.question,
            retriever=vector_store_instance,
            chat_id=chat_id,
            message=message.question,
            message_time=message.message_time,
            db=db
        )
        return response

    except Exception as e:
        raise HTTPException(status_code=500,
                            detail=f"Internal Server Error: {str(e)}")


    


@router.patch("/chat/{chat_id}/disable", response_model=Chat)
def disable_chat(
    chat_id: UUID4,
    current_user: dict = Depends(validate_api_key),
    db: Session = Depends(get_db),
):
    chat = db.query(models.Chat).filter(models.Chat.chat_id == chat_id).first()
    if not chat:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Chat not found"
        )
    chat.is_active = False
    db.commit()
    return chat


@router.post("/chat/{chat_id}/favourite", response_model=Chat)
def favourite_chat(
    chat_id: UUID4,
    current_user: dict = Depends(validate_api_key),
    db: Session = Depends(get_db),
):
    chat = db.query(models.Chat).filter(models.Chat.chat_id == chat_id).first()
    if not chat:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Chat not found"
        )
    if chat.favourite:
        chat.favourite = False
    else:
        chat.favourite = True
    db.commit()
    return chat


@router.put(
    "/chat/{chat_id}/title",
    status_code=status.HTTP_200_OK,
    response_model=Dict[str, str],
)
def update_chat_title(
    chat_id: UUID4,
    new_title: str,
    current_user: dict = Depends(validate_api_key),
    db: Session = Depends(get_db),
):
    logging.info("info***********%s", chat_id)
    chat_to_update = (
        db.query(models.Chat).filter(models.Chat.chat_id == chat_id).first()
    )
    # print(db.query(models.Chat).filter(models.Chat.chat_id == chat_id).first())
    # print(chat_to_update)
    logging.info("info*********** %s ,%s", chat_id, chat_to_update)
    if not chat_to_update:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Chat not found"
        )
    new_title = new_title.strip()
    if not new_title:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Title is empty"
        )

    chat_to_update.title = new_title
    db.commit()
    return {
        "status": "success",
        "message": f"Chat title updated successfully to {new_title}",
    }

@router.post("/message/{message_id}/react", response_model=Message)
def react_to_message(
    message_id: UUID4,
    action: str,
    feedback: str = None,
    current_user: dict = Depends(validate_api_key),
    db: Session = Depends(get_db),
):
    # Retrieve the message from the database
    message = db.query(models.Messages).filter(models.Messages.message_id == message_id).first()
    if not message:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Message not found"
        )

    # Create a log entry for the reaction
    log_entry = models.ReactionLog(
        message_id=message_id,
        user_id=current_user["email"],
        action=action,
        feedback=feedback
    )
    db.add(log_entry)

    # Save changes to the database
    db.commit()

    return message