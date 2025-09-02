import warnings
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from typing_extensions import deprecated

from crypticorn.common.logging import configure_logging
from crypticorn.common.warnings import CrypticornDeprecatedSince217


@deprecated("Use add_middleware instead", category=None)
def add_cors_middleware(app: "FastAPI"):
    warnings.warn(
        "add_cors_middleware is deprecated. Use add_middleware instead.",
        CrypticornDeprecatedSince217,
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:5173",  # vite dev server
            "http://localhost:4173",  # vite preview server
        ],
        allow_origin_regex="^https://([a-zA-Z0-9-]+.)*crypticorn.(dev|com)/?$",  # matches (multiple or no) subdomains of crypticorn.dev and crypticorn.com
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


def add_middleware(app: "FastAPI"):
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:5173",  # vite dev server
            "http://localhost:4173",  # vite preview server
        ],
        allow_origin_regex="^https://([a-zA-Z0-9-]+.)*crypticorn.(dev|com)/?$",  # matches (multiple or no) subdomains of crypticorn.dev and crypticorn.com
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


@asynccontextmanager
async def default_lifespan(app: FastAPI):
    """Default lifespan for the applications.
    This is used to configure the logging for the application.
    To override this, pass a different lifespan to the FastAPI constructor or call this lifespan within a custom lifespan.
    """
    configure_logging()
    yield
