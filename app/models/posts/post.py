from pydantic import BaseModel
from typing import Optional, Union,List


class Post(BaseModel):
    post_ids : List[str]
    description: str

class PostCreate(BaseModel):
    post_ids : Optional[List[str]]
    description: Optional[str]

class PostUpdate(BaseModel):
    post_ids : Optional[List[str]]
    description: Optional[str]

class PostGet(BaseModel):
    id: str
    post_ids : Optional[List[str]]
    description: Optional[str]
