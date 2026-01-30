from datetime import datetime
from typing import Any, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from app.db.session import get_db
from app.documents import schemas, service
from app.core import dependencies
from app.users.models import User
from app.shares.models import DocumentShare, PermissionType

router = APIRouter()

@router.post("/", response_model=schemas.Document)
async def create_document(
    *,
    db: AsyncSession = Depends(get_db),
    document_in: schemas.DocumentCreate,
    current_user: User = Depends(dependencies.get_current_user)
) -> Any:
    return await service.DocumentService.create(db, doc_in=document_in, owner_id=current_user.id)

@router.get("/{id}", response_model=schemas.Document)
async def read_document(
    *,
    db: AsyncSession = Depends(get_db),
    id: int,
    current_user: User = Depends(dependencies.get_current_user)
) -> Any:
    document = await service.DocumentService.get(db, id=id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    if document.owner_id == current_user.id:
        return document
        
    share_query = select(DocumentShare).filter(
        and_(DocumentShare.document_id == id, DocumentShare.user_id == current_user.id)
    )
    share_result = await db.execute(share_query)
    if share_result.scalars().first():
        return document
        
    raise HTTPException(status_code=403, detail="Not enough permissions")

@router.put("/{id}", response_model=schemas.Document)
async def update_document(
    *,
    db: AsyncSession = Depends(get_db),
    id: int,
    document_in: schemas.DocumentUpdate,
    current_user: User = Depends(dependencies.get_current_user)
) -> Any:
    document = await service.DocumentService.get(db, id=id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
        
    if document.owner_id != current_user.id:
        share_query = select(DocumentShare).filter(
            and_(
                DocumentShare.document_id == id, 
                DocumentShare.user_id == current_user.id,
                DocumentShare.permission == PermissionType.WRITE
            )
        )
        share_result = await db.execute(share_query)
        if not share_result.scalars().first():
            raise HTTPException(status_code=403, detail="Not enough permissions")

    return await service.DocumentService.update(db, db_obj=document, obj_in=document_in)

@router.delete("/{id}", response_model=schemas.Document)
async def delete_document(
    *,
    db: AsyncSession = Depends(get_db),
    id: int,
    current_user: User = Depends(dependencies.get_current_user)
) -> Any:
    document = await service.DocumentService.get(db, id=id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    if document.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Only owners can delete documents")
        
    return await service.DocumentService.delete(db, db_obj=document)

@router.get("/search/", response_model=schemas.DocumentSearchResults)
async def search_documents(
    *,
    db: AsyncSession = Depends(get_db),
    q: Optional[str] = Query(None),
    tag: Optional[List[str]] = Query(None),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    skip: int = 0,
    limit: int = 10,
    current_user: User = Depends(dependencies.get_current_user)
) -> Any:
    items, total = await service.DocumentService.search(
        db, user_id=current_user.id, q=q, tags=tag, 
        start_date=start_date, end_date=end_date, skip=skip, limit=limit
    )
    return {"items": items, "total": total}
