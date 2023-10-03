from pydantic import BaseModel
from typing import Optional, Union, Dict


class UserReport(BaseModel):
    user_id: str
    course_id : str
    score : int

class UserReportCreate(BaseModel):
    user_id: str
    course_id : str
    score: Optional[int] = 0

class UserReportUpdate(BaseModel):
    user_id: Optional[str]
    score: Optional[int]

class UserReportGet(BaseModel):
    user_id: Optional[str]
    course_id : Optional[str]
    score: Optional[int]

