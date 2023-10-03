from pydantic import BaseModel
from typing import Optional, Union


class School(BaseModel):
    schoolname : str
    tel: str
    address: Optional[str] 

class SchoolCreate(BaseModel):
    schoolname : str
    tel: Optional[str]
    address: Optional[str] 


class SchoolUpdate(BaseModel):
    schoolname : Optional[str]
    tel: Optional[str]
    address: Optional[str] 

class SchoolGet(BaseModel):
    schoolname : Optional[str]
    tel: Optional[str]
    address: Optional[str] 
