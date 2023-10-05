import json
import os
from fastapi import APIRouter, HTTPException, Request, Header, Query
from typing import List, Optional, Dict, Any
from bson import ObjectId
from app.models.certifications.certification import Certification,CertificationGet,CertificationCreate
from app.database import get_database_atlas
from lib.host_manager import HostDatabaseManager

router = APIRouter()

collection_name = "certifications"
database_manager = HostDatabaseManager(collection_name)


@router.post("/", response_model=CertificationGet)
def create_certification(
    request: Request,
    certification_data: CertificationCreate,
    htoken: Optional[str] = Header(None)
):
    host = htoken
    collection = database_manager.get_collection(host)

    certification_data_dict = certification_data.dict()
    result = collection.insert_one(certification_data_dict)

    if result.acknowledged:
        created_certification = collection.find_one({"_id": ObjectId(result.inserted_id)})
        return Certification(**created_certification)
    else:
        raise HTTPException(status_code=500, detail="Failed to create certification")

@router.get("/", response_model=List[Dict[str, Any]])
def get_all_certifications(
    htoken: Optional[str] = Header(None)
):
    host = htoken
    collection = database_manager.get_collection(host)
    certifications = []
    for certification in collection.find():
        certification_id = str(certification.pop('_id'))
        certification["id"] = certification_id
        certifications.append(certification)
    return certifications

@router.get("/{certification_id}", response_model=Certification)
def get_certification(
    request: Request,
    certification_id: str,
    htoken: Optional[str] = Header(None)
):
    host = htoken
    collection = database_manager.get_collection(host)

    certification = collection.find_one({"_id": certification_id})
    if certification:
        return Certification(**certification)
    else:
        raise HTTPException(status_code=404, detail="Certification not found")

@router.get("/filters/", response_model=List[Certification])
async def get_certification_by_filter(
    request: Request,
    offset: int = 0,
    limit: int = 100,
    htoken: Optional[str] = Header(None)
) -> List[Certification]:
    filter_params = await request.json()
    query = {}

    for field, value in filter_params.items():
        query[field] = value
    host = htoken
    collection = database_manager.get_collection(host)
    cursor = collection.find(query).skip(offset).limit(limit)
    certifications = []
    async for certification in cursor:
        certifications.append(Certification(id=str(certification["_id"]), **certification))
    return certifications

@router.put("/{certification_id}", response_model=Certification)
def update_certification(
    request: Request,
    certification_id: str,
    certification_data,
    htoken: Optional[str] = Header(None)
):
    host = htoken
    collection = database_manager.get_collection(host)

    result = collection.update_one({"_id": certification_id}, {"$set": certification_data.dict()})
    if result.modified_count == 1:
        updated_certification = collection.find_one({"_id": certification_id})
        return Certification(**updated_certification)
    else:
        raise HTTPException(status_code=404, detail="Certification not found")

@router.delete("/{certification_id}")
def delete_certification(
    request: Request,
    certification_id: str,
    htoken: Optional[str] = Header(None)
):
    host = htoken
    collection = database_manager.get_collection(host)

    result = collection.delete_one({"_id": certification_id})
    if result.deleted_count == 1:
        return {"message": "Certification deleted successfully"}
    else:
        raise HTTPException(status_code=404, detail="Certification not found")



