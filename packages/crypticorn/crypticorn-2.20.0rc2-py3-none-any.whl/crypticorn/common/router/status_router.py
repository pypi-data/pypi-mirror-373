"""
This module contains the status router for the API.
It provides endpoints for checking the status of the API and get the server's time.
SHOULD ALLOW ACCESS TO THIS ROUTER WITHOUT AUTH.
To enable metrics, pass enable_metrics=True and the auth_handler to the router.
>>> status_router.enable_metrics = True
>>> status_router.auth_handler = auth_handler
Then include the router in the FastAPI app.
>>> app.include_router(status_router)
"""

from datetime import datetime
from typing import Literal

from fastapi import APIRouter, Request

router = APIRouter(tags=["Status"], prefix="")


@router.get("/", operation_id="ping")
async def ping(request: Request) -> str:
    """
    Returns 'OK' if the API is running.
    """
    return "OK"


@router.get("/time", operation_id="getTime")
async def time(type: Literal["iso", "unix"] = "iso") -> str:
    """
    Returns the current time in either ISO or Unix timestamp (seconds) format.
    """
    if type == "iso":
        return datetime.now().isoformat()
    elif type == "unix":
        return str(int(datetime.now().timestamp()))
