from pydantic import BaseModel
from typing import Optional, Union


class Score(BaseModel):
    user_id: str
    course_id : str
    score : int

class ScoreCreate(BaseModel):
    user_id: str
    course_id : str
    score: Optional[int]

class ScoreUpdate(BaseModel):
    user_id: Optional[str]
    score: Optional[int]

class ScoreGet(BaseModel):
    id : str
    user_id: Optional[str]
    course_id : Optional[str]
    score: Optional[int]

