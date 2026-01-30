import pytest
from httpx import AsyncClient
from app.core.config import settings
from app.shares.models import PermissionType

async def get_token(client: AsyncClient, email: str):
    await client.post(
        f"{settings.API_V1_STR}/users",
        json={"email": email, "password": "password", "full_name": f"User {email}"},
    )
    login_res = await client.post(
        f"{settings.API_V1_STR}/login/access-token",
        data={"username": email, "password": "password"},
    )
    return login_res.json()["access_token"]

@pytest.mark.asyncio
async def test_share_document(client: AsyncClient):
    token_owner = await get_token(client, "owner@example.com")
    token_recipient = await get_token(client, "recipient@example.com")
    
    # 1. Owner creates document
    create_res = await client.post(
        f"{settings.API_V1_STR}/documents/",
        json={"title": "Shared Doc", "s3_url": "url", "tags": []},
        headers={"Authorization": f"Bearer {token_owner}"}
    )
    doc_id = create_res.json()["id"]
    
    # Get recipient user ID
    recipient_res = await client.get(
        f"{settings.API_V1_STR}/me",
        headers={"Authorization": f"Bearer {token_recipient}"}
    )
    recipient_id = recipient_res.json()["id"]
    
    # 2. Owner shares document (READ only)
    share_res = await client.post(
        f"{settings.API_V1_STR}/shares/",
        json={
            "document_id": doc_id,
            "user_id": recipient_id,
            "permission": PermissionType.READ
        },
        headers={"Authorization": f"Bearer {token_owner}"}
    )
    assert share_res.status_code == 200
    
    # 3. Recipient views document
    view_res = await client.get(
        f"{settings.API_V1_STR}/documents/{doc_id}",
        headers={"Authorization": f"Bearer {token_recipient}"}
    )
    assert view_res.status_code == 200
    assert view_res.json()["title"] == "Shared Doc"
    
    # 4. Recipient tries to update (should fail)
    update_res = await client.put(
        f"{settings.API_V1_STR}/documents/{doc_id}",
        json={"title": "Hacked Title"},
        headers={"Authorization": f"Bearer {token_recipient}"}
    )
    assert update_res.status_code == 403

@pytest.mark.asyncio
async def test_write_permission(client: AsyncClient):
    token_owner = await get_token(client, "owner2@example.com")
    token_recipient = await get_token(client, "recipient2@example.com")
    
    create_res = await client.post(
        f"{settings.API_V1_STR}/documents/",
        json={"title": "Writable Doc", "s3_url": "url", "tags": []},
        headers={"Authorization": f"Bearer {token_owner}"}
    )
    doc_id = create_res.json()["id"]
    
    recipient_res = await client.get(
        f"{settings.API_V1_STR}/me",
        headers={"Authorization": f"Bearer {token_recipient}"}
    )
    recipient_id = recipient_res.json()["id"]
    
    # Share with WRITE permission
    await client.post(
        f"{settings.API_V1_STR}/shares/",
        json={
            "document_id": doc_id,
            "user_id": recipient_id,
            "permission": PermissionType.WRITE
        },
        headers={"Authorization": f"Bearer {token_owner}"}
    )
    
    # Recipient updates document
    update_res = await client.put(
        f"{settings.API_V1_STR}/documents/{doc_id}",
        json={"title": "Updated by Recipient"},
        headers={"Authorization": f"Bearer {token_recipient}"}
    )
    assert update_res.status_code == 200
    assert update_res.json()["title"] == "Updated by Recipient"
