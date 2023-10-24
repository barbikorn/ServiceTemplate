from pydantic import BaseModel
from typing import Optional, Union


class Course(BaseModel):
    school_id : str
    coursename: str
    description : str


class CourseCreate(BaseModel):
    school_id : Optional[str]
    coursename: Optional[str]
    description: Optional[str]

class CourseUpdate(BaseModel):
    coursename : Optional[str]
    school_id : Optional[str]
    description: Optional[str]

class CourseGet(BaseModel):
    id:Optional[str]
    coursename : Optional[str]
    school_id : Optional[str]
    description: Optional[str]