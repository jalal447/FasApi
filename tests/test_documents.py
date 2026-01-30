import pytest
from httpx import AsyncClient
from app.core.config import settings

@pytest.fixture
async def auth_header(client: AsyncClient):
    # Create user
    await client.post(
        f"{settings.API_V1_STR}/users",
        json={"email": "doc@example.com", "password": "password", "full_name": "Doc User"},
    )
    # Login
    login_res = await client.post(
        f"{settings.API_V1_STR}/login/access-token",
        data={"username": "doc@example.com", "password": "password"},
    )
    token = login_res.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

@pytest.mark.asyncio
async def test_create_document(client: AsyncClient, auth_header: dict):
    response = await client.post(
        f"{settings.API_V1_STR}/documents/",
        json={
            "title": "My Test Document",
            "description": "A document for testing",
            "tags": ["test", "fastapi"],
            "s3_url": "https://s3.amazonaws.com/bucket/doc.pdf"
        },
        headers=auth_header
    )
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "My Test Document"
    assert data["tags"] == ["test", "fastapi"]

@pytest.mark.asyncio
async def test_get_document(client: AsyncClient, auth_header: dict):
    # Create first
    create_res = await client.post(
        f"{settings.API_V1_STR}/documents/",
        json={"title": "Get Test", "s3_url": "url", "tags": []},
        headers=auth_header
    )
    doc_id = create_res.json()["id"]
    
    response = await client.get(
        f"{settings.API_V1_STR}/documents/{doc_id}",
        headers=auth_header
    )
    assert response.status_code == 200
    assert response.json()["title"] == "Get Test"

@pytest.mark.asyncio
async def test_update_document(client: AsyncClient, auth_header: dict):
    create_res = await client.post(
        f"{settings.API_V1_STR}/documents/",
        json={"title": "Old Title", "s3_url": "url", "tags": []},
        headers=auth_header
    )
    doc_id = create_res.json()["id"]
    
    response = await client.put(
        f"{settings.API_V1_STR}/documents/{doc_id}",
        json={"title": "New Title"},
        headers=auth_header
    )
    assert response.status_code == 200
    assert response.json()["title"] == "New Title"

@pytest.mark.asyncio
async def test_search_documents(client: AsyncClient, auth_header: dict):
    await client.post(
        f"{settings.API_V1_STR}/documents/",
        json={"title": "Searchable Doc", "s3_url": "url", "tags": ["search"]},
        headers=auth_header
    )
    
    response = await client.get(
        f"{settings.API_V1_STR}/documents/search/?q=Searchable",
        headers=auth_header
    )
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 1
    assert data["items"][0]["title"] == "Searchable Doc"

@pytest.mark.asyncio
async def test_delete_document(client: AsyncClient, auth_header: dict):
    create_res = await client.post(
        f"{settings.API_V1_STR}/documents/",
        json={"title": "To Delete", "s3_url": "url", "tags": []},
        headers=auth_header
    )
    doc_id = create_res.json()["id"]
    
    response = await client.delete(
        f"{settings.API_V1_STR}/documents/{doc_id}",
        headers=auth_header
    )
    assert response.status_code == 200
    
    # Verify deleted
    get_res = await client.get(
        f"{settings.API_V1_STR}/documents/{doc_id}",
        headers=auth_header
    )
    assert get_res.status_code == 404
