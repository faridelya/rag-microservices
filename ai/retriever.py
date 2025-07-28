
from langchain_community.vectorstores.azuresearch import AzureSearch
from langchain_openai import OpenAIEmbeddings
from core.config import Settings


openai_api_key: str = Settings().OPENAI_API_KEY
openai_api_version: str = Settings().OPENAI_API_VERSION
model: str = Settings().EMBEDD_MODEL
vector_store_address: str = Settings().VECTOR_STORE_ADDRESS
vector_store_password: str = Settings().VECTOR_STORE_KEY


embeddings = OpenAIEmbeddings(
    openai_api_key=openai_api_key,
    openai_api_version=openai_api_version,
    model=model
)
embedding_function = embeddings.embed_query


def get_azure_search_client(index_name: str):

    vector_store = AzureSearch(
        azure_search_endpoint=vector_store_address,
        azure_search_key=vector_store_password,
        index_name=index_name,
        embedding_function=embedding_function,
    )
    return vector_store

