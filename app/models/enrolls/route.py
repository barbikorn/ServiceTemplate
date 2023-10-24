import json
import os
from fastapi import APIRouter, HTTPException, Request, Header, Query
from pymongo.collection import Collection
from typing import List, Optional, Dict, Any
from bson import ObjectId
from app.models.enrolls.enroll import Enroll,EnrollGet,EnrollCreate
from app.database import get_database_atlas
from lib.host_manager import HostDatabaseManager

router = APIRouter()

collection_name = "enrolls"
database_manager = HostDatabaseManager(collection_name)

# Assuming you have a database_manager instance



@router.post("/", response_model=EnrollGet)
def create_enroll(
    request: Request,
    enroll_data: EnrollCreate,
    htoken: Optional[str] = Header(None)
):
    host = htoken
    collection = database_manager.get_collection(host)

    enroll_data_dict = enroll_data.dict()
    result = collection.insert_one(enroll_data_dict)

    if result.acknowledged:
        created_enroll = collection.find_one({"_id": ObjectId(result.inserted_id)})
        created_enroll['id'] = str(created_enroll['_id'])  # Add 'id' key and convert ObjectId to string
        return EnrollGet(**created_enroll)
    else:
        raise HTTPException(status_code=500, detail="Failed to create enroll")

@router.get("/", response_model=List[Dict[str, Any]])
def get_all_enrolls(
    htoken: Optional[str] = Header(None)
):
    host = htoken
    collection = database_manager.get_collection(host)
    enrolls = []
    for enroll in collection.find():
        enroll_id = str(enroll.pop('_id'))
        enroll["id"] = enroll_id
        enrolls.append(enroll)
    return enrolls

@router.get("/{enroll_id}", response_model=Enroll)
def get_enroll(
    request: Request,
    enroll_id: str,
    htoken: Optional[str] = Header(None)
):
    host = htoken
    collection = database_manager.get_collection(host)

    enroll = collection.find_one({"_id": enroll_id})
    if enroll:
        return Enroll(**enroll)
    else:
        raise HTTPException(status_code=404, detail="Enroll not found")

@router.get("/filters/", response_model=List[Enroll])
async def get_enroll_by_filter(
    request: Request,
    offset: int = 0,
    limit: int = 100,
    htoken: Optional[str] = Header(None)
) -> List[Enroll]:
    filter_params = await request.json()
    query = {}

    for field, value in filter_params.items():
        query[field] = value
    host = htoken
    collection = database_manager.get_collection(host)
    cursor = collection.find(query).skip(offset).limit(limit)
    enrolls = []
    async for enroll in cursor:
        enrolls.append(Enroll(id=str(enroll["_id"]), **enroll))
    return enrolls

@router.put("/{enroll_id}", response_model=Enroll)
def update_enroll(
    request: Request,
    enroll_id: str,
    enroll_data,
    htoken: Optional[str] = Header(None)
):
    host = htoken
    collection = database_manager.get_collection(host)

    result = collection.update_one({"_id": enroll_id}, {"$set": enroll_data.dict()})
    if result.modified_count == 1:
        updated_enroll = collection.find_one({"_id": enroll_id})
        return Enroll(**updated_enroll)
    else:
        raise HTTPException(status_code=404, detail="Enroll not found")

@router.delete("/{enroll_id}")
def delete_enroll(
    request: Request,
    enroll_id: str,
    htoken: Optional[str] = Header(None)
):
    host = htoken
    collection = database_manager.get_collection(host)

    result = collection.delete_one({"_id": enroll_id})
    if result.deleted_count == 1:
        return {"message": "Enroll deleted successfully"}
    else:
        raise HTTPException(status_code=404, detail="Enroll not found")



