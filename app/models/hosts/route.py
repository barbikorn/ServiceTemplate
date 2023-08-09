from typing import Dict, Optional, List
from app.database import get_database_atlas
from fastapi import HTTPException, APIRouter, Depends , Request
from pydantic import BaseModel
from bson import ObjectId

from app.models.hosts.host import Host

class HostDatabaseManager:
    def __init__(self,collection_name: str):
        self.atlas_uri = "mongodb+srv://doadmin:AU97Jfe026gE415o@db-mongodb-kornxecobz-8ade0110.mongo.ondigitalocean.com/admin?tls=true&authSource=admin"
        self.collection_name = collection_name

    def get_database_name(self, host: str) -> Optional[str]:
        host_entry = collection.find_one({"token": host})
        if host_entry:
            return host_entry["databasename"]
        return None

    def get_collection(self, host: str):
        database_name = self.get_database_name(host)
        if database_name:
            return get_database_atlas(database_name, self.atlas_uri)[self.collection_name]
        raise HTTPException(status_code=404, detail="Database not found for the host")

router = APIRouter()
collection_name = "hosts"
atlas_uri = "mongodb+srv://doadmin:AU97Jfe026gE415o@db-mongodb-kornxecobz-8ade0110.mongo.ondigitalocean.com/admin?tls=true&authSource=admin"
collection = get_database_atlas("hosts", atlas_uri)[collection_name]

host_db_manager = HostDatabaseManager(collection_name)

@router.post("/", response_model=Host,include_in_schema=False)
def create_host(host_data: Host):
    host_data_dict = host_data.dict()
    result = collection.insert_one(host_data_dict)

    if result.acknowledged:
        created_host = collection.find_one({"_id": ObjectId(result.inserted_id)})
        return Host(id=str(created_host["_id"]), **created_host)
    else:
        raise HTTPException(status_code=500, detail="Failed to create host")

@router.get("/", response_model=List[Host],include_in_schema=False)
def get_all_hosts():
    hosts = []
    for host in collection.find():
        hosts.append(Host(id=str(host["_id"]), **host))
    return hosts

@router.get("/{host_id}", response_model=Host,include_in_schema=False)
def get_host(host_id: str):
    host = collection.find_one({"_id": ObjectId(host_id)})
    if host:
        return Host(id=str(host["_id"]), **host)
    else:
        raise HTTPException(status_code=404, detail="Host not found")

@router.get("/filters/", response_model=List[Host])
async def get_host_by_filter(
    request: Request,
    offset: int = 0,
    limit: int = 100
) -> List[Host]:
    filter_params = await request.json()
    query = {}

    for field, value in filter_params.items():
        query[field] = value

    cursor = collection.find(query).skip(offset).limit(limit)
    hosts = []
    async for host in cursor:
        hosts.append(Host(id=str(host["_id"]), **host))
    return hosts

@router.put("/{host_id}", response_model=Host,include_in_schema=False)
def update_host(host_id: str, host_data: Host):
    result = collection.update_one({"_id": ObjectId(host_id)}, {"$set": host_data.dict()})
    if result.modified_count == 1:
        updated_host = collection.find_one({"_id": ObjectId(host_id)})
        return Host(id=str(updated_host["_id"]), **updated_host)
    else:
        raise HTTPException(status_code=404, detail="Host not found")

@router.delete("/{host_id}",include_in_schema=False)
def delete_host(host_id: str):
    result = collection.delete_one({"_id": ObjectId(host_id)})
    if result.deleted_count == 1:
        return {"message": "Host deleted successfully"}
    else:
        raise HTTPException(status_code=404, detail="Host not found")

