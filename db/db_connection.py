from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from langchain_community.chat_message_histories import SQLChatMessageHistory
from core.config import Settings
import logging

logging.basicConfig(
    level=logging.INFO,  # Set the logging level to INFO
    format='%(asctime)s - %(levelname)s - %(message)s',
    # Customize the log format
)

POSTGRESQL_DATABASE_URL = Settings().DATABASE_URL
print(f'===================>DB  {POSTGRESQL_DATABASE_URL}')
# Create sync engine
sync_engine = create_engine(POSTGRESQL_DATABASE_URL, echo=False)
logging.info(f"Database engine has loaded successfully")
# Use sync sessionmaker
SessionLocal = sessionmaker(
    bind=sync_engine,
    autocommit=False,
    autoflush=False,
)


def get_db():
    session = SessionLocal()
    try:
        logging.info("Creating a new database session.")
        yield session
    # except Exception as e:
    #     logger.error(f"An error occurred during the session: {e}")
    #     raise
    finally:
        logging.info("Closing the database session.")
        session.close()


