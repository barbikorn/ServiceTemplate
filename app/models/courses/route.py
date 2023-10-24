
import json
import os
from fastapi import FastAPI, APIRouter, HTTPException, Request, Header, Query
from typing import List, Optional, Dict, Any
from bson import ObjectId
from app.models.courses.course import Course,CourseGet,CourseCreate
from app.database import get_database_atlas
from lib.host_manager import HostDatabaseManager
from pymongo.collection import Collection

router = APIRouter()

collection_name = "courses"
database_manager = HostDatabaseManager(collection_name)
app = FastAPI()

# CRUD
@router.post("/", response_model=CourseGet)
def create_course(
    request: Request,
    course_data: CourseCreate,
    htoken: Optional[str] = Header(None)
):
    host = htoken
    collection = database_manager.get_collection(host)

    course_data_dict = course_data.dict()
    result = collection.insert_one(course_data_dict)

    if result.acknowledged:
        created_course = collection.find_one({"_id": ObjectId(result.inserted_id)})
        created_course['id'] = str(created_course['_id'])  # Add 'id' key and convert ObjectId to string
        return CourseGet(**created_course)
    else:
        raise HTTPException(status_code=500, detail="Failed to create course")

@router.get("/", response_model=List[Dict[str, Any]])
def get_all_courses(
    htoken: Optional[str] = Header(None)
):
    host = htoken
    collection = database_manager.get_collection(host)
    courses = []
    for course in collection.find():
        course_id = str(course.pop('_id'))
        course["id"] = course_id
        courses.append(course)
    return courses

@router.get("/{course_id}", response_model=Course)
def get_course(
    request: Request,
    course_id: str,
    htoken: Optional[str] = Header(None)
):
    host = htoken
    collection = database_manager.get_collection(host)

    course = collection.find_one({"_id": course_id})
    if course:
        return Course(**course)
    else:
        raise HTTPException(status_code=404, detail="Course not found")

@router.get("/filters/", response_model=List[Course])
async def get_course_by_filter(
    request: Request,
    offset: int = 0,
    limit: int = 100,
    htoken: Optional[str] = Header(None)
) -> List[Course]:
    filter_params = await request.json()
    query = {}

    for field, value in filter_params.items():
        query[field] = value
    host = htoken
    collection = database_manager.get_collection(host)
    cursor = collection.find(query).skip(offset).limit(limit)
    courses = []
    async for course in cursor:
        courses.append(Course(id=str(course["_id"]), **course))
    return courses

@router.put("/{course_id}", response_model=Course)
def update_course(
    request: Request,
    course_id: str,
    course_data,
    htoken: Optional[str] = Header(None)
):
    host = htoken
    collection = database_manager.get_collection(host)

    result = collection.update_one({"_id": course_id}, {"$set": course_data.dict()})
    if result.modified_count == 1:
        updated_course = collection.find_one({"_id": course_id})
        return Course(**updated_course)
    else:
        raise HTTPException(status_code=404, detail="Course not found")

@router.delete("/{course_id}")
def delete_course(
    request: Request,
    course_id: str,
    htoken: Optional[str] = Header(None)
):
    host = htoken
    collection = database_manager.get_collection(host)

    result = collection.delete_one({"_id": course_id})
    if result.deleted_count == 1:
        return {"message": "Course deleted successfully"}
    else:
        raise HTTPException(status_code=404, detail="Course not found")



