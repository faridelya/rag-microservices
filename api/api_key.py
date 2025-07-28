# app/routes/apikey.py
from fastapi import APIRouter, Depends ,HTTPException
from sqlalchemy.orm import Session
from db_models.models import APIKey, User
from db.db_connection import get_db
from core.api_key_auth import validate_api_key
from uuid import uuid4
from core.jwt_utils import get_current_user
import secrets
import redis
from uuid import UUID

router = APIRouter()


r = redis.Redis(host="localhost", port=6379, db=0, decode_responses=True)


@router.post("/create-apikey")
def create_apikey(organization: str, tier: str = "1",
                  current_user: dict = Depends(get_current_user),
                    db: Session = Depends(get_db)):
    
    email = current_user['email']
    user = db.query(User).filter_by(email=email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if tier in ["1","2"]:
        pass
    else:
        raise HTTPException(
        status_code=400,
        detail="Available tier types are '1' or '2'. Please use a valid tier type."
    )

    key = secrets.token_urlsafe(32)
    apikey = APIKey(
        user_id=user.id,
        organization=organization,
        api_key=key,
        tier=tier,
        is_active=True
    )
    db.add(apikey)
    db.commit()
    db.refresh(apikey)

    return {"api_key": apikey.api_key, "tier": tier}



@router.get("/secure-data")
def secure_data(user = Depends(validate_api_key)):
    return {
        "message": f"Welcome {user['username']}",
        "email": user['email'],
        "tier": user['tier']
    }




@router.delete("/apikeys/{api_key_id}")
def deactivate_api_key(
    api_key_id: str,

    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Fetch API key by ID
    apikey = db.query(APIKey).filter_by(api_key=api_key_id).first()

    if not apikey:
        raise HTTPException(status_code=404, detail="API key not found")

    # Optional: check ownership (only allow deletion of your own keys)
    user = db.query(User).filter_by(id=apikey.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Associated user not found")

    # Optional: check ownership (only allow deletion of your own keys)
    if str(user.email) != current_user["email"]:
        raise HTTPException(status_code=403, detail="You do not own this API key")

    # Soft delete (deactivate)
    apikey.is_active = False
    db.commit()

    # Invalidate Redis cache
    redis_apikey_key = f"apikey:{apikey.api_key}"
    redis_user_key = f"user:{apikey.user_id}"

    r.delete(redis_apikey_key)
    r.delete(redis_user_key)
    r.delete(f"ratelimit:{apikey.api_key}")

    return {"message": "API key deactivated successfully"}


@router.get("/my-apikeys")
def get_user_apikeys(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    user_email = current_user["email"]

    # Get user by email
    user = db.query(User).filter_by(email=user_email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Query active API keys for the user
    active_apikeys = (
        db.query(APIKey)
        .filter_by(user_id=user.id, is_active=True)
        .all()
    )

    return [
        {
            "api_key": key.api_key,
            "tier": key.tier,
            "organization": key.organization,
            "created_at": key.created_at
        }
        for key in active_apikeys
    ]