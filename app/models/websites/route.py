import json
import os
from fastapi import FastAPI,APIRouter, HTTPException, Request, Header, Query
from typing import List, Optional, Dict, Any
from bson import ObjectId
from app.models.websites.website import Website,WebsiteGet,WebsiteCreate
from app.database import get_database_atlas
from lib.host_manager import HostDatabaseManager
from pymongo.collection import Collection

router = APIRouter()

collection_name = "websites"
database_manager = HostDatabaseManager(collection_name)


@router.post("/", response_model=WebsiteGet)
def create_website(
    request: Request,
    website_data: WebsiteCreate,
    htoken: Optional[str] = Header(None)
):
    host = htoken
    collection = database_manager.get_collection(host)

    website_data_dict = website_data.dict()
    result = collection.insert_one(website_data_dict)

    if result.acknowledged:
        created_website = collection.find_one({"_id": ObjectId(result.inserted_id)})
        return Website(**created_website)
    else:
        raise HTTPException(status_code=500, detail="Failed to create website")

@router.get("/", response_model=List[Dict[str, Any]])
def get_all_websites(
    htoken: Optional[str] = Header(None)
):
    host = htoken
    collection = database_manager.get_collection(host)
    websites = []
    for website in collection.find():
        website_id = str(website.pop('_id'))
        website["id"] = website_id
        websites.append(website)
    return websites

@router.get("/{website_id}", response_model=WebsiteGet)
def get_website(
    request: Request,
    website_id: str,
    htoken: Optional[str] = Header(None)
):
    host = htoken
    collection = database_manager.get_collection(host)

    website = collection.find_one({"_id": website_id})
    if website:
        return Website(**website)
    else:
        raise HTTPException(status_code=404, detail="Website not found")

@router.get("/filters/", response_model=List[Website])
async def get_website_by_filter(
    request: Request,
    offset: int = 0,
    limit: int = 100,
    htoken: Optional[str] = Header(None)
) -> List[Website]:
    filter_params = await request.json()
    query = {}

    for field, value in filter_params.items():
        query[field] = value
    host = htoken
    collection = database_manager.get_collection(host)
    cursor = collection.find(query).skip(offset).limit(limit)
    websites = []
    async for website in cursor:
        websites.append(Website(id=str(website["_id"]), **website))
    return websites

@router.put("/{website_id}", response_model=Website)
def update_website(
    request: Request,
    website_id: str,
    website_data,
    htoken: Optional[str] = Header(None)
):
    host = htoken
    collection = database_manager.get_collection(host)

    result = collection.update_one({"_id": website_id}, {"$set": website_data.dict()})
    if result.modified_count == 1:
        updated_website = collection.find_one({"_id": website_id})
        return Website(**updated_website)
    else:
        raise HTTPException(status_code=404, detail="Website not found")

@router.delete("/{website_id}")
def delete_website(
    request: Request,
    website_id: str,
    htoken: Optional[str] = Header(None)
):
    host = htoken
    collection = database_manager.get_collection(host)

    result = collection.delete_one({"_id": website_id})
    if result.deleted_count == 1:
        return {"message": "Website deleted successfully"}
    else:
        raise HTTPException(status_code=404, detail="Website not found")



