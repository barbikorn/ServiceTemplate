# app/middlewares.py

from fastapi import Request
import json
import boto3
import datetime
import re
from app.models.queues.route import create_queue

# def upload_to_s3(bucket_name, object_key, data):
#     s3 = boto3.resource(
#     service_name='s3',
#     region_name='ap-southeast-1',
#     aws_access_key_id='DO00HB7FF7G7QZTGVJP9',
#     aws_secret_access_key='JBkywUAHF5lQzCxuGpC+A4THqUbtCtLBdzlI3JQTOmY'
# )
#     s3.put_object(Bucket=bucket_name, Key=object_key, Body=data)

def upload_to_s3(bucket_name, object_key, data):
    s3 = boto3.client(
        's3',
        region_name='ap-southeast-1',
        aws_access_key_id='DO00HB7FF7G7QZTGVJP9',
        aws_secret_access_key='JBkywUAHF5lQzCxuGpC+A4THqUbtCtLBdzlI3JQTOmY',
        endpoint_url='https://sgp1.digitaloceanspaces.com',
    )

    # Convert the JSON string to bytes
    data_bytes = data.encode('utf-8')

    s3.put_object(Bucket=bucket_name, Key=object_key, Body=data_bytes,ACL='public-read')


## WORK FOR NORMAL FUNC
def log_request_and_upload_to_s3(request: Request, collection_name: str):
    my_s3_bucket = 'log-server'

    timestamp = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    log_name = f"logs/log-entry-{timestamp}.json"

    # Decode the bytes data to a string
    request_body = request.body()
    request_body_str = request_body.decode('utf-8')

    log_info = {
        "method": request.method,
        "path": request.url.path,
        "collection": collection_name,
        "data": request_body_str,  # Use the decoded string
        "id": request.headers.get("id")
    }
    print("logINFO",log_info)
    log_entry = json.dumps(log_info)

    # Upload the log entry to S3 with the timestamp in the file name
    response = upload_to_s3(my_s3_bucket, log_name, log_entry)

    return response

# ## WORK FOR NORMAL FUNC
# async def log_request_and_upload_to_queue(request: Request, collection_name: str,data_dict:dict):
#     my_s3_bucket = 'log-server'

#     timestamp = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
#     log_name = f"logs/log-entry-{timestamp}.json"

#     # Decode the bytes data to a string
#     request_body = await request.body()
#     request_body_str = request_body.decode('utf-8')
#     print(request.method)
#     log_info = {
#         "method": request.method,
#         "path": request.url.path,
#         "collection": collection_name,
#         "data": data_dict,  # Use the decoded string
#         "e_id": request.headers.get("id")
#     }
#     if request.method == "POST" :
#         log_info["e_id"] = data_dict["id"]
#     print("logINFO",log_info)
#     log_entry = json.dumps(log_info)

#     # Upload the log entry to S3 with the timestamp in the file name
#     response = create_queue(log_info)

#     return response



# IF UNDER WORK DELETE THIS
# async def log_request_and_upload_to_s3(request: Request, call_next):
#     my_s3_bucket = "log-server"
#     print("enter middle ware")
#     response = await call_next(request)

#     timestamp = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")

#     # Use regular expression to extract the collection name from the URL path
#     path = request.url.path
#     collection_match = re.match(r"/(\w+)/", path)
#     collection_name = collection_match.group(1) if collection_match else "unknown"

#     log_name = f"logs/log-entry-{timestamp}.json"
#     print("log_name: ",log_name)
#     # Get the binary data as bytes
#     binary_data = await request.body()
#     data_str = binary_data.decode('utf-8')  # Convert bytes to string

#     log_info = {
#         "method": request.method,
#         "path": request.url.path,
#         "collection": collection_name,
#         "data": data_str,  # Use the converted string
#         "id": request.headers.get("id")
#     }
#     log_entry = json.dumps(log_info)
#     print(log_info)

#     # Upload the log entry to S3 with the timestamp in the file name
#     upload_to_s3(my_s3_bucket, log_name, log_entry)
#     print("Upload Success")
#     return response




#### TEST THIS #####
# async def log_request_and_upload_to_s3_middle(request, call_next):
#     my_s3_bucket = "log-server"
#     print("enter middleware")
    
#     # Read the request body as bytes
#     body_bytes = await request.body()
#     data_str = body_bytes.decode('utf-8')

#     response = await call_next(request)

#     timestamp = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
#     path = request.url.path
#     collection_match = re.match(r"/(\w+)/", path)
#     collection_name = collection_match.group(1) if collection_match else "unknown"

#     log_name = f"logs/log-entry-{timestamp}.json"
#     print("log_name: ", log_name)

#     log_info = {
#         "method": request.method,
#         "path": request.url.path,
#         "collection": collection_name,
#         "data": data_str,
#         "id": request.headers.get("id")
#     }
#     log_entry = json.dumps(log_info)
#     print(log_info)

#     upload_to_s3(my_s3_bucket, log_name, log_entry)
#     print("Upload Success")
#     return response
















# async def log_request_and_upload_to_s3(request: Request,collection_name : str, call_next):
#     my_s3_bucket = "your-s3-bucket"
#     response = await call_next(request)

#     timestamp = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
#     log_name = f"logs/log-entry-{timestamp}.json"

#     log_info = {
#         "method": request.method,
#         "path": request.url.path,
#         "collection": collection_name,
#         "data": await request.body(),
#         "id": request.headers.get("id")
#     }
#     log_entry = json.dumps(log_info)

#     # Upload the log entry to S3 with the timestamp in the file name
#     upload_to_s3(my_s3_bucket, log_name, log_entry)

#     return response
