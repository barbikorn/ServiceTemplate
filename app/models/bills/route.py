import json
import os
from fastapi import FastAPI, APIRouter, HTTPException, Request, Header, BackgroundTasks
from pymongo.collection import Collection
from typing import List, Optional, Dict, Any
from bson import ObjectId
from app.models.bills.bill import Bill,BillGet,BillCreate,BillUpdate
from app.database import get_database_atlas
from lib.host_manager import HostDatabaseManager
from lib.middleware.queueLog import log_request_and_upload_to_queue

router = APIRouter()

collection_name = "bills"
database_manager = HostDatabaseManager(collection_name)

@router.post("/", response_model=BillGet)
async def create_bill(
    request: Request,
    bill_data: BillCreate,
    background_tasks: BackgroundTasks,
    htoken: Optional[str] = Header(None)
):
    
    host = htoken
    collection = await database_manager.get_collection(host)

    bill_data_dict = bill_data.dict()
    result = collection.insert_one(bill_data_dict)

    if result.acknowledged:

        created_bill = bill_data_dict  # Start with the bill data provided
        created_bill['id'] = str(result.inserted_id)  # Add 'id' key and convert ObjectId to string
        background_tasks.add_task(
            log_request_and_upload_to_queue,
            request, collection_name, created_bill, htoken, background_tasks
        )
        return BillGet(**created_bill)
    else:
        raise HTTPException(status_code=500, detail="Failed to create bill")


@router.get("/", response_model=List[Dict[str, Any]])
def get_all_bills(
    htoken: Optional[str] = Header(None)
):
    host = htoken
    collection = database_manager.get_collection(host)
    bills = []
    for bill in collection.find():
        bill_id = str(bill.pop('_id'))
        bill["id"] = bill_id
        bills.append(bill)
    return bills

@router.get("/{bill_id}", response_model=Bill)
def get_bill(
    request: Request,
    bill_id: str,
    htoken: Optional[str] = Header(None)
):
    host = htoken
    collection = database_manager.get_collection(host)

    bill = collection.find_one({"_id": bill_id})
    if bill:
        return Bill(**bill)
    else:
        raise HTTPException(status_code=404, detail="Bill not found")

@router.get("/filters/", response_model=List[Bill])
async def get_bill_by_filter(
    request: Request,
    offset: int = 0,
    limit: int = 100,
    htoken: Optional[str] = Header(None)
) -> List[Bill]:
    filter_params = await request.json()
    query = {}

    for field, value in filter_params.items():
        query[field] = value
    host = htoken
    collection = database_manager.get_collection(host)
    cursor = collection.find(query).skip(offset).limit(limit)
    bills = []
    async for bill in cursor:
        bills.append(Bill(id=str(bill["_id"]), **bill))
    return bills


@router.put("/{bill_id}", response_model=BillGet)
async def update_bill(
    request: Request,
    bill_id: str,
    bill_data: BillUpdate,
    background_tasks: BackgroundTasks,
    htoken: Optional[str] = Header(None)
):
    host = htoken
    collection = await database_manager.get_collection(host)
    result = collection.update_one({"_id": ObjectId(bill_id)}, {"$set": bill_data.dict()})

    if result.modified_count == 1:
        updated_bill = collection.find_one({"_id": ObjectId(bill_id)})

        # Use background task to log the update
        background_tasks.add_task(
            log_request_and_upload_to_queue,
            request, collection_name, updated_bill, htoken
        )

        return BillGet(**updated_bill)
    else:
        raise HTTPException(status_code=404, detail="Nothing change")

@router.delete("/{bill_id}")
def delete_bill(
    request: Request,
    bill_id: str,
    htoken: Optional[str] = Header(None)
):
    host = htoken
    collection = database_manager.get_collection(host)

    result = collection.delete_one({"_id": bill_id})
    if result.deleted_count == 1:
        return {"message": "Bill deleted successfully"}
    else:
        raise HTTPException(status_code=404, detail="Bill not found")



