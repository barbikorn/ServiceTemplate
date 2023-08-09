from pydantic import BaseModel
from typing import Optional

class Host(BaseModel):
    token: str
    name: str
    databasename: str