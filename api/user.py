from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.exc import OperationalError
from fastapi import status
from sqlalchemy.orm import Session
from typing import Optional
from db.db_connection import get_db
from db_models.models import User
from schemas.user_schema import UserCreate_SingUp, TokenResponse, UserLogin, TokenResponse
from core.jwt_utils import (
    hash_password, verify_password, create_tokens, verify_token)
from jwt import ExpiredSignatureError, InvalidTokenError
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

router = APIRouter()

bearer_scheme = HTTPBearer()
# User sign-up endpoint
@router.post("/create_user")
def create_user(user: UserCreate_SingUp, db: Session = Depends(get_db)):
    # Check if the user already exists
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Validate role length
    max_role_length = 50  # Update this according to your DB column size
    role_value = str(user.role.value)
    if len(role_value) > max_role_length:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Role value '{role_value}' exceeds maximum allowed length of {max_role_length} characters."
        )

    # Create a new user
    hashed_password = hash_password(user.password)
    new_user = User(
        email=user.email,
        name=user.name,
        password_hash=hashed_password,
        is_active=True,
        role=role_value
    )

    try:
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return {"message": "Registration successful."}
    except OperationalError as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Database error while creating user. Please check the role value or contact admin."
        )




# User login endpoint
@router.post("/login", response_model=TokenResponse)
def login(user_login: UserLogin, db: Session = Depends(get_db)):
    # Retrieve the user by email
    user = db.query(User).filter(User.email == user_login.email).first()
    if not user:
        raise HTTPException(
            status_code=400,
            detail="Invalid email or password")

    # Verify password
    if not verify_password(user_login.password, user.password_hash):
        raise HTTPException(
            status_code=400,
            detail="Invalid email or password")

    # Generate tokens for the user
    access_token, refresh_token, id_token = create_tokens(
        {"sub": str(user.id), "email": user.email, "role": user.role})

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "id_token": id_token,
        "token_type": "bearer"
    }
    
@router.get("/verify-token")
async def token_verify(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)
):
    """
    Verify the provided token from the 'Authorize' button.
    """
    try:
        token = credentials.credentials  # Extract token directly
        resp = verify_token(token)
        if not isinstance(resp, str):
            return {"message": "Token is valid."}
        raise HTTPException(status_code=401, detail=resp)
    except ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Signature expired. Please log in again.")
    except InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token. Please log in again.")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))