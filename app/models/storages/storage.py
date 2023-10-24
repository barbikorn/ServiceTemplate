from pydantic import BaseModel
from typing import Optional, Union


class Storage(BaseModel):
    user_id: str
    course_id : str
    score : int

class StorageCreate(BaseModel):
    user_id: str
    course_id : str
    score: Optional[int]

class StorageUpdate(BaseModel):
    user_id: Optional[str]
    score: Optional[int]

class StorageGet(BaseModel):
    id : str
    user_id: Optional[str]
    course_id : Optional[str]
    score: Optional[int]

