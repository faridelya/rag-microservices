# app/dependencies/auth.py
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import Header, HTTPException, Depends
from sqlalchemy.orm import Session
from db.db_connection import get_db
from core.config import Settings
from db_models.models import APIKey, User
import redis
import json

redis_url = Settings().Redis_URL
r = redis.from_url(redis_url, decode_responses=True)
bearer_scheme = HTTPBearer(auto_error=True) 

def validate_api_key(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db),
):
    apikey = credentials.credentials  # Automatically extracts just the token string (without "Bearer ")

    api_key_cache_key = f"apikey:{apikey}"

    # Try to load full API key info from cache
    api_key_data = r.get(api_key_cache_key)
    if api_key_data:
        api_key_dict = json.loads(api_key_data)
    else:
        api_key_obj = db.query(APIKey).filter_by(api_key=apikey, is_active=True).first()
        if not api_key_obj:
            raise HTTPException(status_code=403, detail="Invalid or inactive API key")

        api_key_dict = {
            "id": str(api_key_obj.id),
            "user_id": str(api_key_obj.user_id),
            "tier": api_key_obj.tier,
            "is_active": api_key_obj.is_active,
        }

        r.setex(api_key_cache_key, 300, json.dumps(api_key_dict))  # cache for 5 minutes

    # Try to load user info from cache
    user_cache_key = f"user:{api_key_dict['user_id']}"
    user_data = r.get(user_cache_key)
    if user_data:
        user_dict = json.loads(user_data)
    else:
        user_obj = db.query(User).filter_by(id=api_key_dict["user_id"], is_active=True).first()
        if not user_obj:
            raise HTTPException(status_code=404, detail="User not found")

        user_dict = {
            "id": str(user_obj.id),
            "username": user_obj.name,
            "email": user_obj.email
        }

        r.setex(user_cache_key, 300, json.dumps(user_dict))  # cache for 5 minutes

    # Apply rate limiting based on tier
    tier = api_key_dict["tier"]
    rate_key = f"ratelimit:{apikey}"
    allowed = 3 if tier == "1" else 100

    current = r.get(rate_key)
    if current and int(current) >= allowed:
        raise HTTPException(status_code=429, detail="Rate limit exceeded")

    pipe = r.pipeline()
    pipe.incr(rate_key, 1)
    pipe.expire(rate_key, 60)
    pipe.execute()

    return {
        "user_id": user_dict["id"],
        "username": user_dict["username"],
        "email": user_dict["email"],
        "tier": tier
    }




