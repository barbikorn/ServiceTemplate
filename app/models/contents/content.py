from pydantic import BaseModel
from typing import Optional, Union, Any


class Content(BaseModel):
    school_id : str
    coursename: str


class ContentCreate(BaseModel):
    school_id : Optional[str]
    coursename: str
    description: Optional[str]


class ContentUpdate(BaseModel):
    coursename : Optional[str]
    school_id : Optional[str]
    description: Optional[Any]

class ContentGet(BaseModel):
    id:Optional[str]
    coursename : Optional[str]
    school_id : Optional[str]
    description: Optional[Any]
