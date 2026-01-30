from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class DocumentBase(BaseModel):
    title: str
    description: Optional[str] = None
    tags: Optional[List[str]] = None
    s3_url: str

class DocumentCreate(DocumentBase):
    pass

class DocumentUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    tags: Optional[List[str]] = None
    s3_url: Optional[str] = None

class Document(DocumentBase):
    id: int
    owner_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class DocumentSearchResults(BaseModel):
    items: List[Document]
    total: int
