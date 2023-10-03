from pydantic import BaseModel
from typing import Optional, Union


class Bill(BaseModel):
    name: str
    user_id : str
    course_id: str

class BillCreate(BaseModel):
    name: Optional[str]
    user_id: Optional[str]
    course_id: Optional[str] 


class BillUpdate(BaseModel):
    name: Optional[str]
    user_id: Optional[str]
    course_id: Optional[str] 

class BillGet(BaseModel):
    name: Optional[str]
    user_id: Optional[str]
    course_id: Optional[str] 

