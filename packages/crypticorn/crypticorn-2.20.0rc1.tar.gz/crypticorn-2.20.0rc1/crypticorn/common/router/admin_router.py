"""
This module contains the admin router for the API.
It provides endpoints for monitoring the server and getting information about the environment.
ONLY ALLOW ACCESS TO THIS ROUTER WITH ADMIN SCOPES.
>>> app.include_router(admin_router, dependencies=[Security(auth_handler.full_auth, scopes=[Scope.READ_ADMIN, Scope.WRITE_ADMIN])])
"""

import importlib.metadata
import logging
import os
import re
import threading
import time
from typing import Literal

import psutil
from fastapi import APIRouter, Query, Response
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest

from crypticorn.common.logging import LogLevel

router = APIRouter(tags=["Admin"], prefix="/admin")

START_TIME = time.time()


@router.get("/log-level", status_code=200, operation_id="getLogLevel", deprecated=True)
async def get_logging_level() -> LogLevel:
    """
    Get the log level of the server logger. Will be removed in a future release.
    """
    return LogLevel.get_name(logging.getLogger().level)


@router.get("/uptime", operation_id="getUptime", status_code=200)
def get_uptime(type: Literal["seconds", "human"] = "seconds") -> str:
    """Return the server uptime in seconds or human-readable form."""
    uptime_seconds = int(time.time() - START_TIME)
    if type == "seconds":
        return str(uptime_seconds)
    elif type == "human":
        return time.strftime("%H:%M:%S", time.gmtime(uptime_seconds))


@router.get("/memory", operation_id="getMemoryUsage", status_code=200)
def get_memory_usage() -> float:
    """
    Resident Set Size (RSS) in MB — the actual memory used by the process in RAM.
    Represents the physical memory footprint. Important for monitoring real usage.
    """
    process = psutil.Process(os.getpid())
    mem_info = process.memory_info()
    return round(mem_info.rss / (1024 * 1024), 2)


@router.get("/threads", operation_id="getThreads", status_code=200)
def get_threads() -> dict:
    """Return count and names of active threads."""
    threads = threading.enumerate()
    return {
        "count": len(threads),
        "threads": [t.name for t in threads],
    }


@router.get("/limits", operation_id="getContainerLimits", status_code=200)
def get_container_limits() -> dict:
    """Return container resource limits from cgroup."""
    limits = {}
    try:
        with open("/sys/fs/cgroup/memory/memory.limit_in_bytes") as f:
            limits["memory_limit_MB"] = int(f.read().strip()) / 1024 / 1024
    except Exception:
        limits["memory_limit_MB"] = "N/A"

    try:
        with (
            open("/sys/fs/cgroup/cpu/cpu.cfs_quota_us") as f1,
            open("/sys/fs/cgroup/cpu/cpu.cfs_period_us") as f2,
        ):
            quota = int(f1.read().strip())
            period = int(f2.read().strip())
            limits["cpu_limit_cores"] = quota / period if quota > 0 else "N/A"
    except Exception:
        limits["cpu_limit_cores"] = "N/A"

    return limits


@router.get("/dependencies", operation_id="getDependencies", status_code=200)
def list_installed_packages(
    include: list[str] = Query(
        default=None,
        description="List of regex patterns to match against package names. If not provided, all installed packages will be returned.",
    )
) -> dict[str, str]:
    """Return a list of installed packages and versions.

    The include parameter accepts regex patterns to match against package names.
    For example:
    - crypticorn.* will match all packages starting with 'crypticorn'
    - .*tic.* will match all packages containing 'tic' in their name
    """
    packages = {
        dist.metadata["Name"]: dist.version
        for dist in importlib.metadata.distributions()
        if include is None
        or any(re.match(pattern, dist.metadata["Name"]) for pattern in include)
    }
    return dict(sorted(packages.items()))


@router.get("/metrics", operation_id="getMetrics")
def metrics():
    """
    Get Prometheus metrics for the application. Returns plain text.
    """
    return Response(generate_latest(registry), media_type=CONTENT_TYPE_LATEST)
