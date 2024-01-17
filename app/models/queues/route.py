
import json
import os
from fastapi import APIRouter, HTTPException, Request, Header, BackgroundTasks
from typing import List, Optional, Dict, Any
from bson import ObjectId
from app.models.queues.queue import Queue,QueueGet,QueueCreate
from app.database import get_database_atlas
from lib.host_manager import HostDatabaseManager
from lib.middleware.queueLog import log_request_and_upload_to_queue


router = APIRouter()

collection_name = "queues"
database_manager = HostDatabaseManager(collection_name)


@router.post("/", response_model=QueueGet)
async def create_queue(
    request: Request,
    queue_data: QueueCreate,
    background_tasks: BackgroundTasks,
    htoken: Optional[str] = Header(None)
):
    
    host = htoken
    collection = await database_manager.get_collection(host)

    queue_data_dict = queue_data.dict()
    result = collection.insert_one(queue_data_dict)

    if result.acknowledged:

        created_queue = queue_data_dict  # Start with the queue data provided
        created_queue['id'] = str(result.inserted_id)  # Add 'id' key and convert ObjectId to string
        background_tasks.add_task(
            log_request_and_upload_to_queue,
            request, collection_name, created_queue, htoken, background_tasks
        )
        return QueueGet(**created_queue)
    else:
        raise HTTPException(status_code=500, detail="Failed to create queue")

@router.get("/", response_model=List[Dict[str, Any]])
def get_all_queues(
    htoken: Optional[str] = Header(None)
):
    host = htoken
    collection = database_manager.get_collection(host)
    queues = []
    for queue in collection.find():
        queue_id = str(queue.pop('_id'))
        queue["id"] = queue_id
        queues.append(queue)
    return queues

@router.get("/{queue_id}", response_model=Queue)
def get_queue(
    request: Request,
    queue_id: str,
    htoken: Optional[str] = Header(None)
):
    host = htoken
    collection = database_manager.get_collection(host)

    queue = collection.find_one({"_id": queue_id})
    if queue:
        return Queue(**queue)
    else:
        raise HTTPException(status_code=404, detail="Queue not found")

@router.get("/filters/", response_model=List[Queue])
async def get_queue_by_filter(
    request: Request,
    offset: int = 0,
    limit: int = 100,
    htoken: Optional[str] = Header(None)
) -> List[Queue]:
    filter_params = await request.json()
    query = {}

    for field, value in filter_params.items():
        query[field] = value
    host = htoken
    collection = database_manager.get_collection(host)
    cursor = collection.find(query).skip(offset).limit(limit)
    queues = []
    async for queue in cursor:
        queues.append(Queue(id=str(queue["_id"]), **queue))
    return queues

@router.put("/{queue_id}", response_model=Queue)
def update_queue(
    request: Request,
    queue_id: str,
    queue_data,
    htoken: Optional[str] = Header(None)
):
    host = htoken
    collection = database_manager.get_collection(host)

    result = collection.update_one({"_id": queue_id}, {"$set": queue_data.dict()})
    if result.modified_count == 1:
        updated_queue = collection.find_one({"_id": queue_id})
        return Queue(**updated_queue)
    else:
        raise HTTPException(status_code=404, detail="Queue not found")

@router.delete("/{queue_id}")
def delete_queue(
    request: Request,
    queue_id: str,
    htoken: Optional[str] = Header(None)
):
    host = htoken
    collection = database_manager.get_collection(host)

    result = collection.delete_one({"_id": queue_id})
    if result.deleted_count == 1:
        return {"message": "Queue deleted successfully"}
    else:
        raise HTTPException(status_code=404, detail="Queue not found")



