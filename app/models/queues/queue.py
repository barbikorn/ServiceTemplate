from pydantic import BaseModel
from typing import Optional, Union, Dict, Any


class Queue(BaseModel):
    name: str
    collection: str
    data : Optional[Dict[str, Any]]
    e_id : str

class QueueCreate(BaseModel):
    name: str
    collection: str
    data : Optional[Dict[str, Any]]
    e_id : str

class QueueUpdate(BaseModel):
    name: Optional[str]
    collection: Optional[str]
    data : Optional[Dict[str, Any]]
    e_id : Optional[str]

class QueueGet(BaseModel):
    name: Optional[str]
    collection: Optional[str]
    data : Optional[Dict[str, Any]]
    e_id : Optional[str]


