from pydantic import BaseModel
from typing import Optional

class Product(BaseModel):
    id : Optional[str]
    name: str
    email: str
    password: str
    age: int
    address: Optional[str] = None
    