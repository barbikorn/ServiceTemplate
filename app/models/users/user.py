from pydantic import BaseModel
from typing import Optional, Union


class User(BaseModel):
    name: str
    username : str
    email: str
    password: str
    role: str
    age: int
    address: Optional[str] 

class UserCreate(BaseModel):
    name: str
    username : str
    email: str
    password: str
    role: Optional[str] = "users"
    age: Optional[int] = 0
    address: Optional[str] 


class UserUpdate(BaseModel):
    name: Optional[str]
    username : Optional[str]
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
