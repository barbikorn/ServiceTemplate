from pydantic import BaseModel
from typing import Optional, Union


class Form(BaseModel):
    course_id: str
    description : str

class FormCreate(BaseModel):
    course_id: Optional[str]
    description: Optional[str] 


class FormUpdate(BaseModel):
    course_id: Optional[str]
    description: Optional[str] 

class FormGet(BaseModel):
    course_id: Optional[str]
    description: Optional[str] 
    
