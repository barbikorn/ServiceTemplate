import os
import json
from typing import Dict, Optional
from app.database import get_database_atlas
from fastapi import HTTPException

from typing import Dict, Optional
from app.database import get_database_atlas

class HostDatabaseManager:
    def __init__(self, host_config_path: str, atlas_uri: str, collection_name: str):
        self.host_config_path = host_config_path
        self.atlas_uri = atlas_uri
        self.collection_name = collection_name
        self.host_config = self.load_host_config()
        collection_name = "hosts"

    def load_host_config(self) -> Dict[str, str]:
        collection = self.database_manager.get_collection("host")
        hosts = []
        for host in collection.find():
            hosts.append(Host(**host))
        return hosts

    def get_database_name(self, host: str) -> Optional[str]:
        host_config_entry = self.host_config.get(host)
        if host_config_entry:
            return host_config_entry.get("databasename")
        return None

    def get_collection(self, host: str):
        database_name = self.get_database_name(host)
        if database_name:
            return get_database_atlas(database_name, self.atlas_uri)[self.collection_name]
        raise HTTPException(status_code=404, detail="Database not found for the host")
