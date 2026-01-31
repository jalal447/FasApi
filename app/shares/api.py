from typing import Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.shares import schemas, service
from app.documents.service import DocumentService
from app.core import dependencies
from app.users.models import User

router = APIRouter()

@router.post("/", response_model=schemas.DocumentShare)
async def share_document(
    *,
    db: AsyncSession = Depends(get_db),
    share_in: schemas.DocumentShareCreate,
    current_user: User = Depends(dependencies.get_current_user)
) -> Any:

    document = await DocumentService.get(db, id=share_in.document_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
        
    if document.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Only owners can share documents")
        

    existing = await service.ShareService.get_existing(
        db, document_id=share_in.document_id, user_id=share_in.user_id
    )
    if existing:
        raise HTTPException(status_code=400, detail="Document already shared with this user")

    return await service.ShareService.create(db, share_in=share_in)

@router.delete("/{id}")
async def unshare_document(
    *,
    db: AsyncSession = Depends(get_db),
    id: int,
    current_user: User = Depends(dependencies.get_current_user)
) -> Any:
    share = await service.ShareService.get_by_id(db, id=id)
    if not share:
        raise HTTPException(status_code=404, detail="Share record not found")
        
    document = await DocumentService.get(db, id=share.document_id)
    if document.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Only owners can revoke access")
        
    await service.ShareService.delete(db, db_obj=share)
    return {"status": "success"}
