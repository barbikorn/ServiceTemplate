from pydantic import BaseModel
from typing import Optional, Union


class Transaction(BaseModel):
    user_id: str
    course_id : str
    score : int

class TransactionCreate(BaseModel):
    user_id: str
    course_id : str
    score: Optional[int]

class TransactionUpdate(BaseModel):
    user_id: Optional[str]
    score: Optional[int]

class TransactionGet(BaseModel):
    user_id: Optional[str]
    course_id : Optional[str]
    score: Optional[int]

