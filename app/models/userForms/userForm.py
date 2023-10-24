from pydantic import BaseModel
from typing import Optional, Union


class UserForm(BaseModel):
    user_id: str
    course_id : str
    score : int

class UserFormCreate(BaseModel):
    user_id: str
    course_id : str
    score: Optional[int]

class UserFormUpdate(BaseModel):
    user_id: Optional[str]
    score: Optional[int]

class UserFormGet(BaseModel):
    id : str
    user_id: Optional[str]
    course_id : Optional[str]
    score: Optional[int]

