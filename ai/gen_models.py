from langchain_openai import ChatOpenAI
from langchain_community.vectorstores.azuresearch import AzureSearch
from core.config import Settings
import os


openai_api_key: str = Settings().OPENAI_API_KEY
gpt_model = Settings().GPT_MODEL
vector_store_address: str = Settings().VECTOR_STORE_ADDRESS
vector_store_password: str = Settings().VECTOR_STORE_KEY







def openai_gpt_model1():
    llm = ChatOpenAI(
        model=gpt_model,
        temperature=0.2,
        max_tokens=None,
        timeout=None,
        max_retries=2,
        api_key=openai_api_key

    )
    return llm


def openai_gpt_model2():
    llm = ChatOpenAI(
        model=gpt_model,
        temperature=0.2,
        max_tokens=None,
        timeout=None,
        max_retries=2,
        api_key=openai_api_key

    )
    return llm
