from pydantic import BaseModel
from typing import Optional, Union


class Exam(BaseModel):
    exam_name: str
    course_id: str

class ExamCreate(BaseModel):
    exam_name: str
    course_id: str

class ExamUpdate(BaseModel):
    exam_name: Optional[str]
    course_id : Optional[str]

class ExamGet(BaseModel):
    exam_name: Optional[str]
    course_id : Optional[str]
