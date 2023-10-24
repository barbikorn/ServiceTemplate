
import json
import os
from fastapi import APIRouter, HTTPException, Request, Header, Query
from typing import List, Optional, Dict, Any
from bson import ObjectId
from app.models.users.user import User,UserGet,UserCreate
from app.database import get_database_atlas
from lib.host_manager import HostDatabaseManager

router = APIRouter()

collection_name = "users"
database_manager = HostDatabaseManager(collection_name)


from fastapi import FastAPI, Header, HTTPException
from pymongo.collection import Collection
from bson import ObjectId

app = FastAPI()

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
def create_user(
    request: Request,
    user_data: UserCreate,
    htoken: Optional[str] = Header(None)
):
    host = htoken
    collection = database_manager.get_collection(host)

    user_data_dict = user_data.dict()
    result = collection.insert_one(user_data_dict)

    if result.acknowledged:
        created_user = collection.find_one({"_id": ObjectId(result.inserted_id)})
        created_user['id'] = str(created_user['_id'])  # Add 'id' key and convert ObjectId to string
        return UserGet(**created_user)
    else:
        raise HTTPException(status_code=500, detail="Failed to create user")


@router.get("/", response_model=List[Dict[str, Any]])
def get_all_users(
    request: Request,
    htoken: Optional[str] = Header(None)
):
    host = htoken
    collection = database_manager.get_collection(host)
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

@router.put("/{user_id}", response_model=User)
def update_user(
    request: Request,
    user_id: str,
    user_data,
    htoken: Optional[str] = Header(None)
):
    host = htoken
    collection = database_manager.get_collection(host)

    result = collection.update_one({"_id": user_id}, {"$set": user_data.dict()})
    if result.modified_count == 1:
        updated_user = collection.find_one({"_id": user_id})
        return User(**updated_user)
    else:
        raise HTTPException(status_code=404, detail="User not found")

@router.delete("/{user_id}")
def delete_user(
    request: Request,
    user_id: str,
    htoken: Optional[str] = Header(None)
):
    host = htoken
    collection = database_manager.get_collection(host)

    result = collection.delete_one({"_id": user_id})
    if result.deleted_count == 1:
        return {"message": "User deleted successfully"}
    else:
        raise HTTPException(status_code=404, detail="User not found")



