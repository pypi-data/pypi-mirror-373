# in tenxagent/schemas.py
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime


class ToolCall(BaseModel):
    id: str
    name: str
    arguments: Dict[str, Any]
     
class Message(BaseModel):
    role: str
    content: Optional[str] = None
    tool_calls: Optional[List[ToolCall]] = None
    tool_call_id: Optional[str] = None

# A schema to standardize the output from any language model
class GenerationResult(BaseModel):
    message: Message
    input_tokens: int
    output_tokens: int

# Custom message schema for MongoDB storage
class MongoMessage(BaseModel):
    user_id: str
    session_id: str 
    type: str = Field(description="Message type or role")
    message: str = Field(description="The message content")
    bot_id: Optional[str] = None
    data: Optional[List[Any]] = Field(default_factory=list)
    sender: str = Field(description="Either 'bot' or 'user'")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Optional fields for tool calling support
    tool_calls: Optional[List[ToolCall]] = None
    tool_call_id: Optional[str] = None

