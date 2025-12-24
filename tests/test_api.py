import pytest
from httpx import AsyncClient
from app.schemas.chat import ChatSession

@pytest.mark.asyncio
async def test_register(client: AsyncClient):
    response = await client.post("/api/v1/auth/register", json={
        "username": "newuser",
        "email": "new@example.com",
        "password": "123"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "newuser"
    assert "id" in data

@pytest.mark.asyncio
async def test_login(client: AsyncClient):
    await client.post("/api/v1/auth/register", json={
        "username": "loginuser",
        "password": "123"
    })
    
    response = await client.post("/api/v1/auth/login", data={
        "username": "loginuser",
        "password": "123"
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

@pytest.mark.asyncio
async def test_create_session(client: AsyncClient, token: str):
    response = await client.post(
        "/api/v1/chat/sessions",
        headers={"Authorization": token}
    )
    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert data["user_id"] is not None

@pytest.mark.asyncio
async def test_get_history(client: AsyncClient, token: str):
    session_res = await client.post(
        "/api/v1/chat/sessions",
        headers={"Authorization": token}
    )
    session_id = session_res.json()["id"]
    
    response = await client.get(
        f"/api/v1/chat/sessions/{session_id}",
        headers={"Authorization": token}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == session_id
    assert data["messages"] == []

