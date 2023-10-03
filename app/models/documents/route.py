import json
import os
from fastapi import APIRouter, HTTPException, Request, Header, Query
from pymongo.collection import Collection
from typing import List, Optional, Dict, Any
from bson import ObjectId
from app.models.documents.document import Document,DocumentGet,DocumentCreate
from app.database import get_database_atlas
from lib.host_manager import HostDatabaseManager

router = APIRouter()

collection_name = "documents"
database_manager = HostDatabaseManager(collection_name)

# Assuming you have a database_manager instance



@router.post("/", response_model=DocumentGet)
def create_document(
    request: Request,
    document_data: DocumentCreate,
    htoken: Optional[str] = Header(None)
):
    host = htoken
    collection = database_manager.get_collection(host)

    document_data_dict = document_data.dict()
    result = collection.insert_one(document_data_dict)

    if result.acknowledged:
        created_document = collection.find_one({"_id": ObjectId(result.inserted_id)})
        return Document(**created_document)
    else:
        raise HTTPException(status_code=500, detail="Failed to create document")

@router.get("/", response_model=List[Dict[str, Any]])
def get_all_documents(
    document_id: str,
    htoken: Optional[str] = Header(None)
):
    host = htoken
    collection = database_manager.get_collection(host)
    documents = []
    for document in collection.find():
        document_id = str(document.pop('_id'))
        document["id"] = document_id
        documents.append(document)
    return documents

@router.get("/{document_id}", response_model=Document)
def get_document(
    request: Request,
    document_id: str,
    htoken: Optional[str] = Header(None)
):
    host = htoken
    collection = database_manager.get_collection(host)

    document = collection.find_one({"_id": document_id})
    if document:
        return Document(**document)
    else:
        raise HTTPException(status_code=404, detail="Document not found")

@router.get("/filters/", response_model=List[Document])
async def get_document_by_filter(
    request: Request,
    offset: int = 0,
    limit: int = 100,
    htoken: Optional[str] = Header(None)
) -> List[Document]:
    filter_params = await request.json()
    query = {}

    for field, value in filter_params.items():
        query[field] = value
    host = htoken
    collection = database_manager.get_collection(host)
    cursor = collection.find(query).skip(offset).limit(limit)
    documents = []
    async for document in cursor:
        documents.append(Document(id=str(document["_id"]), **document))
    return documents

@router.put("/{document_id}", response_model=Document)
def update_document(
    request: Request,
    document_id: str,
    document_data,
    htoken: Optional[str] = Header(None)
):
    host = htoken
    collection = database_manager.get_collection(host)

    result = collection.update_one({"_id": document_id}, {"$set": document_data.dict()})
    if result.modified_count == 1:
        updated_document = collection.find_one({"_id": document_id})
        return Document(**updated_document)
    else:
        raise HTTPException(status_code=404, detail="Document not found")

@router.delete("/{document_id}")
def delete_document(
    request: Request,
    document_id: str,
    htoken: Optional[str] = Header(None)
):
    host = htoken
    collection = database_manager.get_collection(host)

    result = collection.delete_one({"_id": document_id})
    if result.deleted_count == 1:
        return {"message": "Document deleted successfully"}
    else:
        raise HTTPException(status_code=404, detail="Document not found")



