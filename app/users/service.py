from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core import security
from app.users import models, schemas

class UserService:
    @staticmethod
    async def get_by_email(db: AsyncSession, email: str) -> Optional[models.User]:
        result = await db.execute(select(models.User).filter(models.User.email == email))
        return result.scalars().first()

    @staticmethod
    async def get_by_id(db: AsyncSession, user_id: int) -> Optional[models.User]:
        result = await db.execute(select(models.User).filter(models.User.id == user_id))
        return result.scalars().first()

    @staticmethod
    async def create(db: AsyncSession, user_in: schemas.UserCreate) -> models.User:
        db_obj = models.User(
            email=user_in.email,
            hashed_password=security.get_password_hash(user_in.password),
            full_name=user_in.full_name,
        )
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    @staticmethod
    async def authenticate(db: AsyncSession, email: str, password: str) -> Optional[models.User]:
        user = await UserService.get_by_email(db, email)
        if not user:
            return None
        if not security.verify_password(password, user.hashed_password):
            return None
        return user
