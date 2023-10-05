import json
import os
from fastapi import FastAPI,APIRouter, HTTPException, Request, Header, Query
from typing import List, Optional, Dict, Any
from bson import ObjectId
from app.models.transactions.transaction import Transaction,TransactionGet,TransactionCreate
from app.database import get_database_atlas
from lib.host_manager import HostDatabaseManager
from pymongo.collection import Collection

router = APIRouter()

collection_name = "transactions"
database_manager = HostDatabaseManager(collection_name)


@router.post("/", response_model=TransactionGet)
def create_transaction(
    request: Request,
    transaction_data: TransactionCreate,
    htoken: Optional[str] = Header(None)
):
    host = htoken
    collection = database_manager.get_collection(host)

    transaction_data_dict = transaction_data.dict()
    result = collection.insert_one(transaction_data_dict)

    if result.acknowledged:
        created_transaction = collection.find_one({"_id": ObjectId(result.inserted_id)})
        return Transaction(**created_transaction)
    else:
        raise HTTPException(status_code=500, detail="Failed to create transaction")

@router.get("/", response_model=List[Dict[str, Any]])
def get_all_transactions(
    htoken: Optional[str] = Header(None)
):
    host = htoken
    collection = database_manager.get_collection(host)
    transactions = []
    for transaction in collection.find():
        transaction_id = str(transaction.pop('_id'))
        transaction["id"] = transaction_id
        transactions.append(transaction)
    return transactions

@router.get("/{transaction_id}", response_model=TransactionGet)
def get_transaction(
    request: Request,
    transaction_id: str,
    htoken: Optional[str] = Header(None)
):
    host = htoken
    collection = database_manager.get_collection(host)

    transaction = collection.find_one({"_id": transaction_id})
    if transaction:
        return Transaction(**transaction)
    else:
        raise HTTPException(status_code=404, detail="Transaction not found")

@router.get("/filters/", response_model=List[Transaction])
async def get_transaction_by_filter(
    request: Request,
    offset: int = 0,
    limit: int = 100,
    htoken: Optional[str] = Header(None)
) -> List[Transaction]:
    filter_params = await request.json()
    query = {}

    for field, value in filter_params.items():
        query[field] = value
    host = htoken
    collection = database_manager.get_collection(host)
    cursor = collection.find(query).skip(offset).limit(limit)
    transactions = []
    async for transaction in cursor:
        transactions.append(Transaction(id=str(transaction["_id"]), **transaction))
    return transactions

@router.put("/{transaction_id}", response_model=Transaction)
def update_transaction(
    request: Request,
    transaction_id: str,
    transaction_data,
    htoken: Optional[str] = Header(None)
):
    host = htoken
    collection = database_manager.get_collection(host)

    result = collection.update_one({"_id": transaction_id}, {"$set": transaction_data.dict()})
    if result.modified_count == 1:
        updated_transaction = collection.find_one({"_id": transaction_id})
        return Transaction(**updated_transaction)
    else:
        raise HTTPException(status_code=404, detail="Transaction not found")

@router.delete("/{transaction_id}")
def delete_transaction(
    request: Request,
    transaction_id: str,
    htoken: Optional[str] = Header(None)
):
    host = htoken
    collection = database_manager.get_collection(host)

    result = collection.delete_one({"_id": transaction_id})
    if result.deleted_count == 1:
        return {"message": "Transaction deleted successfully"}
    else:
        raise HTTPException(status_code=404, detail="Transaction not found")



