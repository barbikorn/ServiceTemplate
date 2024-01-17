# ./lib/middleware/queueUtils.py
from fastapi import Request
import json
import datetime
import re
from lib.queue_manager import QueueManager
import asyncio

queueManager = QueueManager()

async def getRequestSrt(request: Request):
    request_body = await request.body()
    return request_body

def add_log_to_queue(log_info: dict):
    # Assuming queueManager is a global object or accessible within this function
    response = queueManager.add_queue(log_info)
    # You can handle the response or perform any other tasks here if needed    

def log_request_and_upload_to_queue(request: Request, collection_name: str, data_dict: dict, htoken: str):
    my_s3_bucket = 'log-server'

    timestamp = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    log_name = f"logs/log-entry-{timestamp}.json"

    log_info = {
        "method": request.method,
        "path": request.url.path,
        "collection": collection_name,
        "data": data_dict,
        "e_id": request.headers.get("id"),
        "htoken": htoken
    }

    if request.method == "POST":
        log_info["e_id"] = data_dict["id"]

    # Schedule the background task
    # background_tasks.add_task(add_log_to_queue, log_info)
    add_log_to_queue(log_info)

    return True
