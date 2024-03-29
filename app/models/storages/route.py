import json
import os
from fastapi import FastAPI,APIRouter, HTTPException, Request, Header, BackgroundTasks
from typing import List, Optional, Dict, Any
from bson import ObjectId
from app.models.storages.storage import Storage,StorageGet,StorageCreate,StorageUpdate
from app.database import get_database_atlas
from lib.host_manager import HostDatabaseManager
from pymongo.collection import Collection
from lib.middleware.queueLog import log_request_and_upload_to_queue

router = APIRouter()

collection_name = "storages"
database_manager = HostDatabaseManager(collection_name)

@router.post("/", response_model=StorageGet)
async def create_storage(
    request: Request,
    storage_data: StorageCreate,
    background_tasks: BackgroundTasks,
    htoken: Optional[str] = Header(None)
):
    
    host = htoken
    collection = await database_manager.get_collection(host)

    storage_data_dict = storage_data.dict()
    result = collection.insert_one(storage_data_dict)

    if result.acknowledged:

        created_storage = storage_data_dict  # Start with the storage data provided
        created_storage['id'] = str(result.inserted_id)  # Add 'id' key and convert ObjectId to string
        background_tasks.add_task(
            log_request_and_upload_to_queue,
            request, collection_name, created_storage, htoken, background_tasks
        )
        return StorageGet(**created_storage)
    else:
        raise HTTPException(status_code=500, detail="Failed to create storage")

@router.get("/", response_model=List[Dict[str, Any]])
def get_all_storages(
    htoken: Optional[str] = Header(None)
):
    host = htoken
    collection = database_manager.get_collection(host)
    storages = []
    for storage in collection.find():
        storage_id = str(storage.pop('_id'))
        storage["id"] = storage_id
        storages.append(storage)
    return storages

@router.get("/{storage_id}", response_model=StorageGet)
def get_storage(
    request: Request,
    storage_id: str,
    htoken: Optional[str] = Header(None)
):
    host = htoken
    collection = database_manager.get_collection(host)

    storage = collection.find_one({"_id": storage_id})
    if storage:
        return Storage(**storage)
    else:
        raise HTTPException(status_code=404, detail="Storage not found")

@router.get("/filters/", response_model=List[Storage])
async def get_storage_by_filter(
    request: Request,
    offset: int = 0,
    limit: int = 100,
    htoken: Optional[str] = Header(None)
) -> List[Storage]:
    filter_params = await request.json()
    query = {}

    for field, value in filter_params.items():
        query[field] = value
    host = htoken
    collection = database_manager.get_collection(host)
    cursor = collection.find(query).skip(offset).limit(limit)
    storages = []
    async for storage in cursor:
        storages.append(Storage(id=str(storage["_id"]), **storage))
    return storages

@router.put("/{storage_id}", response_model=StorageGet)
async def update_storage(
    request: Request,
    storage_id: str,
    storage_data: StorageUpdate,
    background_tasks: BackgroundTasks,
    htoken: Optional[str] = Header(None)
):
    host = htoken
    collection = await database_manager.get_collection(host)
    result = collection.update_one({"_id": ObjectId(storage_id)}, {"$set": storage_data.dict()})

    if result.modified_count == 1:
        updated_storage = collection.find_one({"_id": ObjectId(storage_id)})

        # Use background task to log the update
        background_tasks.add_task(
            log_request_and_upload_to_queue,
            request, collection_name, updated_storage, htoken
        )

        return StorageGet(**updated_storage)
    else:
        raise HTTPException(status_code=404, detail="Nothing change")

@router.delete("/{storage_id}")
def delete_storage(
    request: Request,
    storage_id: str,
    htoken: Optional[str] = Header(None)
):
    host = htoken
    collection = database_manager.get_collection(host)

    result = collection.delete_one({"_id": storage_id})
    if result.deleted_count == 1:
        return {"message": "Storage deleted successfully"}
    else:
        raise HTTPException(status_code=404, detail="Storage not found")



