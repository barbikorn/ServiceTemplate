from pydantic import BaseModel
from typing import Optional, Union


class Player(BaseModel):
    exam_id: str
    course_id: str
    name : str

class PlayerCreate(BaseModel):
    exam_id: str
    course_id : str
    name: str


class PlayerUpdate(BaseModel):
    exam_id: Optional[str]
    course_id : Optional[str]
    name: Optional[str]


class PlayerGet(BaseModel):
    id:str
    exam_id: Optional[str]
    course_id : Optional[str]
    name: Optional[str]


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: Union[str, None] = None
