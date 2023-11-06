import os
import json
from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
from pydantic import BaseModel
import uuid

servers = [
    {"url": "http://127.0.0.1:8000"},
]

app = FastAPI(openapi_extra={"servers": servers})
internal = "internal"
random = str(uuid.uuid4())

# Define a Pydantic model for payload validation
class HelloRequest(BaseModel):
    entity: str

# GET request handler
@app.get("/internal", tags=[])
async def read_hello():
    return {"message": "This is internal Endpoint"}

# GET request handler
@app.get("/hello", tags=[random])
async def read_hello():
    return {"message": "Hello World"}

# POST request handler with payload validation
@app.post("/hello")
async def create_hello(request_data: HelloRequest):
    return {"message": f"Hello {request_data.entity}"}

# GET request handler for generating random UUID
@app.get("/uuid")
async def generate_uuid():
    random_uuid = str(uuid.uuid4())  # Generate a random UUID
    return {"uuid": random_uuid}

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    app.openapi_schema = get_openapi(
        title="Hello World API",
        openapi_version="3.0.3",
        version="1.0.0",
        routes=app.routes,
    )

    filtered_routes = {}

    for path, path_info in app.openapi_schema["paths"].items():
        filtered_routes[path] = {}
        for method, method_info in path_info.items():
            route = method_info
            tags = [tag.lower() for tag in method_info.get("tags", [])]
            if "internal" not in tags:
                filtered_routes[path][method] = route

    # Remove empty paths
    filtered_routes = {path: methods for path, methods in filtered_routes.items() if methods}

    # Replace paths in app.openapi_schema with filtered_routes
    app.openapi_schema["paths"] = filtered_routes
    app.openapi_schema["servers"] = servers

    return app.openapi_schema

app.openapi = custom_openapi

def generate_openapi_json():
    openapi_schema = app.openapi()
    with open("../oas/my-api.oas.json", "w") as file:
        json.dump(openapi_schema, file, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    generate_openapi_json()