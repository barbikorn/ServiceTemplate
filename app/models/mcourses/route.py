
import json
import os
from fastapi import FastAPI, APIRouter, HTTPException, Request, Header, Query
from typing import List, Optional, Dict, Any
from bson import ObjectId
from app.models.mcourses.mcourse import Mcourse,McourseGet,McourseCreate
from app.database import get_database_atlas
from lib.host_manager import HostDatabaseManager
from pymongo.collection import Collection

router = APIRouter()

collection_name = "mcourses"
database_manager = HostDatabaseManager(collection_name)
app = FastAPI()

# CRUD
@router.post("/", response_model=McourseGet)
def create_mcourse(
    request: Request,
    mcourse_data: McourseCreate,
    htoken: Optional[str] = Header(None)
):
    host = htoken
    collection = database_manager.get_collection(host)

    mcourse_data_dict = mcourse_data.dict()
    result = collection.insert_one(mcourse_data_dict)

    if result.acknowledged:
        created_mcourse = collection.find_one({"_id": ObjectId(result.inserted_id)})
        return Mcourse(**created_mcourse)
    else:
        raise HTTPException(status_code=500, detail="Failed to create mcourse")

@router.get("/", response_model=List[Dict[str, Any]])
def get_all_mcourses(
    htoken: Optional[str] = Header(None)
):
    host = htoken
    collection = database_manager.get_collection(host)
    mcourses = []
    for mcourse in collection.find():
        mcourse_id = str(mcourse.pop('_id'))
        mcourse["id"] = mcourse_id
        mcourses.append(mcourse)
    return mcourses

@router.get("/{mcourse_id}", response_model=Mcourse)
def get_mcourse(
    request: Request,
    mcourse_id: str,
    htoken: Optional[str] = Header(None)
):
    host = htoken
    collection = database_manager.get_collection(host)

    mcourse = collection.find_one({"_id": mcourse_id})
    if mcourse:
        return Mcourse(**mcourse)
    else:
        raise HTTPException(status_code=404, detail="Mcourse not found")

@router.get("/filters/", response_model=List[Mcourse])
async def get_mcourse_by_filter(
    request: Request,
    offset: int = 0,
    limit: int = 100,
    htoken: Optional[str] = Header(None)
) -> List[Mcourse]:
    filter_params = await request.json()
    query = {}

    for field, value in filter_params.items():
        query[field] = value
    host = htoken
    collection = database_manager.get_collection(host)
    cursor = collection.find(query).skip(offset).limit(limit)
    mcourses = []
    async for mcourse in cursor:
        mcourses.append(Mcourse(id=str(mcourse["_id"]), **mcourse))
    return mcourses

@router.put("/{mcourse_id}", response_model=Mcourse)
def update_mcourse(
    request: Request,
    mcourse_id: str,
    mcourse_data,
    htoken: Optional[str] = Header(None)
):
    host = htoken
    collection = database_manager.get_collection(host)

    result = collection.update_one({"_id": mcourse_id}, {"$set": mcourse_data.dict()})
    if result.modified_count == 1:
        updated_mcourse = collection.find_one({"_id": mcourse_id})
        return Mcourse(**updated_mcourse)
    else:
        raise HTTPException(status_code=404, detail="Mcourse not found")

@router.delete("/{mcourse_id}")
def delete_mcourse(
    request: Request,
    mcourse_id: str,
    htoken: Optional[str] = Header(None)
):
    host = htoken
    collection = database_manager.get_collection(host)

    result = collection.delete_one({"_id": mcourse_id})
    if result.deleted_count == 1:
        return {"message": "Mcourse deleted successfully"}
    else:
        raise HTTPException(status_code=404, detail="Mcourse not found")



