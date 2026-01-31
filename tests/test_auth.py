import pytest
from httpx import AsyncClient
from app.core.config import settings

@pytest.mark.asyncio
async def test_create_user(client: AsyncClient):
    response = await client.post(
        f"{settings.API_V1_STR}/users",
        json={"email": "test@example.com", "password": "password", "full_name": "Test User"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "test@example.com"
    assert "id" in data

@pytest.mark.asyncio
async def test_login(client: AsyncClient):

    await client.post(
        f"{settings.API_V1_STR}/users",
        json={"email": "login@example.com", "password": "password", "full_name": "Login User"},
    )
    

    response = await client.post(
        f"{settings.API_V1_STR}/login/access-token",
        data={"username": "login@example.com", "password": "password"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

@pytest.mark.asyncio
async def test_read_user_me(client: AsyncClient):

    await client.post(
        f"{settings.API_V1_STR}/users",
        json={"email": "me@example.com", "password": "password", "full_name": "Me User"},
    )
    login_res = await client.post(
        f"{settings.API_V1_STR}/login/access-token",
        data={"username": "me@example.com", "password": "password"},
    )
    token = login_res.json()["access_token"]
    
    response = await client.get(
        f"{settings.API_V1_STR}/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert response.json()["email"] == "me@example.com"
