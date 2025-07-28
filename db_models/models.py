from uuid import uuid4
from sqlalchemy import (
    Boolean,
    Column,
    Integer,
    String,
    ForeignKey,
    ForeignKey,
    DateTime,
    Float,
    UniqueConstraint
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Unicode
from sqlalchemy.dialects.mssql import UNIQUEIDENTIFIER
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(UNIQUEIDENTIFIER, primary_key=True, default=uuid.uuid4, nullable=False)
    name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    role = Column(String(10), default="user", nullable=False)
    created_at = Column(DateTime, default=datetime.now, nullable=False)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, nullable=False)

    chats = relationship("Chat", back_populates="user", cascade="all, delete-orphan")
    api_keys = relationship("APIKey", back_populates="user", cascade="all, delete-orphan")

    __table_args__ = (UniqueConstraint('email', name='uq_users_email'),)




class APIKey(Base):
    __tablename__ = "api_keys"

    id = Column(UNIQUEIDENTIFIER, primary_key=True, default=uuid.uuid4, nullable=False)
    user_id = Column(UNIQUEIDENTIFIER, ForeignKey("users.id"), nullable=False)
    organization = Column(String(255), nullable=False)
    api_key = Column(String(255), unique=True, nullable=False)
    tier = Column(String(10), nullable=False)  # "tier1" or "tier2"
    created_at = Column(DateTime, default=datetime.now)
    is_active = Column(Boolean, default=True)

    user = relationship("User", back_populates="api_keys")






class Chat(Base):
    __tablename__ = "chat"

    chat_id = Column(
        UNIQUEIDENTIFIER,
        primary_key=True,
        default=uuid4,
        unique=True,
        nullable=False,
        index=True,
    )
    title = Column(String(length=255), nullable=False, index=True)
    user_email = Column(String(length=255), ForeignKey("users.email"))
    created_at = Column(DateTime, default=datetime.now())
    last_message_at = Column(DateTime, nullable=True)
    is_active = Column(String, default=True)
    favourite = Column(Boolean, default=False)
    first_question_asked = Column(Boolean, default=True)
    index_name = Column(String(length=255))
    chat_type = Column(String(length=255))
    user = relationship("User", back_populates="chats")
    messages = relationship(
        "Messages", back_populates="chat", cascade="all, delete-orphan"
    )


class Messages(Base):
    __tablename__ = "messages"

    message_id = Column(
        UNIQUEIDENTIFIER,
        default=uuid4,
        primary_key=True,
        unique=True,
        nullable=False,
        index=True,
    )
    chat_id = Column(UNIQUEIDENTIFIER, ForeignKey("chat.chat_id"))
    question = Column(Unicode(1000), nullable=False)
    answer = Column(Unicode(1000), nullable=False)  # Storing answer as JSON
    message_time = Column(DateTime, default=datetime.now())
    chat = relationship("Chat", back_populates="messages")


class ReactionLog(Base):
    __tablename__ = "reaction_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    message_id = Column(UNIQUEIDENTIFIER, ForeignKey("messages.message_id"))
    user_id = Column(String, nullable=False) 
    action = Column(String, nullable=False)
    feedback = Column(String, nullable=True)
    timestamp = Column(DateTime, default=datetime.now)

    message = relationship("Messages")
    