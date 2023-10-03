from pydantic import BaseModel
from typing import Optional, Union


class Player(BaseModel):
    name: str
    schoolname : str
    email: str
    password: str
    role: str
    age: int
    address: Optional[str] 

class PlayerCreate(BaseModel):
    name: str
    schoolname : str
    email: str
    password: str
    role: Optional[str] = "..."
    age: Optional[int] = 0
    address: Optional[str] 


class PlayerUpdate(BaseModel):
    name: Optional[str]
    schoolname : Optional[str]
    email: Optional[str]
    password: Optional[str]
    role: Optional[str]
    age: Optional[int]
    address: Optional[str] 

class PlayerGet(BaseModel):
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
