# 🧠 RAG-based Chatbot with User & API Key Management

This is a FastAPI-based backend that implements a **Retrieval-Augmented Generation (RAG)** chatbot using **Azure AI Search** as the vector database. It includes user authentication, API key management, chat history tracking, and MSSQL visualization through SQLPAD.

---

## 🚀 Features

### 🔍 RAG Chatbot (Azure AI Search)
- Semantic search using **Azure AI Search**
- Maintains **chat history per user** and session (Chat ID)
- **Like / Dislike** feedback for chat responses
- Favourite chat
- Rename chat titles
- Disable chats
- Retrieve:
  - All user chats
  - Chats by session ID

### 👤 User Management
- **Sign up / Register**
- **Login** to get JWT **access** and **refresh** tokens

### 🔑 API Key Management
- Create API key per registered user
- **Rate limit** enforced per API key associated to type of tier
- **Delete** API key
- **Validate** API key on API requests

---

## 🐳 Docker Setup

### 🧱 Build and Run Containers

```bash
# Build images and start containers in background
docker compose up --build -d

# Stop and remove containers
docker compose down

```
## URL
- FastAPI `http://localhost:8000/docs`
- SQLPAD UI `http://localhost:3000`

## Adminer Database Configuration
To log into SQLPAD at http://localhost:3000, first use `admin` as user and password for SQLPAD dashboard then connect to your mssql-server container to fill in the connection form as follows:
| Field     | Value                          |
|-----------|--------------------------------|
| System    | Microsoft SQL Server           |
| Server    | mssql-server (container name)  |
| Username  | sa                             |
| Password  | yourStrong\)\_1\_\(Password      |
| Database  | master                         |


## Enviroment Variable (.env)
Make sure to provide a `.env` file in your roject root.
```
Redis_URL="redis://redis-server:6379/0"
DATABASE_URL="mssql+pymssql://sa:yourStrong%29_1_%28Password@mssql:1433/master"
OPENAI_API_KEY=your_openai_api_key
LANGSMITH_KEY=your_langsmith_key
OPENAI_API_VERSION="2023-05-15"
EMBEDD_MODEL=text-embedding-ada-002
GPT_MODEL="gpt-4o-mini-2024-07-18"
VECTOR_STORE_ADDRESS=Azure Ai search index url
VECTOR_STORE_KEY=your_azure_ai_search_key
JWT_SECRET_KEY=super-secret-add any thing 
ACCESS_TOKEN_EXPIRE_MINUTES=5
REFRESH_TOKEN_EXPIRE_DAYS=7
```

### **Project Structure**
```
.
├── ai
│   ├── gen_models.py
│   ├── __init__.py
│   └── retriever.py
├── alembic
│   ├── env.py
│   ├── README
│   ├── script.py.mako
│   └── versions
│       ├── 60547dc1cfdb_fix_relationship_mismatch.py
│       └── 913ec573b6a4_initial_migration.py
├── alembic.ini
├── api
│   ├── api_key.py
│   ├── chat.py
│   ├── __init__.py
│   └── user.py
├── core
│   ├── api_key_auth.py
│   ├── config.py
│   ├── __init__.py
│   └── jwt_utils.py
├── db
│   ├── chat_memory.py
│   └── db_connection.py
├── db_models
│   ├── __init__.py
│   └── models.py
├── docker-compose.yml
├── Dockerfile
├── main.py
├── mssql_data  [error opening dir]
├── pyproject.toml
├── README.md
├── schemas
│   ├── chat_schemas.py
│   ├── __init__.py
│   └── user_schema.py
├── services
│   ├── chat_service.py
│   └── __init__.py
├── tests
│   ├── db test.py
│   └── __init__.py
├── uv.lock
└── wait-for-it.sh
```

## 🛠️ Tech Stack

- **Python** – Core programming language
- **FastAPI** – Backend web framework
- **Uvicorn** – ASGI server for running FastAPI
- **SQLAlchemy** – ORM for database models and interactions
- **Alembic** – Database migrations for SQLAlchemy models
- **LangChain** – Framework for building LLM-based applications
- **LangChain OpenAI** – Integration with OpenAI APIs for embeddings and completions
- **LangChain Unstructured** – For parsing and chunking unstructured documents (e.g. PDFs, Word)
- **LangChain Expression Language (LCEL)** – Used to build modular RAG pipelines
- **LangSmith** – Tracing, observability, and debugging for LangChain apps
- **SQLChatMessageHistory** – Used to persist chat history in MSSQL
- **Azure AI Search** – Vector database for semantic document search
- **AzureSearch (LangChain)** – LangChain wrapper for index creation and search in Azure AI Search
- **Redis (Docker)** – In-memory store for caching and temporary storage
- **MSSQL (Docker)** – SQL Server for chat/message storage
- **Docker** – Containerization of all services
- **Docker Compose** – Orchestration of multi-container application
- **OpenAI API Key** – Access to OpenAI’s GPT and embedding models
- **python-jose** – JWT authentication and token verification
- **uv** – Lightweight Python dependency and virtual environment manager

