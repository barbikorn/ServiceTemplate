
import json
import os
from fastapi import APIRouter, HTTPException, Request, Header
from typing import List, Optional, Dict
from bson import ObjectId
from app.models.products.product import Product
from app.database import get_database_atlas
from app.models.hosts.route import HostDatabaseManager

router = APIRouter()

atlas_uri = "mongodb+srv://doadmin:AU97Jfe026gE415o@db-mongodb-kornxecobz-8ade0110.mongo.ondigitalocean.com/admin?tls=true&authSource=admin"
collection_name = "products"

database_manager = HostDatabaseManager(atlas_uri, collection_name)

@router.post("/", response_model=Product)
def create_product(
    request: Request,
    product_data: Product,
    htoken: Optional[str] = Header(None)
):
    host = htoken
    collection = database_manager.get_collection(host)

    product_data_dict = product_data.dict()
    result = collection.insert_one(product_data_dict)

    if result.acknowledged:
        created_product = collection.find_one({"_id": ObjectId(result.inserted_id)})
        return Product(**created_product)
    else:
        raise HTTPException(status_code=500, detail="Failed to create product")

@router.get("/", response_model=List[Product])
def get_all_products(
    request: Request,
    htoken: Optional[str] = Header(None)
):
    host = htoken
    collection = database_manager.get_collection(host)

    products = []
    for product in collection.find():
        products.append(Product(**product))
    return products

@router.get("/{product_id}", response_model=Product)
def get_product(
    request: Request,
    product_id: str,
    htoken: Optional[str] = Header(None)
):
    host = htoken
    collection = database_manager.get_collection(host)

    product = collection.find_one({"_id": product_id})
    if product:
        return Product(**product)
    else:
        raise HTTPException(status_code=404, detail="Product not found")

@router.get("/filters/", response_model=List[Product])
async def get_products_by_filter(
    request: Request,
    name: Optional[str] = None,
    email: Optional[str] = None,
    offset: int = 0,
    limit: int = 100,
    htoken: Optional[str] = Header(None)
):
    host = htoken
    collection = database_manager.get_collection(host)

    query = {}
    if name:
        query["name"] = name
    if email:
        query["email"] = email

    products = []
    for product in collection.find(query).skip(offset).limit(limit):
        products.append(Product(id=str(product["_id"]), **product))
    return products

@router.get("/filter", response_model=List[Product])
def get_products_by_filter(
    request: Request,
    filter: Dict,
    htoken: Optional[str] = Header(None)
):
    host = htoken
    collection = database_manager.get_collection(host)

    products = []
    for product in collection.find(filter):
        products.append(Product(**product))
    return products

@router.put("/{product_id}", response_model=Product)
def update_product(
    request: Request,
    product_id: str,
    product_data,
    htoken: Optional[str] = Header(None)
):
    host = htoken
    collection = database_manager.get_collection(host)

    result = collection.update_one({"_id": product_id}, {"$set": product_data.dict()})
    if result.modified_count == 1:
        updated_product = collection.find_one({"_id": product_id})
        return Product(**updated_product)
    else:
        raise HTTPException(status_code=404, detail="Product not found")

@router.delete("/{product_id}")
def delete_product(
    request: Request,
    product_id: str,
    htoken: Optional[str] = Header(None)
):
    host = htoken
    collection = database_manager.get_collection(host)

    result = collection.delete_one({"_id": product_id})
    if result.deleted_count == 1:
        return {"message": "Product deleted successfully"}
    else:
        raise HTTPException(status_code=404, detail="Product not found")
