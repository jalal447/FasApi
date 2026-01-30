from sqlalchemy import String, Integer, DateTime, ForeignKey, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from app.db.session import Base
from datetime import datetime
import enum

class PermissionType(str, enum.Enum):
    READ = "read"
    WRITE = "write"

class DocumentShare(Base):
    __tablename__ = "document_share"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    document_id: Mapped[int] = mapped_column(Integer, ForeignKey("document.id"), nullable=False)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("user.id"), nullable=False)
    permission: Mapped[PermissionType] = mapped_column(String, nullable=False, default=PermissionType.READ)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    # Relationships
    document: Mapped["Document"] = relationship("Document", back_populates="shares")
    user: Mapped["User"] = relationship("User", back_populates="shares_received")
