from pydantic import BaseModel
from typing import Optional, Union


class Document(BaseModel):
    course_id: str
    description : str

class DocumentCreate(BaseModel):
    course_id: Optional[str]
    description: Optional[str] 


class DocumentUpdate(BaseModel):
    course_id: Optional[str]
    description: Optional[str] 

class DocumentGet(BaseModel):
    course_id: Optional[str]
    description: Optional[str] 
    
