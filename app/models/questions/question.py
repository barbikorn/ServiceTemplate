from pydantic import BaseModel
from typing import Optional, Union


class Question(BaseModel):
    name: str
    question : str
    exam_id: str

class QuestionCreate(BaseModel):
    name: Optional[str] 
    question : Optional[str] 
    exam_id: Optional[str]

class QuestionUpdate(BaseModel):
    name: Optional[str] 
    question : Optional[str] 
    exam_id: Optional[str]

class QuestionGet(BaseModel):
    id : str
    name: Optional[str] 
    question : Optional[str] 
    exam_id: Optional[str]
