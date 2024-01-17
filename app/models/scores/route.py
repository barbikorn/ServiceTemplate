import json
import os
from fastapi import FastAPI,APIRouter, HTTPException, Request, Header, BackgroundTasks
from typing import List, Optional, Dict, Any
from bson import ObjectId
from app.models.scores.score import Score,ScoreGet,ScoreCreate,ScoreUpdate
from app.database import get_database_atlas
from lib.host_manager import HostDatabaseManager
from pymongo.collection import Collection

from lib.middleware.queueLog import log_request_and_upload_to_queue

router = APIRouter()

collection_name = "scores"
database_manager = HostDatabaseManager(collection_name)


@router.post("/", response_model=ScoreGet)
async def create_score(
    request: Request,
    score_data: ScoreCreate,
    background_tasks: BackgroundTasks,
    htoken: Optional[str] = Header(None)
):
    
    host = htoken
    collection = await database_manager.get_collection(host)

    score_data_dict = score_data.dict()
    result = collection.insert_one(score_data_dict)

    if result.acknowledged:

        created_score = score_data_dict  # Start with the score data provided
        created_score['id'] = str(result.inserted_id)  # Add 'id' key and convert ObjectId to string
        background_tasks.add_task(
            log_request_and_upload_to_queue,
            request, collection_name, created_score, htoken, background_tasks
        )
        return ScoreGet(**created_score)
    else:
        raise HTTPException(status_code=500, detail="Failed to create score")

@router.get("/", response_model=List[Dict[str, Any]])
def get_all_scores(
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
@router.put("/{score_id}", response_model=ScoreGet)
async def update_score(
    request: Request,
    score_id: str,
    score_data: ScoreUpdate,
    background_tasks: BackgroundTasks,
    htoken: Optional[str] = Header(None)
):
    host = htoken
    collection = await database_manager.get_collection(host)
    result = collection.update_one({"_id": ObjectId(score_id)}, {"$set": score_data.dict()})

    if result.modified_count == 1:
        updated_score = collection.find_one({"_id": ObjectId(score_id)})

        # Use background task to log the update
        background_tasks.add_task(
            log_request_and_upload_to_queue,
            request, collection_name, updated_score, htoken
        )

        return ScoreGet(**updated_score)
    else:
        raise HTTPException(status_code=404, detail="Nothing change")

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



