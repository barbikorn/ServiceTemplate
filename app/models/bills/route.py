import json
import os
from fastapi import FastAPI, APIRouter, HTTPException, Request, Header, Query
from pymongo.collection import Collection
from typing import List, Optional, Dict, Any
from bson import ObjectId
from app.models.bills.bill import Bill,BillGet,BillCreate
from app.database import get_database_atlas
from lib.host_manager import HostDatabaseManager

router = APIRouter()

collection_name = "bills"
database_manager = HostDatabaseManager(collection_name)

# CRUD
@router.post("/", response_model=BillGet)
def create_bill(
    request: Request,
    bill_data: BillCreate,
    htoken: Optional[str] = Header(None)
):
    host = htoken
    collection = database_manager.get_collection(host)

    bill_data_dict = bill_data.dict()
    result = collection.insert_one(bill_data_dict)

    if result.acknowledged:
        created_bill = collection.find_one({"_id": ObjectId(result.inserted_id)})
        return Bill(**created_bill)
    else:
        raise HTTPException(status_code=500, detail="Failed to create bill")

@router.get("/", response_model=List[Dict[str, Any]])
def get_all_bills(
    bill_id: str,
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

@router.put("/{bill_id}", response_model=Bill)
def update_bill(
    request: Request,
    bill_id: str,
    bill_data,
    htoken: Optional[str] = Header(None)
):
    host = htoken
    collection = database_manager.get_collection(host)

    result = collection.update_one({"_id": bill_id}, {"$set": bill_data.dict()})
    if result.modified_count == 1:
        updated_bill = collection.find_one({"_id": bill_id})
        return Bill(**updated_bill)
    else:
        raise HTTPException(status_code=404, detail="Bill not found")

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



