import json
import os
from fastapi import APIRouter, HTTPException, Request, Header, Query
from typing import List, Optional, Dict, Any
from bson import ObjectId
from app.models.posts.post import Post,PostGet,PostCreate
from app.database import get_database_atlas
from lib.host_manager import HostDatabaseManager

router = APIRouter()

collection_name = "exams"
database_manager = HostDatabaseManager(collection_name)


# Assuming you have a database_manager instance



@router.post("/", response_model=PostGet)
def create_post(
    request: Request,
    post_data: PostCreate,
    htoken: Optional[str] = Header(None)
):
    host = htoken
    collection = database_manager.get_collection(host)

    post_data_dict = post_data.dict()
    result = collection.insert_one(post_data_dict)

    if result.acknowledged:
        created_post = collection.find_one({"_id": ObjectId(result.inserted_id)})
        created_post['id'] = str(created_post['_id'])  # Add 'id' key and convert ObjectId to string
        return PostGet(**created_post)
    else:
        raise HTTPException(status_code=500, detail="Failed to create post")

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

@router.get("/{exam_id}", response_model=Post)
def get_exam(
    request: Request,
    exam_id: str,
    htoken: Optional[str] = Header(None)
):
    host = htoken
    collection = database_manager.get_collection(host)
    exam = collection.find_one({"_id": exam_id})
    if exam:
        return Post(**exam)
    else:
        raise HTTPException(status_code=404, detail="Post not found")

@router.get("/filters/", response_model=List[Post])
async def get_exam_by_filter(
    request: Request,
    offset: int = 0,
    limit: int = 100,
    htoken: Optional[str] = Header(None)
) -> List[Post]:
    filter_params = await request.json()
    query = {}

    for field, value in filter_params.items():
        query[field] = value
    host = htoken
    collection = database_manager.get_collection(host)
    cursor = collection.find(query).skip(offset).limit(limit)
    exams = []
    async for exam in cursor:
        exams.append(Post(id=str(exam["_id"]), **exam))
    return exams

@router.put("/{exam_id}", response_model=Post)
def update_exam(
    request: Request,
    exam_id: str,
    exam_data,
    htoken: Optional[str] = Header(None)
):
    host = htoken
    collection = database_manager.get_collection(host)

    result = collection.update_one({"_id": exam_id}, {"$set": exam_data.dict()})
    if result.modified_count == 1:
        updated_exam = collection.find_one({"_id": exam_id})
        return Post(**updated_exam)
    else:
        raise HTTPException(status_code=404, detail="Post not found")

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
        return {"message": "Post deleted successfully"}
    else:
        raise HTTPException(status_code=404, detail="Post not found")



