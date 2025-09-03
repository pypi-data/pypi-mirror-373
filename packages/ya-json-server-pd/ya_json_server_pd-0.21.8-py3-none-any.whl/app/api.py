from fastapi import FastAPI

from app.handlers.exceptions import APIException, api_exception_handler
from app.views.routes import router

description = """A REST API for JSON content with zero coding.

Technologies::
* Python 3.13
* FastAPI 0.116
"""
app = FastAPI(
    title="Yet Another JSON Server",
    description=description,
    version="1.0.1",
    openapi_tags=[{"name": "API"}],
)

app.add_exception_handler(APIException, api_exception_handler)
app.add_exception_handler(FileNotFoundError, api_exception_handler)
app.add_exception_handler(Exception, api_exception_handler)

app.include_router(router)
