
import json
import os
from fastapi import FastAPI, APIRouter, HTTPException, Request, Header, BackgroundTasks
from typing import List, Optional, Dict, Any
from bson import ObjectId
from app.models.displays.display import Display,DisplayGet,DisplayCreate,DisplayUpdate
from app.database import get_database_atlas
from lib.host_manager import HostDatabaseManager
from pymongo.collection import Collection
from lib.middleware.queueLog import log_request_and_upload_to_queue

router = APIRouter()

collection_name = "displays"
database_manager = HostDatabaseManager(collection_name)
app = FastAPI()

# CRUD@router.post("/", response_model=DisplayGet)
async def create_display(
    request: Request,
    display_data: DisplayCreate,
    background_tasks: BackgroundTasks,
    htoken: Optional[str] = Header(None)
):
    
    host = htoken
    collection = await database_manager.get_collection(host)

    display_data_dict = display_data.dict()
    result = collection.insert_one(display_data_dict)

    if result.acknowledged:

        created_display = display_data_dict  # Start with the display data provided
        created_display['id'] = str(result.inserted_id)  # Add 'id' key and convert ObjectId to string
        background_tasks.add_task(
            log_request_and_upload_to_queue,
            request, collection_name, created_display, htoken, background_tasks
        )
        return DisplayGet(**created_display)
    else:
        raise HTTPException(status_code=500, detail="Failed to create display")


@router.get("/", response_model=List[Dict[str, Any]])
def get_all_displays(
    htoken: Optional[str] = Header(None)
):
    host = htoken
    collection = database_manager.get_collection(host)
    displays = []
    for display in collection.find():
        display_id = str(display.pop('_id'))
        display["id"] = display_id
        displays.append(display)
    return displays

@router.get("/{display_id}", response_model=Display)
def get_display(
    request: Request,
    display_id: str,
    htoken: Optional[str] = Header(None)
):
    host = htoken
    collection = database_manager.get_collection(host)

    display = collection.find_one({"_id": display_id})
    if display:
        return Display(**display)
    else:
        raise HTTPException(status_code=404, detail="Display not found")

@router.get("/filters/", response_model=List[Display])
async def get_display_by_filter(
    request: Request,
    offset: int = 0,
    limit: int = 100,
    htoken: Optional[str] = Header(None)
) -> List[Display]:
    filter_params = await request.json()
    query = {}

    for field, value in filter_params.items():
        query[field] = value
    host = htoken
    collection = database_manager.get_collection(host)
    cursor = collection.find(query).skip(offset).limit(limit)
    displays = []
    async for display in cursor:
        displays.append(Display(id=str(display["_id"]), **display))
    return displays
@router.put("/{display_id}", response_model=DisplayGet)
async def update_display(
    request: Request,
    display_id: str,
    display_data: DisplayUpdate,
    background_tasks: BackgroundTasks,
    htoken: Optional[str] = Header(None)
):
    host = htoken
    collection = await database_manager.get_collection(host)
    result = collection.update_one({"_id": ObjectId(display_id)}, {"$set": display_data.dict()})

    if result.modified_count == 1:
        updated_display = collection.find_one({"_id": ObjectId(display_id)})

        # Use background task to log the update
        background_tasks.add_task(
            log_request_and_upload_to_queue,
            request, collection_name, updated_display, htoken
        )

        return DisplayGet(**updated_display)
    else:
        raise HTTPException(status_code=404, detail="Nothing change")

@router.delete("/{display_id}")
def delete_display(
    request: Request,
    display_id: str,
    htoken: Optional[str] = Header(None)
):
    host = htoken
    collection = database_manager.get_collection(host)

    result = collection.delete_one({"_id": display_id})
    if result.deleted_count == 1:
        return {"message": "Display deleted successfully"}
    else:
        raise HTTPException(status_code=404, detail="Display not found")



