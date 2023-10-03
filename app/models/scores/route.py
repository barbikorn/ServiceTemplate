import json
import os
from fastapi import FastAPI,APIRouter, HTTPException, Request, Header, Query
from typing import List, Optional, Dict, Any
from bson import ObjectId
from app.models.scores.score import Score,ScoreGet,ScoreCreate
from app.database import get_database_atlas
from lib.host_manager import HostDatabaseManager
from pymongo.collection import Collection

router = APIRouter()

collection_name = "scores"
database_manager = HostDatabaseManager(collection_name)


@router.post("/", response_model=ScoreGet)
def create_score(
    request: Request,
    score_data: ScoreCreate,
    htoken: Optional[str] = Header(None)
):
    host = htoken
    collection = database_manager.get_collection(host)

    score_data_dict = score_data.dict()
    result = collection.insert_one(score_data_dict)

    if result.acknowledged:
        created_score = collection.find_one({"_id": ObjectId(result.inserted_id)})
        return Score(**created_score)
    else:
        raise HTTPException(status_code=500, detail="Failed to create score")

@router.get("/", response_model=List[Dict[str, Any]])
def get_all_scores(
    score_id: str,
    htoken: Optional[str] = Header(None)
):
    host = htoken
    collection = database_manager.get_collection(host)
    scores = []
    for score in collection.find():
        score_id = str(score.pop('_id'))
        score["id"] = score_id
        scores.append(score)
    return scores

@router.get("/{score_id}", response_model=ScoreGet)
def get_score(
    request: Request,
    score_id: str,
    htoken: Optional[str] = Header(None)
):
    host = htoken
    collection = database_manager.get_collection(host)

    score = collection.find_one({"_id": score_id})
    if score:
        return Score(**score)
    else:
        raise HTTPException(status_code=404, detail="Score not found")

@router.get("/filters/", response_model=List[Score])
async def get_score_by_filter(
    request: Request,
    offset: int = 0,
    limit: int = 100,
    htoken: Optional[str] = Header(None)
) -> List[Score]:
    filter_params = await request.json()
    query = {}

    for field, value in filter_params.items():
        query[field] = value
    host = htoken
    collection = database_manager.get_collection(host)
    cursor = collection.find(query).skip(offset).limit(limit)
    scores = []
    async for score in cursor:
        scores.append(Score(id=str(score["_id"]), **score))
    return scores

@router.put("/{score_id}", response_model=Score)
def update_score(
    request: Request,
    score_id: str,
    score_data,
    htoken: Optional[str] = Header(None)
):
    host = htoken
    collection = database_manager.get_collection(host)

    result = collection.update_one({"_id": score_id}, {"$set": score_data.dict()})
    if result.modified_count == 1:
        updated_score = collection.find_one({"_id": score_id})
        return Score(**updated_score)
    else:
        raise HTTPException(status_code=404, detail="Score not found")

@router.delete("/{score_id}")
def delete_score(
    request: Request,
    score_id: str,
    htoken: Optional[str] = Header(None)
):
    host = htoken
    collection = database_manager.get_collection(host)

    result = collection.delete_one({"_id": score_id})
    if result.deleted_count == 1:
        return {"message": "Score deleted successfully"}
    else:
        raise HTTPException(status_code=404, detail="Score not found")



