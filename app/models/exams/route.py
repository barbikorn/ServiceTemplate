import json
import os
from fastapi import APIRouter, HTTPException, Request, Header, BackgroundTasks
from typing import List, Optional, Dict, Any
from bson import ObjectId
from app.models.exams.exam import Exam,ExamGet,ExamCreate,ExamUpdate
from app.database import get_database_atlas
from lib.host_manager import HostDatabaseManager
from lib.middleware.queueLog import log_request_and_upload_to_queue

router = APIRouter()

collection_name = "exams"
database_manager = HostDatabaseManager(collection_name)


@router.post("/", response_model=ExamGet)
async def create_exam(
    request: Request,
    exam_data: ExamCreate,
    background_tasks: BackgroundTasks,
    htoken: Optional[str] = Header(None)
):
    
    host = htoken
    collection = await database_manager.get_collection(host)

    exam_data_dict = exam_data.dict()
    result = collection.insert_one(exam_data_dict)

    if result.acknowledged:

        created_exam = exam_data_dict  # Start with the exam data provided
        created_exam['id'] = str(result.inserted_id)  # Add 'id' key and convert ObjectId to string
        background_tasks.add_task(
            log_request_and_upload_to_queue,
            request, collection_name, created_exam, htoken, background_tasks
        )
        return ExamGet(**created_exam)
    else:
        raise HTTPException(status_code=500, detail="Failed to create exam")


@router.get("/", response_model=List[Dict[str, Any]])
def get_all_exams(
    htoken: Optional[str] = Header(None)
):
    host = htoken
    collection = database_manager.get_collection(host)
    exams = []
    for exam in collection.find():
        exam_id = str(exam.pop('_id'))
        exam["id"] = exam_id
        exams.append(exam)
    return exams

@router.get("/{exam_id}", response_model=Exam)
def get_exam(
    request: Request,
    exam_id: str,
    htoken: Optional[str] = Header(None)
):
    host = htoken
    collection = database_manager.get_collection(host)

    exam = collection.find_one({"_id": exam_id})
    if exam:
        return Exam(**exam)
    else:
        raise HTTPException(status_code=404, detail="Exam not found")

@router.get("/filters/", response_model=List[Exam])
async def get_exam_by_filter(
    request: Request,
    offset: int = 0,
    limit: int = 100,
    htoken: Optional[str] = Header(None)
) -> List[Exam]:
    filter_params = await request.json()
    query = {}

    for field, value in filter_params.items():
        query[field] = value
    host = htoken
    collection = database_manager.get_collection(host)
    cursor = collection.find(query).skip(offset).limit(limit)
    exams = []
    async for exam in cursor:
        exams.append(Exam(id=str(exam["_id"]), **exam))
    return exams
@router.put("/{exam_id}", response_model=ExamGet)
async def update_exam(
    request: Request,
    exam_id: str,
    exam_data: ExamUpdate,
    background_tasks: BackgroundTasks,
    htoken: Optional[str] = Header(None)
):
    host = htoken
    collection = await database_manager.get_collection(host)
    result = collection.update_one({"_id": ObjectId(exam_id)}, {"$set": exam_data.dict()})

    if result.modified_count == 1:
        updated_exam = collection.find_one({"_id": ObjectId(exam_id)})

        # Use background task to log the update
        background_tasks.add_task(
            log_request_and_upload_to_queue,
            request, collection_name, updated_exam, htoken
        )

        return ExamGet(**updated_exam)
    else:
        raise HTTPException(status_code=404, detail="Nothing change")

@router.delete("/{exam_id}")
def delete_exam(
    request: Request,
    exam_id: str,
    htoken: Optional[str] = Header(None)
):
    host = htoken
    collection = database_manager.get_collection(host)

    result = collection.delete_one({"_id": exam_id})
    if result.deleted_count == 1:
        return {"message": "Exam deleted successfully"}
    else:
        raise HTTPException(status_code=404, detail="Exam not found")



