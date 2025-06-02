import asyncio
import os
from datetime import timedelta
from typing import Any
from typing import AsyncGenerator

import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine
from starlette.testclient import TestClient

import settings
from db.session import get_db
from main import app
from security import create_access_token

CLEAN_TABLES = [
    "users",
]


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session", autouse=True)
async def run_migrations():
    if not os.path.exists(r"tests\migrations"):
        os.system("alembic init migrations")
    # os.system('alembic -c tests/alembic.ini revision --autogenerate -m "added column password"')
    # os.system("alembic -c tests/alembic.ini upgrade head")


@pytest.fixture(scope="session")
async def async_session_test():
    engine = create_async_engine(settings.TEST_DATABASE_URL, future=True, echo=False)
    async_session = async_sessionmaker(engine, expire_on_commit=False)
    yield async_session


@pytest.fixture(scope="function", autouse=True)
async def clean_tables(async_session_test):
    """Clean data in all tables before running test function"""
    async with async_session_test() as session:
        async with session.begin():
            for table_for_cleaning in CLEAN_TABLES:
                await session.execute(text(f"""TRUNCATE TABLE {table_for_cleaning};"""))


async def _get_test_db():
    try:
        # create async engine for interaction with database
        test_engine = create_async_engine(
            settings.TEST_DATABASE_URL, future=True, echo=False
        )

        # create session for the interaction with database
        test_async_session = async_sessionmaker(test_engine, expire_on_commit=False)
        yield test_async_session()
    finally:
        pass


@pytest.fixture(scope="function")
async def client() -> AsyncGenerator[TestClient, Any]:
    """
    Create a new FastAPI TestClient that uses the `db_session` fixture to override
    the `get_db` dependency that is injected into routes.
    """
    app.dependency_overrides[get_db] = _get_test_db
    with TestClient(app) as client:
        yield client


@pytest.fixture(scope="function")
async def get_user_from_database(async_session_test):
    async def get_user_from_database_by_uuid(user_id: str):
        async with async_session_test() as session:
            async with session.begin():
                res = await session.execute(
                    text("""SELECT * FROM users WHERE user_id = :user_id"""),
                    {"user_id": user_id},
                )
                return res.mappings().all()

    return get_user_from_database_by_uuid


@pytest.fixture(scope="function")
async def create_user_in_database(async_session_test):
    async def create_user_in_database(
        user_id: str,
        name: str,
        surname: str,
        email: str,
        is_active: bool,
        hashed_password: str,
        # roles: list[PortalRole],
    ):
        async with async_session_test() as session:
            async with session.begin():
                return await session.execute(
                    text(
                        """INSERT INTO users (user_id, name, surname, email, is_active, hashed_password)
                            VALUES (:user_id, :name, :surname, :email, :is_active, :hashed_password)"""
                    ),
                    {
                        "user_id": user_id,
                        "name": name,
                        "surname": surname,
                        "email": email,
                        "is_active": is_active,
                        "hashed_password": hashed_password,
                    },
                )

    return create_user_in_database


def create_test_auth_headers_for_user(email: str) -> dict[str, str]:
    access_token = create_access_token(
        data={"sub": email},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    return {"Authorization": f"Bearer {access_token}"}
