from langchain_community.chat_message_histories import SQLChatMessageHistory
from core.config import Settings
import logging

logging.basicConfig(
    level=logging.INFO,  # Set the logging level to INFO
    format='%(asctime)s - %(levelname)s - %(message)s',
    # Customize the log format
)

POSTGRESQL_DATABASE_URL = Settings().DATABASE_URL

def get_history(chat_id: str):
    logging.info(f"Retrieving chat history for session_id: {chat_id}")
    history = SQLChatMessageHistory(
        connection=POSTGRESQL_DATABASE_URL,
        session_id=chat_id,
        # Set to False for synchronous mode
    )

    return history, history.messages[-8:]  # last 8 conversation Q&A
