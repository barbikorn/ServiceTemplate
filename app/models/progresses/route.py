import json
import os
from fastapi import APIRouter, HTTPException, Request, Header, Query
from typing import List, Optional, Dict, Any
from bson import ObjectId
from app.models.progresses.progress import Progress,ProgressGet,ProgressCreate
from app.database import get_database_atlas
from lib.host_manager import HostDatabaseManager

router = APIRouter()

collection_name = "progresses"
database_manager = HostDatabaseManager(collection_name)


@router.post("/", response_model=ProgressGet)
def create_progress(
    request: Request,
    progress_data: ProgressCreate,
    htoken: Optional[str] = Header(None)
):
    host = htoken
    collection = database_manager.get_collection(host)

    progress_data_dict = progress_data.dict()
    result = collection.insert_one(progress_data_dict)

    if result.acknowledged:
        created_progress = collection.find_one({"_id": ObjectId(result.inserted_id)})
        created_progress['id'] = str(created_progress['_id'])  # Add 'id' key and convert ObjectId to string
        return ProgressGet(**created_progress)
    else:
        raise HTTPException(status_code=500, detail="Failed to create progress")

@router.get("/", response_model=List[Dict[str, Any]])
def get_all_progresses(
    htoken: Optional[str] = Header(None)
):
    host = htoken
    collection = database_manager.get_collection(host)
    progresses = []
    for progress in collection.find():
        progress_id = str(progress.pop('_id'))
        progress["id"] = progress_id
        progresses.append(progress)
    return progresses

@router.get("/{progress_id}", response_model=Progress)
def get_progress(
    request: Request,
    progress_id: str,
    htoken: Optional[str] = Header(None)
):
    host = htoken
    collection = database_manager.get_collection(host)

    progress = collection.find_one({"_id": progress_id})
    if progress:
        return Progress(**progress)
    else:
        raise HTTPException(status_code=404, detail="Progress not found")

@router.get("/filters/", response_model=List[Progress])
async def get_progress_by_filter(
    request: Request,
    offset: int = 0,
    limit: int = 100,
    htoken: Optional[str] = Header(None)
) -> List[Progress]:
    filter_params = await request.json()
    query = {}

    for field, value in filter_params.items():
        query[field] = value
    host = htoken
    collection = database_manager.get_collection(host)
    cursor = collection.find(query).skip(offset).limit(limit)
    progresses = []
    async for progress in cursor:
        progresses.append(Progress(id=str(progress["_id"]), **progress))
    return progresses

@router.put("/{progress_id}", response_model=Progress)
def update_progress(
    request: Request,
    progress_id: str,
    progress_data,
    htoken: Optional[str] = Header(None)
):
    host = htoken
    collection = database_manager.get_collection(host)

    result = collection.update_one({"_id": progress_id}, {"$set": progress_data.dict()})
    if result.modified_count == 1:
        updated_progress = collection.find_one({"_id": progress_id})
        return Progress(**updated_progress)
    else:
        raise HTTPException(status_code=404, detail="Progress not found")

@router.delete("/{progress_id}")
def delete_progress(
    request: Request,
    progress_id: str,
    htoken: Optional[str] = Header(None)
):
    host = htoken
    collection = database_manager.get_collection(host)

    result = collection.delete_one({"_id": progress_id})
    if result.deleted_count == 1:
        return {"message": "Progress deleted successfully"}
    else:
        raise HTTPException(status_code=404, detail="Progress not found")



