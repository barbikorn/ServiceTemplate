from pydantic import BaseModel
from typing import Optional, Union


class Enroll(BaseModel):
    course_id: str
    description : str

class EnrollCreate(BaseModel):
    course_id: Optional[str]
    description: Optional[str] 


class EnrollUpdate(BaseModel):
    course_id: Optional[str]
    description: Optional[str] 

class EnrollGet(BaseModel):
    course_id: Optional[str]
    description: Optional[str] 
    
