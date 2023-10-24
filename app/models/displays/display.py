from pydantic import BaseModel
from typing import Optional, Union


class Display(BaseModel):
    school_id : str
    coursename: str


class DisplayCreate(BaseModel):
    school_id : Optional[str]
    coursename: Optional[str]
    description: Optional[str]


class DisplayUpdate(BaseModel):
    coursename : Optional[str]
    school_id : Optional[str]
    description: Optional[str]

class DisplayGet(BaseModel):
    school_id : str
    description: Optional[str]
    coursename : Optional[str]
    school_id : Optional[str]
