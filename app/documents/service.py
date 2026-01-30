from typing import Any, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_, and_, func
from app.documents import models, schemas
from app.shares.models import DocumentShare, PermissionType
from datetime import datetime

class DocumentService:
    @staticmethod
    async def create(db: AsyncSession, doc_in: schemas.DocumentCreate, owner_id: int) -> models.Document:
        db_obj = models.Document(**doc_in.model_dump(), owner_id=owner_id)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    @staticmethod
    async def get(db: AsyncSession, id: int) -> Optional[models.Document]:
        result = await db.execute(select(models.Document).filter(models.Document.id == id))
        return result.scalars().first()

    @staticmethod
    async def update(db: AsyncSession, db_obj: models.Document, obj_in: schemas.DocumentUpdate) -> models.Document:
        update_data = obj_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    @staticmethod
    async def delete(db: AsyncSession, db_obj: models.Document) -> models.Document:
        await db.delete(db_obj)
        await db.commit()
        return db_obj

    @staticmethod
    async def search(
        db: AsyncSession, 
        user_id: int,
        q: Optional[str] = None,
        tags: Optional[List[str]] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        skip: int = 0,
        limit: int = 10
    ) -> Any:
        share_subquery = select(DocumentShare.document_id).filter(DocumentShare.user_id == user_id)
        query = select(models.Document).filter(
            or_(models.Document.owner_id == user_id, models.Document.id.in_(share_subquery))
        )
        
        if q:
            query = query.filter(or_(
                models.Document.title.ilike(f"%{q}%"),
                models.Document.description.ilike(f"%{q}%")
            ))
        if tags:
            for t in tags:
                query = query.filter(models.Document.tags.contains(t))
        if start_date:
            query = query.filter(models.Document.created_at >= start_date)
        if end_date:
            query = query.filter(models.Document.created_at <= end_date)
            
        count_query = select(func.count()).select_from(query.subquery())
        total = await db.scalar(count_query)
        
        result = await db.execute(query.offset(skip).limit(limit))
        items = result.scalars().all()
        return items, total
