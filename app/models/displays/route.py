
import json
import os
from fastapi import FastAPI, APIRouter, HTTPException, Request, Header, Query
from typing import List, Optional, Dict, Any
from bson import ObjectId
from app.models.displays.display import Display,DisplayGet,DisplayCreate
from app.database import get_database_atlas
from lib.host_manager import HostDatabaseManager
from pymongo.collection import Collection

router = APIRouter()

collection_name = "displays"
database_manager = HostDatabaseManager(collection_name)
app = FastAPI()

# CRUD
@router.post("/", response_model=DisplayGet)
def create_display(
    request: Request,
    display_data: DisplayCreate,
    htoken: Optional[str] = Header(None)
):
    host = htoken
    collection = database_manager.get_collection(host)

    display_data_dict = display_data.dict()
    result = collection.insert_one(display_data_dict)

    if result.acknowledged:
        created_display = collection.find_one({"_id": ObjectId(result.inserted_id)})
        created_display['id'] = str(created_display['_id'])  # Add 'id' key and convert ObjectId to string
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

@router.put("/{display_id}", response_model=Display)
def update_display(
    request: Request,
    display_id: str,
    display_data,
    htoken: Optional[str] = Header(None)
):
    host = htoken
    collection = database_manager.get_collection(host)

    result = collection.update_one({"_id": display_id}, {"$set": display_data.dict()})
    if result.modified_count == 1:
        updated_display = collection.find_one({"_id": display_id})
        return Display(**updated_display)
    else:
        raise HTTPException(status_code=404, detail="Display not found")

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



