# "conftest.py is a special pytest configuration file used to define shared fixtures and test setup. 
# It allows multiple test files to reuse common resources such as the FastAPI test client, test database sessions, 
# dependency overrides, authentication helpers, and cleanup logic without duplicating code."


import os
from collections.abc import AsyncGenerator

os.environ["DATABASE_URL"] = (
    "postgresql+asyncpg://postgres:postgres@db:5432/test_ShopOnBot_db"
)
os.environ["AWS_S3_BUCKET_NAME"] = "test-bucket"
os.environ["SECRET_KEY"] = "test-secret-key-for-testing-only"

os.environ["S3_ACCESS_KEY_ID"] = "testing"
os.environ["S3_SECRET_ACCESS_KEY"] = "testing"
os.environ["S3_REGION"] = "ap-south-1"

os.environ["AWS_ACCESS_KEY_ID"] = "testing"
os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"
os.environ["AWS_DEFAULT_REGION"] = "ap-south-1"

import boto3
import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from app.db.database import Base, get_db
from app.main import app

pytest_plugins = ["anyio"]

@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"


@pytest.fixture(scope="session")
def test_engine():
    engine= create_async_engine(
        os.environ["DATABASE_URL"],
        poolclass=NullPool
    )
    return engine