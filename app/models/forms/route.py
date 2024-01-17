import json
import os
from fastapi import APIRouter, HTTPException, Request, Header, BackgroundTasks
from pymongo.collection import Collection
from typing import List, Optional, Dict, Any
from bson import ObjectId
from app.models.forms.form import Form,FormGet,FormCreate,FormUpdate
from app.database import get_database_atlas
from lib.host_manager import HostDatabaseManager
from lib.middleware.queueLog import log_request_and_upload_to_queue

router = APIRouter()

collection_name = "forms"
database_manager = HostDatabaseManager(collection_name)

# Assuming you have a database_manager instance


@router.post("/", response_model=FormGet)
async def create_form(
    request: Request,
    form_data: FormCreate,
    background_tasks: BackgroundTasks,
    htoken: Optional[str] = Header(None)
):
    
    host = htoken
    collection = await database_manager.get_collection(host)

    form_data_dict = form_data.dict()
    result = collection.insert_one(form_data_dict)

    if result.acknowledged:

        created_form = form_data_dict  # Start with the form data provided
        created_form['id'] = str(result.inserted_id)  # Add 'id' key and convert ObjectId to string
        background_tasks.add_task(
            log_request_and_upload_to_queue,
            request, collection_name, created_form, htoken, background_tasks
        )
        return FormGet(**created_form)
    else:
        raise HTTPException(status_code=500, detail="Failed to create form")


@router.get("/", response_model=List[Dict[str, Any]])
def get_all_forms(
    htoken: Optional[str] = Header(None)
):
    host = htoken
    collection = database_manager.get_collection(host)
    forms = []
    for form in collection.find():
        form_id = str(form.pop('_id'))
        form["id"] = form_id
        forms.append(form)
    return forms

@router.get("/{form_id}", response_model=Form)
def get_form(
    request: Request,
    form_id: str,
    htoken: Optional[str] = Header(None)
):
    host = htoken
    collection = database_manager.get_collection(host)

    form = collection.find_one({"_id": form_id})
    if form:
        return Form(**form)
    else:
        raise HTTPException(status_code=404, detail="Form not found")

@router.get("/filters/", response_model=List[Form])
async def get_form_by_filter(
    request: Request,
    offset: int = 0,
    limit: int = 100,
    htoken: Optional[str] = Header(None)
) -> List[Form]:
    filter_params = await request.json()
    query = {}

    for field, value in filter_params.items():
        query[field] = value
    host = htoken
    collection = database_manager.get_collection(host)
    cursor = collection.find(query).skip(offset).limit(limit)
    forms = []
    async for form in cursor:
        forms.append(Form(id=str(form["_id"]), **form))
    return forms
@router.put("/{form_id}", response_model=FormGet)
async def update_form(
    request: Request,
    form_id: str,
    form_data: FormUpdate,
    background_tasks: BackgroundTasks,
    htoken: Optional[str] = Header(None)
):
    host = htoken
    collection = await database_manager.get_collection(host)
    result = collection.update_one({"_id": ObjectId(form_id)}, {"$set": form_data.dict()})

    if result.modified_count == 1:
        updated_form = collection.find_one({"_id": ObjectId(form_id)})

        # Use background task to log the update
        background_tasks.add_task(
            log_request_and_upload_to_queue,
            request, collection_name, updated_form, htoken
        )

        return FormGet(**updated_form)
    else:
        raise HTTPException(status_code=404, detail="Nothing change")

@router.delete("/{form_id}")
def delete_form(
    request: Request,
    form_id: str,
    htoken: Optional[str] = Header(None)
):
    host = htoken
    collection = database_manager.get_collection(host)

    result = collection.delete_one({"_id": form_id})
    if result.deleted_count == 1:
        return {"message": "Form deleted successfully"}
    else:
        raise HTTPException(status_code=404, detail="Form not found")



