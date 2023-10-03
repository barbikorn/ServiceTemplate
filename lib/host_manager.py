import os
import json
from typing import Dict, Optional
from app.database import get_database_atlas
from fastapi import HTTPException

from typing import Dict, Optional
from app.database import get_database_atlas

class HostDatabaseManager:
    def __init__(self, collection_name: str):
        self.atlas_uri = "mongodb+srv://doadmin:k2R0165xp4G8iV3E@host-manager-a6c7287d.mongo.ondigitalocean.com/admin?tls=true&authSource=admin"
        self.collection_name = collection_name
        self.collection = get_database_atlas("hosts", self.atlas_uri)[collection_name]

    def get_database_name(self, host: str) -> Optional[str]:
        host_entry = self.collection.find_one({"token": host})
        if host_entry:
            return host_entry["databasename"]
        return None

    def get_collection(self, host: str):
        database_name = self.get_database_name(host)
        if database_name:
            return get_database_atlas(database_name, self.atlas_uri)[self.collection_name]
        raise HTTPException(status_code=404, detail="Database not found for the host")
