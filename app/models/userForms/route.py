import json
import os
from fastapi import FastAPI,APIRouter, HTTPException, Request, Header, Query
from typing import List, Optional, Dict, Any
from bson import ObjectId
from app.models.userForms.userForm import UserForm,UserFormGet,UserFormCreate
from app.database import get_database_atlas
from lib.host_manager import HostDatabaseManager
from pymongo.collection import Collection

router = APIRouter()

collection_name = "userForms"
database_manager = HostDatabaseManager(collection_name)


@router.post("/", response_model=UserFormGet)
def create_userForm(
    request: Request,
    userForm_data: UserFormCreate,
    htoken: Optional[str] = Header(None)
):
    host = htoken
    collection = database_manager.get_collection(host)

    userForm_data_dict = userForm_data.dict()
    result = collection.insert_one(userForm_data_dict)

    if result.acknowledged:
        created_userForm = collection.find_one({"_id": ObjectId(result.inserted_id)})
        created_userForm['id'] = str(created_userForm['_id'])  # Add 'id' key and convert ObjectId to string
        return UserFormGet(**created_userForm)
    else:
        raise HTTPException(status_code=500, detail="Failed to create userForm")

@router.get("/", response_model=List[Dict[str, Any]])
def get_all_userForms(
    htoken: Optional[str] = Header(None)
):
    host = htoken
    collection = database_manager.get_collection(host)
    userForms = []
    for userForm in collection.find():
        userForm_id = str(userForm.pop('_id'))
        userForm["id"] = userForm_id
        userForms.append(userForm)
    return userForms

@router.get("/{userForm_id}", response_model=UserFormGet)
def get_userForm(
    request: Request,
    userForm_id: str,
    htoken: Optional[str] = Header(None)
):
    host = htoken
    collection = database_manager.get_collection(host)

    userForm = collection.find_one({"_id": userForm_id})
    if userForm:
        return UserForm(**userForm)
    else:
        raise HTTPException(status_code=404, detail="UserForm not found")

@router.get("/filters/", response_model=List[UserForm])
async def get_userForm_by_filter(
    request: Request,
    offset: int = 0,
    limit: int = 100,
    htoken: Optional[str] = Header(None)
) -> List[UserForm]:
    filter_params = await request.json()
    query = {}

    for field, value in filter_params.items():
        query[field] = value
    host = htoken
    collection = database_manager.get_collection(host)
    cursor = collection.find(query).skip(offset).limit(limit)
    userForms = []
    async for userForm in cursor:
        userForms.append(UserForm(id=str(userForm["_id"]), **userForm))
    return userForms

@router.put("/{userForm_id}", response_model=UserForm)
def update_userForm(
    request: Request,
    userForm_id: str,
    userForm_data,
    htoken: Optional[str] = Header(None)
):
    host = htoken
    collection = database_manager.get_collection(host)

    result = collection.update_one({"_id": userForm_id}, {"$set": userForm_data.dict()})
    if result.modified_count == 1:
        updated_userForm = collection.find_one({"_id": userForm_id})
        return UserForm(**updated_userForm)
    else:
        raise HTTPException(status_code=404, detail="UserForm not found")

@router.delete("/{userForm_id}")
def delete_userForm(
    request: Request,
    userForm_id: str,
    htoken: Optional[str] = Header(None)
):
    host = htoken
    collection = database_manager.get_collection(host)

    result = collection.delete_one({"_id": userForm_id})
    if result.deleted_count == 1:
        return {"message": "UserForm deleted successfully"}
    else:
        raise HTTPException(status_code=404, detail="UserForm not found")



