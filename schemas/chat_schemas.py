from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, UUID4, Json, Field


def current_datetime():
    return datetime.now()


class UserBase(BaseModel):
    email: str
    name: str


class UserCreate(UserBase):
    pass


class User(UserBase):
    id: UUID4

    class Config:
        # orm_mode = True
        from_attributes = True


class MessageBase(BaseModel):
    # chat_id: UUID4
    question: str

    message_time: Optional[datetime] = Field(default_factory=current_datetime)


class MessageCreate(MessageBase):
    pass


class Message(MessageBase):
    message_id: UUID4
    answer: Json[Dict[Any, Any]]
    message_action: Optional[str] = None

    class Config:
        # orm_mode: True
        from_attributes = True  #v2


class ChatBase(BaseModel):
    title: str
    created_at: Optional[datetime] = Field(default_factory=current_datetime)
    last_message_at: Optional[datetime] = None
    is_active: Optional[bool] = True
    favourite: Optional[bool] = False
    call_type: str
    chat_type: str


class ChatCreate(ChatBase):
    pass


class Chat(ChatBase):
    chat_id: UUID4
    user_email: str

    class Config:
        # orm_mode: True
        from_attributes = True


class ChatWithMessages(ChatBase):
    chat_id: UUID4
    user: User

    class Config:
        # orm_mode = True
        from_attributes = True


class ValidIndex(BaseModel):
    index_name: str
    index_description: str


class GroupListResponse(BaseModel):
    group_id: str
    valid_indexes: List[ValidIndex]

class ReactionLogSchema(BaseModel):
    id: int
    message_id: UUID4
    user_id: str
    action: str
    feedback: Optional[str]
    timestamp: datetime

    class Config:
        orm_mode = True
        
        
class SearchRetrievalMetric(BaseModel):
    call_type: str
    chat_type_category: str
    email: str
    usage_count: int
    last_interaction: datetime
    
    
class DocuTalkUsageCategory(BaseModel):
    Category: str
    NumberOfUsers: int
    
class MentorMindUsageCategory(BaseModel):
    Category: str
    NumberOfUsers: int
    
class FeedbackMetricsByMessageType(BaseModel):
    MessageType: str
    ThumbsUp: int
    ThumbsDown: int
    
class DocuTalkThumbsUpTopicPercentage(BaseModel):
    Topic: str
    ThumbsUpCount: int
    ThumbsUpPercentage: float
    TotalThumbsUp: int
    
class DocuTalkThumbsDownTopicPercentage(BaseModel):
    Topic: str
    ThumbsDownCount: int
    ThumbsDownPercentage: float
    TotalThumbsDown: int
    
class MentorMindThumbsUpTopicPercentage(BaseModel):
    Topic: str
    ThumbsUpCount: int
    ThumbsUpPercentage: float
    TotalThumbsUp: int
    
class MentorMindThumbsDownTopicPercentage(BaseModel):
    Topic: str
    ThumbsDownCount: int
    ThumbsDownPercentage: float
    TotalThumbsDown: int
    
class FeedbackRate(BaseModel):
    ThumbsUpPercentage: float
    ThumbsDownPercentage: float
    
    class Config:
        orm_mode = True
    
class FeedbackJobRoleView(BaseModel):
    chat_type: str
    thumbs_up: int
    thumbs_down: int
    
class MostSearchedTopics(BaseModel):
    call_type: str
    chat_type: str
    total_messages: int
    
class InteractionFrequencies(BaseModel):
    frequency: str
    number_of_interactions: int
    
class UserSegmentationJobRole(BaseModel):
    chat_type: str
    number_of_chats: int
    percentage: float
    
class MessageCountMonth(BaseModel):
    year: int
    month: int
    message_count: int
        # orm_mode = True
        # from_attributes = True
        
class OverallEngagementsByPast12Months(BaseModel):
    year: int
    month: int
    message_count: int
    
class User_Message(BaseModel):
    user_question: str
    index_name: str
    indx_filter_id: str
    email: str
    message_time: Optional[datetime] = Field(default_factory=current_datetime)
