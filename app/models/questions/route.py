import json
import os
from fastapi import APIRouter, HTTPException, Request, Header, BackgroundTasks
from typing import List, Optional, Dict, Any
from bson import ObjectId
from app.models.questions.question import Question,QuestionGet,QuestionCreate,QuestionUpdate
from app.database import get_database_atlas
from lib.host_manager import HostDatabaseManager
from lib.middleware.queueLog import log_request_and_upload_to_queue

router = APIRouter()

collection_name = "questions"
database_manager = HostDatabaseManager(collection_name)

# Assuming you have a database_manager instance


@router.post("/", response_model=QuestionGet)
async def create_question(
    request: Request,
    question_data: QuestionCreate,
    background_tasks: BackgroundTasks,
    htoken: Optional[str] = Header(None)
):
    
    host = htoken
    collection = await database_manager.get_collection(host)

    question_data_dict = question_data.dict()
    result = collection.insert_one(question_data_dict)

    if result.acknowledged:

        created_question = question_data_dict  # Start with the question data provided
        created_question['id'] = str(result.inserted_id)  # Add 'id' key and convert ObjectId to string
        background_tasks.add_task(
            log_request_and_upload_to_queue,
            request, collection_name, created_question, htoken, background_tasks
        )
        return QuestionGet(**created_question)
    else:
        raise HTTPException(status_code=500, detail="Failed to create question")

@router.get("/", response_model=List[Dict[str, Any]])
def get_all_questions(
    htoken: Optional[str] = Header(None)
):
    host = htoken
    collection = database_manager.get_collection(host)
    questions = []
    for question in collection.find():
        question_id = str(question.pop('_id'))
        question["id"] = question_id
        questions.append(question)
    return questions

@router.get("/{question_id}", response_model=QuestionGet)
def get_question(
    request: Request,
    question_id: str,
    htoken: Optional[str] = Header(None)
):
    host = htoken
    collection = database_manager.get_collection(host)

    question = collection.find_one({"_id": question_id})
    if question:
        return Question(**question)
    else:
        raise HTTPException(status_code=404, detail="Question not found")

@router.get("/filters/", response_model=List[Question])
async def get_question_by_filter(
    request: Request,
    offset: int = 0,
    limit: int = 100,
    htoken: Optional[str] = Header(None)
) -> List[Question]:
    filter_params = await request.json()
    query = {}

    for field, value in filter_params.items():
        query[field] = value
    host = htoken
    collection = database_manager.get_collection(host)
    cursor = collection.find(query).skip(offset).limit(limit)
    questions = []
    async for question in cursor:
        questions.append(Question(id=str(question["_id"]), **question))
    return questions
@router.put("/{question_id}", response_model=QuestionGet)
async def update_question(
    request: Request,
    question_id: str,
    question_data: QuestionUpdate,
    background_tasks: BackgroundTasks,
    htoken: Optional[str] = Header(None)
):
    host = htoken
    collection = await database_manager.get_collection(host)
    result = collection.update_one({"_id": ObjectId(question_id)}, {"$set": question_data.dict()})

    if result.modified_count == 1:
        updated_question = collection.find_one({"_id": ObjectId(question_id)})

        # Use background task to log the update
        background_tasks.add_task(
            log_request_and_upload_to_queue,
            request, collection_name, updated_question, htoken
        )

        return QuestionGet(**updated_question)
    else:
        raise HTTPException(status_code=404, detail="Nothing change")

@router.delete("/{question_id}")
def delete_question(
    request: Request,
    question_id: str,
    htoken: Optional[str] = Header(None)
):
    host = htoken
    collection = database_manager.get_collection(host)
    
    result = collection.delete_one({"_id": question_id})
    if result.deleted_count == 1:
        return {"message": "Question deleted successfully"}
    else:
        raise HTTPException(status_code=404, detail="Question not found")



