import json
import os
from fastapi import FastAPI,APIRouter, HTTPException, Request, Header, Query
from typing import List, Optional, Dict, Any
from bson import ObjectId
from app.models.userReports.userReport import UserReport,UserReportGet,UserReportCreate
from app.database import get_database_atlas
from lib.host_manager import HostDatabaseManager
from pymongo.collection import Collection

router = APIRouter()

collection_name = "userReports"
database_manager = HostDatabaseManager(collection_name)


@router.post("/", response_model=UserReportGet)
def create_userReport(
    request: Request,
    userReport_data: UserReportCreate,
    htoken: Optional[str] = Header(None)
):
    host = htoken
    collection = database_manager.get_collection(host)

    userReport_data_dict = userReport_data.dict()
    result = collection.insert_one(userReport_data_dict)

    if result.acknowledged:
        created_userReport = collection.find_one({"_id": ObjectId(result.inserted_id)})
        created_userReport['id'] = str(created_userReport['_id'])  # Add 'id' key and convert ObjectId to string
        return UserReportGet(**created_userReport)
    else:
        raise HTTPException(status_code=500, detail="Failed to create userReport")

@router.get("/", response_model=List[Dict[str, Any]])
def get_all_userReports(
    htoken: Optional[str] = Header(None)
):
    host = htoken
    collection = database_manager.get_collection(host)
    userReports = []
    for userReport in collection.find():
        userReport_id = str(userReport.pop('_id'))
        userReport["id"] = userReport_id
        userReports.append(userReport)
    return userReports

@router.get("/{userReport_id}", response_model=UserReportGet)
def get_userReport(
    request: Request,
    userReport_id: str,
    htoken: Optional[str] = Header(None)
):
    host = htoken
    collection = database_manager.get_collection(host)

    userReport = collection.find_one({"_id": userReport_id})
    if userReport:
        return UserReport(**userReport)
    else:
        raise HTTPException(status_code=404, detail="UserReport not found")

@router.get("/filters/", response_model=List[UserReport])
async def get_userReport_by_filter(
    request: Request,
    offset: int = 0,
    limit: int = 100,
    htoken: Optional[str] = Header(None)
) -> List[UserReport]:
    filter_params = await request.json()
    query = {}

    for field, value in filter_params.items():
        query[field] = value
    host = htoken
    collection = database_manager.get_collection(host)
    cursor = collection.find(query).skip(offset).limit(limit)
    userReports = []
    async for userReport in cursor:
        userReports.append(UserReport(id=str(userReport["_id"]), **userReport))
    return userReports

@router.put("/{userReport_id}", response_model=UserReport)
def update_userReport(
    request: Request,
    userReport_id: str,
    userReport_data,
    htoken: Optional[str] = Header(None)
):
    host = htoken
    collection = database_manager.get_collection(host)

    result = collection.update_one({"_id": userReport_id}, {"$set": userReport_data.dict()})
    if result.modified_count == 1:
        updated_userReport = collection.find_one({"_id": userReport_id})
        return UserReport(**updated_userReport)
    else:
        raise HTTPException(status_code=404, detail="UserReport not found")

@router.delete("/{userReport_id}")
def delete_userReport(
    request: Request,
    userReport_id: str,
    htoken: Optional[str] = Header(None)
):
    host = htoken
    collection = database_manager.get_collection(host)

    result = collection.delete_one({"_id": userReport_id})
    if result.deleted_count == 1:
        return {"message": "UserReport deleted successfully"}
    else:
        raise HTTPException(status_code=404, detail="UserReport not found")



