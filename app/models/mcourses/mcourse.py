from pydantic import BaseModel
from typing import Optional, Union


class Mcourse(BaseModel):
    school_id : str
    coursename: str


class McourseCreate(BaseModel):
    school_id : Optional[str]
    coursename: Optional[str]
    description: Optional[str]


class McourseUpdate(BaseModel):
    coursename : Optional[str]
    school_id : Optional[str]
    description: Optional[str]

class McourseGet(BaseModel):
    id:str
    coursename : Optional[str]
    school_id : Optional[str]
