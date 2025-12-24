import pytest
import pytest_asyncio
from typing import AsyncGenerator
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.db.database import get_db, Base
from app.core.security import create_access_token


TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

engine = create_async_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    echo=False,
)

TestingSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

@pytest_asyncio.fixture(scope="function")
async def db() -> AsyncGenerator[AsyncSession, None]:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async with TestingSessionLocal() as session:
        yield session
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest_asyncio.fixture(scope="function")
async def client(db: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    async def override_get_db():
        yield db

    app.dependency_overrides[get_db] = override_get_db
    
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        yield c
    
    app.dependency_overrides.clear()

@pytest_asyncio.fixture
async def token(client: AsyncClient):
    """
    Фикстура создает тестового пользователя и возвращает JWT токен.
    """
    
    test_user = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "TestPass123"
    }
    
    
    register_response = await client.post(
        "/api/v1/auth/register",
        json=test_user
    )
    
    
    assert register_response.status_code in [200, 201], \
        f"Registration failed: {register_response.text}"
    
    
    login_data = {
        "username": test_user["username"],
        "password": test_user["password"]
    }
    
    
    try:
        
        login_response = await client.post(
            "/api/v1/auth/login",
            data=login_data
        )
    except:
        
        login_response = await client.post(
            "/api/v1/auth/login",
            json=login_data
        )
    
    
    assert login_response.status_code == 200, \
        f"Login failed: {login_response.text}"
    
    
    token_data = login_response.json()
    
    
    assert "access_token" in token_data, \
        f"No access_token in response: {token_data}"
    
    
    return f"Bearer {token_data['access_token']}"
