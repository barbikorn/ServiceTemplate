
import json
import os
from fastapi import APIRouter, HTTPException, Request, Header, Query ,BackgroundTasks
from typing import List, Optional, Dict, Any
from bson import ObjectId
from app.models.users.user import User,UserGet,UserCreate,UserUpdate
from app.database import get_database_atlas
from lib.host_manager import HostDatabaseManager
# from lib.convert_request import request_to_dict
from lib.middleware.queueLog import log_request_and_upload_to_queue



router = APIRouter()

collection_name = "users"
database_manager = HostDatabaseManager(collection_name)
# Use the middleware on the router

from fastapi import FastAPI, Header, HTTPException
from pymongo.collection import Collection
from bson import ObjectId


# Assuming you have a database_manager instance


# @router.get("/search_look/")
# async def search(query: str, aggregation: Optional[List[dict]] = None):
#     try:
#         aggregation_pipeline = [
#             {"$match": {"$text": {"$search": query}}},
#             # Perform a $lookup to join data from the authors collection
#             {"$lookup": {
#                 "from": "authors",
#                 "localField": "author_id",
#                 "foreignField": "_id",
#                 "as": "author_info"
#             }},
#             # Add any additional aggregation stages
#         ]
        
#         if aggregation:
#             aggregation_pipeline.extend(aggregation)

#         # Perform the search query
#         search_result = list(books_collection.aggregate(aggregation_pipeline))

#         return search_result

#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))

@router.post("/", response_model=UserGet)
async def create_user(
    request: Request,
    user_data: UserCreate,
    background_tasks: BackgroundTasks,
    htoken: Optional[str] = Header(None)
):
    
    host = htoken
    collection = await database_manager.get_collection(host)

    user_data_dict = user_data.dict()
    result = collection.insert_one(user_data_dict)

    if result.acknowledged:

        created_user = user_data_dict  # Start with the user data provided
        created_user['id'] = str(result.inserted_id)  # Add 'id' key and convert ObjectId to string
        background_tasks.add_task(
            log_request_and_upload_to_queue,
            request, collection_name, created_user, htoken
        )
        return UserGet(**created_user)
    else:
        raise HTTPException(status_code=500, detail="Failed to create user")


@router.get("/", response_model=List[Dict[str, Any]])
async def get_all_users(
    request: Request,
    htoken: Optional[str] = Header(None)
):
    host = htoken
    collection = await database_manager.get_collection(host)
    users = []
    for user in collection.find():
        user_id = str(user.pop('_id'))
        user["id"] = user_id
        users.append(UserGet(**user))
    return users

@router.get("/{user_id}", response_model=User)
def get_user(
    request: Request,
    user_id: str,
    htoken: Optional[str] = Header(None)
):
    host = htoken
    collection = database_manager.get_collection(host)

    user = collection.find_one({"_id": user_id})
    if user:
        return User(**user)
    else:
        raise HTTPException(status_code=404, detail="User not found")

@router.get("/filters/", response_model=List[User])
async def get_user_by_filter(
    request: Request,
    offset: int = 0,
    limit: int = 100,
    htoken: Optional[str] = Header(None)
) -> List[User]:
    filter_params = await request.json()
    query = {}

    for field, value in filter_params.items():
        query[field] = value
    host = htoken
    collection = database_manager.get_collection(host)
    cursor = collection.find(query).skip(offset).limit(limit)
    users = []
    async for user in cursor:
        users.append(User(id=str(user["_id"]), **user))
    return users

@router.put("/{user_id}", response_model=UserGet)
async def update_user(
    request: Request,
    user_id: str,
    user_data: UserUpdate,
    background_tasks: BackgroundTasks,
    htoken: Optional[str] = Header(None)
):
    host = htoken
    collection = await database_manager.get_collection(host)
    result = collection.update_one({"_id": ObjectId(user_id)}, {"$set": user_data.dict()})

    if result.modified_count == 1:
        updated_user = collection.find_one({"_id": ObjectId(user_id)})

        # Use background task to log the update
        background_tasks.add_task(
            log_request_and_upload_to_queue,
            request, collection_name, updated_user, htoken
        )

        return UserGet(**updated_user)
    else:
        raise HTTPException(status_code=404, detail="Nothing change")

@router.delete("/{user_id}")
async def delete_user(
    request: Request,
    user_id: str,
    htoken: Optional[str] = Header(None)
):
    host = htoken
    collection = await database_manager.get_collection(host)

    result = collection.delete_one({"_id": user_id})
    if result.deleted_count == 1:
        return {"message": "User deleted successfully"}
    else:
        raise HTTPException(status_code=404, detail="User not found")



