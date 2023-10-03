from pydantic import BaseModel
from typing import Optional, Union


class Template(BaseModel):
    user_id: str
    course_id : str
    score : int

class TemplateCreate(BaseModel):
    user_id: str
    course_id : str
    score: Optional[int]

class TemplateUpdate(BaseModel):
    user_id: Optional[str]
    score: Optional[int]

class TemplateGet(BaseModel):
    user_id: Optional[str]
    course_id : Optional[str]
    score: Optional[int]

