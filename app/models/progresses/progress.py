from pydantic import BaseModel
from typing import Optional, Union


class Progress(BaseModel):
    user_id: str
    course_id:str
    player_id : str

class ProgressCreate(BaseModel):
    user_id: Optional[str]
    course_id: Optional[str]
    player_id : Optional[str]


class ProgressUpdate(BaseModel):
    user_id: Optional[str]
    course_id: Optional[str]
    player_id : Optional[str]

class ProgressGet(BaseModel):
    user_id: Optional[str]
    course_id: Optional[str]
    player_id : Optional[str]

