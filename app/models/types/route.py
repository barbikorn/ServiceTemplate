import json
import os
from fastapi import FastAPI,APIRouter, HTTPException, Request, Header, Query
from typing import List, Optional, Dict, Any
from bson import ObjectId
from app.models.types.type import Type,TypeGet,TypeCreate
from app.database import get_database_atlas
from lib.host_manager import HostDatabaseManager
from pymongo.collection import Collection

router = APIRouter()

collection_name = "types"
database_manager = HostDatabaseManager(collection_name)


@router.post("/", response_model=TypeGet)
def create_type(
    request: Request,
    type_data: TypeCreate,
    htoken: Optional[str] = Header(None)
):
    host = htoken
    collection = database_manager.get_collection(host)

    type_data_dict = type_data.dict()
    result = collection.insert_one(type_data_dict)

    if result.acknowledged:
        created_type = collection.find_one({"_id": ObjectId(result.inserted_id)})
        created_type['id'] = str(created_type['_id'])  # Add 'id' key and convert ObjectId to string
        return TypeGet(**created_type)
    else:
        raise HTTPException(status_code=500, detail="Failed to create type")
@router.get("/", response_model=List[Dict[str, Any]])
def get_all_types(
    htoken: Optional[str] = Header(None)
):
    host = htoken
    collection = database_manager.get_collection(host)
    types = []
    for type in collection.find():
        type_id = str(type.pop('_id'))
        type["id"] = type_id
        types.append(type)
    return types

@router.get("/{type_id}", response_model=TypeGet)
def get_type(
    request: Request,
    type_id: str,
    htoken: Optional[str] = Header(None)
):
    host = htoken
    collection = database_manager.get_collection(host)

    type = collection.find_one({"_id": type_id})
    if type:
        return Type(**type)
    else:
        raise HTTPException(status_code=404, detail="Type not found")

@router.get("/filters/", response_model=List[Type])
async def get_type_by_filter(
    request: Request,
    offset: int = 0,
    limit: int = 100,
    htoken: Optional[str] = Header(None)
) -> List[Type]:
    filter_params = await request.json()
    query = {}

    for field, value in filter_params.items():
        query[field] = value
    host = htoken
    collection = database_manager.get_collection(host)
    cursor = collection.find(query).skip(offset).limit(limit)
    types = []
    async for type in cursor:
        types.append(Type(id=str(type["_id"]), **type))
    return types

@router.put("/{type_id}", response_model=Type)
def update_type(
    request: Request,
    type_id: str,
    type_data,
    htoken: Optional[str] = Header(None)
):
    host = htoken
    collection = database_manager.get_collection(host)

    result = collection.update_one({"_id": type_id}, {"$set": type_data.dict()})
    if result.modified_count == 1:
        updated_type = collection.find_one({"_id": type_id})
        return Type(**updated_type)
    else:
        raise HTTPException(status_code=404, detail="Type not found")

@router.delete("/{type_id}")
def delete_type(
    request: Request,
    type_id: str,
    htoken: Optional[str] = Header(None)
):
    host = htoken
    collection = database_manager.get_collection(host)

    result = collection.delete_one({"_id": type_id})
    if result.deleted_count == 1:
        return {"message": "Type deleted successfully"}
    else:
        raise HTTPException(status_code=404, detail="Type not found")



