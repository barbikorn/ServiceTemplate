import json
import os
from fastapi import FastAPI,APIRouter, HTTPException, Request, Header, Query
from typing import List, Optional, Dict, Any
from bson import ObjectId
from app.models.templates.template import Template,TemplateGet,TemplateCreate
from app.database import get_database_atlas
from lib.host_manager import HostDatabaseManager
from pymongo.collection import Collection

router = APIRouter()

collection_name = "templates"
database_manager = HostDatabaseManager(collection_name)


@router.post("/", response_model=TemplateGet)
def create_template(
    request: Request,
    template_data: TemplateCreate,
    htoken: Optional[str] = Header(None)
):
    host = htoken
    collection = database_manager.get_collection(host)

    template_data_dict = template_data.dict()
    result = collection.insert_one(template_data_dict)

    if result.acknowledged:
        created_template = collection.find_one({"_id": ObjectId(result.inserted_id)})
        return Template(**created_template)
    else:
        raise HTTPException(status_code=500, detail="Failed to create template")

@router.get("/", response_model=List[Dict[str, Any]])
def get_all_templates(
    htoken: Optional[str] = Header(None)
):
    host = htoken
    collection = database_manager.get_collection(host)
    templates = []
    for template in collection.find():
        template_id = str(template.pop('_id'))
        template["id"] = template_id
        templates.append(template)
    return templates

@router.get("/{template_id}", response_model=TemplateGet)
def get_template(
    request: Request,
    template_id: str,
    htoken: Optional[str] = Header(None)
):
    host = htoken
    collection = database_manager.get_collection(host)

    template = collection.find_one({"_id": template_id})
    if template:
        return Template(**template)
    else:
        raise HTTPException(status_code=404, detail="Template not found")

@router.get("/filters/", response_model=List[Template])
async def get_template_by_filter(
    request: Request,
    offset: int = 0,
    limit: int = 100,
    htoken: Optional[str] = Header(None)
) -> List[Template]:
    filter_params = await request.json()
    query = {}

    for field, value in filter_params.items():
        query[field] = value
    host = htoken
    collection = database_manager.get_collection(host)
    cursor = collection.find(query).skip(offset).limit(limit)
    templates = []
    async for template in cursor:
        templates.append(Template(id=str(template["_id"]), **template))
    return templates

@router.put("/{template_id}", response_model=Template)
def update_template(
    request: Request,
    template_id: str,
    template_data,
    htoken: Optional[str] = Header(None)
):
    host = htoken
    collection = database_manager.get_collection(host)

    result = collection.update_one({"_id": template_id}, {"$set": template_data.dict()})
    if result.modified_count == 1:
        updated_template = collection.find_one({"_id": template_id})
        return Template(**updated_template)
    else:
        raise HTTPException(status_code=404, detail="Template not found")

@router.delete("/{template_id}")
def delete_template(
    request: Request,
    template_id: str,
    htoken: Optional[str] = Header(None)
):
    host = htoken
    collection = database_manager.get_collection(host)

    result = collection.delete_one({"_id": template_id})
    if result.deleted_count == 1:
        return {"message": "Template deleted successfully"}
    else:
        raise HTTPException(status_code=404, detail="Template not found")



