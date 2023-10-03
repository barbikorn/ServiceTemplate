from pydantic import BaseModel
from typing import Optional, Union


class Type(BaseModel):
    user_id: str
    course_id : str
    score : int

class TypeCreate(BaseModel):
    user_id: str
    course_id : str
    score: Optional[int]

class TypeUpdate(BaseModel):
    user_id: Optional[str]
    score: Optional[int]

class TypeGet(BaseModel):
    user_id: Optional[str]
    course_id : Optional[str]
    score: Optional[int]

