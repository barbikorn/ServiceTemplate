# from starlette.requests import Request

# # Create a sample Request object for demonstration
# request = Request(scope={})

# # Define a function to convert the Request to a dictionary
# def request_to_dict(request):
#     request_dict = {
#         "method": request.method,
#         "url": str(request.url),
#         "headers": dict(request.headers),
#         "query_params": dict(request.query_params),
#         "path_params": dict(request.path_params),
#     }

#     # Read and decode the request body
#     body = request.body.decode()
#     if body:
#         request_dict["body"] = body

#     return request_dict

# # Convert the Request to a dictionary
# request_dict = request_to_dict(request)

# # Print the resulting dictionary
# print(request_dict)
