import os
import json
from typing import Dict, Optional, Any
from app.database import get_database_atlas
from fastapi.exceptions import HTTPException

class QueueManager:
    def __init__(self):
        self.host_uri = "mongodb+srv://doadmin:k2R0165xp4G8iV3E@host-manager-a6c7287d.mongo.ondigitalocean.com/admin?tls=true&authSource=admin"
        self.atlas_uri = "mongodb+srv://doadmin:Z79MQ4mxi5X0281G@academy-client-a3614ad3.mongo.ondigitalocean.com/admin?tls=true&authSource=admin"
        self.queue_collection = get_database_atlas("hosts", self.host_uri)["queues"]

    async def add_queue(self,data:Dict[str, Any]):
        result = await self.queue_collection.insert_one(data)
        print("add to queue succsess")
        return True
    
    def get_queue(self) :
        return True
    
    
