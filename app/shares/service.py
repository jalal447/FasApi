from typing import Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from app.shares import models, schemas

class ShareService:
    @staticmethod
    async def get_by_id(db: AsyncSession, id: int) -> Optional[models.DocumentShare]:
        result = await db.execute(select(models.DocumentShare).filter(models.DocumentShare.id == id))
        return result.scalars().first()

    @staticmethod
    async def get_existing(db: AsyncSession, document_id: int, user_id: int) -> Optional[models.DocumentShare]:
        query = select(models.DocumentShare).filter(
            and_(
                models.DocumentShare.document_id == document_id,
                models.DocumentShare.user_id == user_id
            )
        )
        result = await db.execute(query)
        return result.scalars().first()

    @staticmethod
    async def create(db: AsyncSession, share_in: schemas.DocumentShareCreate) -> models.DocumentShare:
        db_obj = models.DocumentShare(**share_in.model_dump())
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    @staticmethod
    async def delete(db: AsyncSession, db_obj: models.DocumentShare) -> None:
        await db.delete(db_obj)
        await db.commit()
