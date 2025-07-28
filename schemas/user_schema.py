from pydantic import BaseModel
from pydantic import BaseModel, field_validator
from enum import Enum


class UserRole(str, Enum):
    USER = "user"
    ADMIN = "admin"
    SUPERUSER = "superuser"

class UserCreate_SingUp(BaseModel):
    email: str
    name: str
    password: str
    role: UserRole  # Restrict role to one of the enum values

    @field_validator('role')
    def validate_role(cls, v):
        if v not in UserRole.__members__.values():
            raise ValueError(
                f"Invalid role: {v}. Must be one of {list(UserRole)}")
        return v
    
# Schema for user login
class UserLogin(BaseModel):
    email: str
    password: str

# Schema for token response
class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    id_token: str
    token_type: str