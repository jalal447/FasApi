from pydantic import BaseModel
from app.shares.models import PermissionType
from datetime import datetime

class DocumentShareBase(BaseModel):
    document_id: int
    user_id: int
    permission: PermissionType = PermissionType.READ

class DocumentShareCreate(DocumentShareBase):
    pass

class DocumentShareUpdate(BaseModel):
    permission: PermissionType

class DocumentShare(DocumentShareBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
