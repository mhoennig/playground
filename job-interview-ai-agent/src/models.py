"""
Data models for the Job Interview AI Agent.
"""
from pydantic import BaseModel
from typing import List, Optional

class Evaluation(BaseModel):
    """Model for evaluating chat responses."""
    is_acceptable: bool
    perfection: int
    feedback: str

class QuestionMetadata(BaseModel):
    """Model for question analysis metadata."""
    question: str
    coverage: int
    recruiter: int
    language: str
    category: str

class ChatMessage(BaseModel):
    """Model for chat messages."""
    role: str
    content: str

class ChatHistory(BaseModel):
    """Model for chat history."""
    messages: List[ChatMessage] 