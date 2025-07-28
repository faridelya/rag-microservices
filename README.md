### **Structure**
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
│   └── __init__.py
├── uv.lock
└── wait-for-it.sh
```

### *Run Docker Compose*
`sudo docker compose up --build -d