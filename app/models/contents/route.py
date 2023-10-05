
import json
import os
from fastapi import FastAPI, APIRouter, HTTPException, Request, Header, Query
from typing import List, Optional, Dict, Any
from bson import ObjectId
from app.models.contents.content import Content,ContentGet,ContentCreate
from app.database import get_database_atlas
from lib.host_manager import HostDatabaseManager
from pymongo.collection import Collection


router = APIRouter()

collection_name = "contents"
database_manager = HostDatabaseManager(collection_name)
app = FastAPI()

# CRUD
@router.post("/", response_model=ContentGet)
def create_content(
    request: Request,
    content_data: ContentCreate,
    htoken: Optional[str] = Header(None)
):
    host = htoken
    collection = database_manager.get_collection(host)

    content_data_dict = content_data.dict()
    result = collection.insert_one(content_data_dict)

    if result.acknowledged:
        created_content = collection.find_one({"_id": ObjectId(result.inserted_id)})
        return Content(**created_content)
    else:
        raise HTTPException(status_code=500, detail="Failed to create content")

@router.get("/", response_model=List[Dict[str, Any]])
def get_all_contents(
    htoken: Optional[str] = Header(None)
):
    host = htoken
    collection = database_manager.get_collection(host)
    contents = []
    for content in collection.find():
        content_id = str(content.pop('_id'))
        content["id"] = content_id
        contents.append(content)
    return contents

@router.get("/{content_id}", response_model=Content)
def get_content(
    request: Request,
    content_id: str,
    htoken: Optional[str] = Header(None)
):
    host = htoken
    collection = database_manager.get_collection(host)

    content = collection.find_one({"_id": content_id})
    if content:
        return Content(**content)
    else:
        raise HTTPException(status_code=404, detail="Content not found")

@router.get("/filters/", response_model=List[Content])
async def get_content_by_filter(
    request: Request,
    offset: int = 0,
    limit: int = 100,
    htoken: Optional[str] = Header(None)
) -> List[Content]:
    filter_params = await request.json()
    query = {}

    for field, value in filter_params.items():
        query[field] = value
    host = htoken
    collection = database_manager.get_collection(host)
    cursor = collection.find(query).skip(offset).limit(limit)
    contents = []
    async for content in cursor:
        contents.append(Content(id=str(content["_id"]), **content))
    return contents

@router.put("/{content_id}", response_model=Content)
def update_content(
    request: Request,
    content_id: str,
    content_data,
    htoken: Optional[str] = Header(None)
):
    host = htoken
    collection = database_manager.get_collection(host)

    result = collection.update_one({"_id": content_id}, {"$set": content_data.dict()})
    if result.modified_count == 1:
        updated_content = collection.find_one({"_id": content_id})
        return Content(**updated_content)
    else:
        raise HTTPException(status_code=404, detail="Content not found")

@router.delete("/{content_id}")
def delete_content(
    request: Request,
    content_id: str,
    htoken: Optional[str] = Header(None)
):
    host = htoken
    collection = database_manager.get_collection(host)

    result = collection.delete_one({"_id": content_id})
    if result.deleted_count == 1:
        return {"message": "Content deleted successfully"}
    else:
        raise HTTPException(status_code=404, detail="Content not found")



