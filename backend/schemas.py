from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class HeadlineOut(BaseModel):
    id: int
    text: str
    is_manipulative: bool
    category: Optional[str] = None
    difficulty: int

class AnswerIn(BaseModel):
    headline_id: int
    user_answer: bool

class AnswerOut(BaseModel):
    is_correct: bool
    correct_answer: bool
    explanation: Optional[str] = None

class StatsOut(BaseModel):
    total_answers: int
    correct_answers: int
    score: int
    level: int
