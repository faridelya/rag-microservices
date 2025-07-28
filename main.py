from fastapi import FastAPI
from api.chat import router as chat_router
from api.user import router as user_router
from api.api_key import router as apikey_router
import uvicorn
import os
import logging
from fastapi.middleware.cors import CORSMiddleware



logging.basicConfig(
    level=logging.INFO,  # Set the default logging level
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',  # Log format
)
logger = logging.getLogger("fastapi_app")

app = FastAPI()

# Include the API router with a prefix
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/", tags=["Bonjour"])
async def root():
    return {"message": "Welcome to the FastAPI Rag Application!"}
app.include_router(user_router, prefix="/api", tags=["User Management"])
app.include_router(apikey_router, prefix="/api", tags=["API Key Management"])

app.include_router(chat_router, prefix="/api", tags=["Chat APIs"])


if __name__ == "__main__":

    uvicorn.run(app, host="0.0.0.0", port=8800)
