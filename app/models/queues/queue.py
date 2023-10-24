from pydantic import BaseModel
from typing import Optional, Union


class Queue(BaseModel):
    name: str
    schoolname : str
    email: str
    password: str
    role: str
    age: int
    address: Optional[str] 

class QueueCreate(BaseModel):
    name: str
    schoolname : str
    email: str
    password: str
    role: Optional[str] = "..."
    age: Optional[int] = 0
    address: Optional[str] 


class QueueUpdate(BaseModel):
    name: Optional[str]
    schoolname : Optional[str]
    email: Optional[str]
    password: Optional[str]
    role: Optional[str]
    age: Optional[int]
    address: Optional[str] 

class QueueGet(BaseModel):
    id : str
    name: Optional[str]
    schoolname : Optional[str]
    email: Optional[str]
    password: Optional[str]
    role: Optional[str]
    age: Optional[int]
    address: Optional[str] 


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: Union[str, None] = None
