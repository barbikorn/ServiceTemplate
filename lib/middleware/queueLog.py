# app/middlewares.py

from fastapi import Request,BackgroundTasks
import json
import boto3
import datetime
import re
from app.models.queues.route import create_queue
from lib.queue_manager import QueueManager
import asyncio

# def upload_to_s3(bucket_name, object_key, data):
#     s3 = boto3.resource(
#     service_name='s3',
#     region_name='ap-southeast-1',
#     aws_access_key_id='DO00HB7FF7G7QZTGVJP9',
#     aws_secret_access_key='JBkywUAHF5lQzCxuGpC+A4THqUbtCtLBdzlI3JQTOmY'
# )
#     s3.put_object(Bucket=bucket_name, Key=object_key, Body=data)

queueManager = QueueManager()
# ## WORK FOR NORMAL FUNC
# async def log_request_and_upload_to_queue(
#         request : Request, 
#         collection_name : str,
#         data_dict : dict,
#         htoken : str
#         ):
#     my_s3_bucket = 'log-server'

#     timestamp = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
#     log_name = f"logs/log-entry-{timestamp}.json"

#     # Decode the bytes data to a string
#     request_body = await request.body()
#     request_body_str = request_body.decode('utf-8')
#     print(request_body)
#     # print(request.method)
#     log_info = {
#         "method": request.method,
#         "path": request.url.path,
#         "collection": collection_name,
#         "data": data_dict,  # Use the decoded string
#         "e_id": request.headers.get("id"),
#         "htoken" : htoken
#     }
#     if request.method == "POST" :
#         log_info["e_id"] = data_dict["id"]
#     print("logINFO",log_info)
#     # log_entry = json.dumps(log_info)

#     # Upload the log entry to S3 with the timestamp in the file name
#     response =  queueManager.add_queue(log_info)
#     return True

# async def run_log_request_and_upload_to_queue(
#     request: Request,
#     collection_name: str,
#     created_user: dict,
#     htoken: str
# ):
#     loop = asyncio.get_event_loop()
#     await loop.run_in_executor(None, lambda: asyncio.run(log_request_and_upload_to_queue(request, collection_name, created_user, htoken)))



# ลองตัวใหม่
    
def log_request_and_upload_to_queue(
    request: Request,
    collection_name: str,
    data_dict: dict,
    htoken: str,
    background_tasks: BackgroundTasks
):
    my_s3_bucket = 'log-server'

    timestamp = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    log_name = f"logs/log-entry-{timestamp}.json"

    # Decode the bytes data to a string
    # request_body = await request.body()
    # request_body_str = request_body.decode('utf-8')
    
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
    background_tasks.add_task(add_log_to_queue, log_info)

    return True

def add_log_to_queue(log_info: dict):
    # Assuming queueManager is a global object or accessible within this function
    response = queueManager.add_queue(log_info)
    # You can handle the response or perform any other tasks here if needed


async def getRequestSrt(
    request: Request,
):
    request_body = await request.body()
    return request_body

