
import json
import os
from fastapi import APIRouter, HTTPException, Request, Header, Query
from typing import List, Optional, Dict, Any
from bson import ObjectId
from app.models.players.player import Player,PlayerGet,PlayerCreate
from app.database import get_database_atlas
from lib.host_manager import HostDatabaseManager

router = APIRouter()

collection_name = "players"
database_manager = HostDatabaseManager(collection_name)


# Assuming you have a database_manager instance

@router.post("/", response_model=PlayerGet)
def create_player(
    request: Request,
    player_data: PlayerCreate,
    htoken: Optional[str] = Header(None)
):
    host = htoken
    collection = database_manager.get_collection(host)

    player_data_dict = player_data.dict()
    result = collection.insert_one(player_data_dict)

    if result.acknowledged:
        created_player = collection.find_one({"_id": ObjectId(result.inserted_id)})
        created_player['id'] = str(created_player['_id'])  # Add 'id' key and convert ObjectId to string
        return PlayerGet(**created_player)
    else:
        raise HTTPException(status_code=500, detail="Failed to create player")

@router.get("/", response_model=List[Dict[str, Any]])
def get_all_players(
    htoken: Optional[str] = Header(None)
):
    host = htoken
    collection = database_manager.get_collection(host)
    players = []
    for player in collection.find():
        player_id = str(player.pop('_id'))
        player["id"] = player_id
        players.append(player)
    return players

@router.get("/{player_id}", response_model=Player)
def get_player(
    request: Request,
    player_id: str,
    htoken: Optional[str] = Header(None)
):
    host = htoken
    collection = database_manager.get_collection(host)

    player = collection.find_one({"_id": player_id})
    if player:
        return Player(**player)
    else:
        raise HTTPException(status_code=404, detail="Player not found")

@router.get("/filters/", response_model=List[Player])
async def get_player_by_filter(
    request: Request,
    offset: int = 0,
    limit: int = 100,
    htoken: Optional[str] = Header(None)
) -> List[Player]:
    filter_params = await request.json()
    query = {}

    for field, value in filter_params.items():
        query[field] = value
    host = htoken
    collection = database_manager.get_collection(host)
    cursor = collection.find(query).skip(offset).limit(limit)
    players = []
    async for player in cursor:
        players.append(Player(id=str(player["_id"]), **player))
    return players

@router.put("/{player_id}", response_model=Player)
def update_player(
    request: Request,
    player_id: str,
    player_data,
    htoken: Optional[str] = Header(None)
):
    host = htoken
    collection = database_manager.get_collection(host)

    result = collection.update_one({"_id": player_id}, {"$set": player_data.dict()})
    if result.modified_count == 1:
        updated_player = collection.find_one({"_id": player_id})
        return Player(**updated_player)
    else:
        raise HTTPException(status_code=404, detail="Player not found")

@router.delete("/{player_id}")
def delete_player(
    request: Request,
    player_id: str,
    htoken: Optional[str] = Header(None)
):
    host = htoken
    collection = database_manager.get_collection(host)

    result = collection.delete_one({"_id": player_id})
    if result.deleted_count == 1:
        return {"message": "Player deleted successfully"}
    else:
        raise HTTPException(status_code=404, detail="Player not found")



