from pydantic import BaseModel
from typing import Optional, Union


class Progress(BaseModel):
    user_id: str
    course_id:str
    player_id : str
    time : int

class ProgressCreate(BaseModel):
    user_id: Optional[str]
    course_id: Optional[str]
    player_id : Optional[str]
    time : int


class ProgressUpdate(BaseModel):
    user_id: Optional[str]
    course_id: Optional[str]
    player_id : Optional[str]
    time : Optional[int]

class ProgressGet(BaseModel):
    id : str
    user_id: Optional[str]
    course_id: Optional[str]
    player_id : Optional[str]
    time : Optional[int]

