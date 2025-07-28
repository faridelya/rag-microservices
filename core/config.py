from pydantic_settings import BaseSettings
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()
print("########################## ",  os.getenv('DATABASE_URL'))

# class Settings(BaseSettings):
#     DATABASE_URL: str = os.getenv('DATABASE_URL')
#     OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY")
#     OPENAI_API_VERSION: str = os.getenv("OPENAI_API_VERSION")
#     EMBEDD_MODEL: str = os.getenv('EMBEDD_MODEL')
#     GPT_MODEL: str = os.getenv('GPT_MODEL')
#     VECTOR_STORE_ADDRESS: str = os.getenv('AZURE_KNOWLEDGEBASE_URL')
#     VECTOR_STORE_KEY: str = os.getenv('AZURE_KNOWLEDGEBASE_KEY')
#     JWT_SECRET_KEY: str = os.getenv('JWT_SECRET_KEY')
#     ACCESS_TOKEN_EXPIRE_MINUTES: int = os.getenv('ACCESS_TOKEN_EXPIRE_MINUTES')
#     REFRESH_TOKEN_EXPIRE_DAYS: int = os.getenv('REFRESH_TOKEN_EXPIRE_DAYS')

#     class Config:
#         env_file = ".env"

from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    Redis_URL: str
    DATABASE_URL: str
    OPENAI_API_KEY: str
    LANGSMITH_KEY:str
    OPENAI_API_VERSION: str
    EMBEDD_MODEL: str
    GPT_MODEL: str
    VECTOR_STORE_ADDRESS: str  # AZURE_KNOWLEDGEBASE_URL
    VECTOR_STORE_KEY: str      # AZURE_KNOWLEDGEBASE_KEY
    JWT_SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    REFRESH_TOKEN_EXPIRE_DAYS: int
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

# settings = Settings()
# print("2222222===========>", Settings().DATABASE_URL)