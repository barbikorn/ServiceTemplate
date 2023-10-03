from pydantic import BaseModel
from typing import Optional, Union


class Website(BaseModel):
    user_id: str
    course_id : str
    score : int

class WebsiteCreate(BaseModel):
    user_id: str
    course_id : str
    score: Optional[int]

class WebsiteUpdate(BaseModel):
    user_id: Optional[str]
    score: Optional[int]

class WebsiteGet(BaseModel):
    user_id: Optional[str]
    course_id : Optional[str]
    score: Optional[int]

