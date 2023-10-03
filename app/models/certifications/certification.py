from pydantic import BaseModel
from typing import Optional, Union


class Certification(BaseModel):
    name: str
    user_id : str
    course_id: str

class CertificationCreate(BaseModel):
    name: Optional[str]
    user_id:Optional[str] 
    course_id: Optional[str] 


class CertificationUpdate(BaseModel):
    name: Optional[str]
    user_id:Optional[str] 
    course_id: Optional[str] 

class CertificationGet(BaseModel):
    name: Optional[str] 
    user_id:Optional[str] 
    course_id: Optional[str] 

