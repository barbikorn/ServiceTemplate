
import json
import os
from fastapi import APIRouter, HTTPException, Request, Header, BackgroundTasks, FastAPI
from typing import List, Optional, Dict, Any
from bson import ObjectId
from app.models.schools.school import School,SchoolGet,SchoolCreate,SchoolUpdate
from app.database import get_database_atlas
from lib.host_manager import HostDatabaseManager
from pymongo.collection import Collection
from lib.middleware.queueLog import log_request_and_upload_to_queue

router = APIRouter()

collection_name = "schools"
database_manager = HostDatabaseManager(collection_name)


@router.post("/", response_model=SchoolGet)
async def create_school(
    request: Request,
    school_data: SchoolCreate,
    background_tasks: BackgroundTasks,
    htoken: Optional[str] = Header(None)
):
    
    host = htoken
    collection = await database_manager.get_collection(host)

    school_data_dict = school_data.dict()
    result = collection.insert_one(school_data_dict)

    if result.acknowledged:

        created_school = school_data_dict  # Start with the school data provided
        created_school['id'] = str(result.inserted_id)  # Add 'id' key and convert ObjectId to string
        background_tasks.add_task(
            log_request_and_upload_to_queue,
            request, collection_name, created_school, htoken, background_tasks
        )
        return SchoolGet(**created_school)
    else:
        raise HTTPException(status_code=500, detail="Failed to create school")
@router.get("/", response_model=List[Dict[str, Any]])
def get_all_schools(
    htoken: Optional[str] = Header(None)
):
    host = htoken
    collection = database_manager.get_collection(host)
    schools = []
    for school in collection.find():
        school_id = str(school.pop('_id'))
        school["id"] = school_id
        schools.append(school)
    return schools

@router.get("/{school_id}", response_model=School)
def get_school(
    request: Request,
    school_id: str,
    htoken: Optional[str] = Header(None)
):
    host = htoken
    collection = database_manager.get_collection(host)

    school = collection.find_one({"_id": school_id})
    if school:
        return School(**school)
    else:
        raise HTTPException(status_code=404, detail="School not found")

@router.get("/filters/", response_model=List[School])
async def get_school_by_filter(
    request: Request,
    offset: int = 0,
    limit: int = 100,
    htoken: Optional[str] = Header(None)
) -> List[School]:
    filter_params = await request.json()
    query = {}

    for field, value in filter_params.items():
        query[field] = value
    host = htoken
    collection = database_manager.get_collection(host)
    cursor = collection.find(query).skip(offset).limit(limit)
    schools = []
    async for school in cursor:
        schools.append(School(id=str(school["_id"]), **school))
    return schools

@router.put("/{school_id}", response_model=SchoolGet)
async def update_school(
    request: Request,
    school_id: str,
    school_data: SchoolUpdate,
    background_tasks: BackgroundTasks,
    htoken: Optional[str] = Header(None)
):
    host = htoken
    collection = await database_manager.get_collection(host)
    result = collection.update_one({"_id": ObjectId(school_id)}, {"$set": school_data.dict()})

    if result.modified_count == 1:
        updated_school = collection.find_one({"_id": ObjectId(school_id)})

        # Use background task to log the update
        background_tasks.add_task(
            log_request_and_upload_to_queue,
            request, collection_name, updated_school, htoken
        )

        return SchoolGet(**updated_school)
    else:
        raise HTTPException(status_code=404, detail="Nothing change")

@router.delete("/{school_id}")
def delete_school(
    request: Request,
    school_id: str,
    htoken: Optional[str] = Header(None)
):
    host = htoken
    collection = database_manager.get_collection(host)

    result = collection.delete_one({"_id": school_id})
    if result.deleted_count == 1:
        return {"message": "School deleted successfully"}
    else:
        raise HTTPException(status_code=404, detail="School not found")



