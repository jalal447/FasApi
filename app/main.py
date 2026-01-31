from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.middleware import LoggingMiddleware
from app.users.api import router as user_router
from app.documents.api import router as document_router
from app.shares.api import router as share_router


app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.add_middleware(LoggingMiddleware)


app.include_router(
    user_router, 
    prefix=settings.API_V1_STR, 
    tags=["Authentication & Users"],
)
app.include_router(
    document_router, 
    prefix=f"{settings.API_V1_STR}/documents", 
    tags=["Document Management"],
)
app.include_router(
    share_router, 
    prefix=f"{settings.API_V1_STR}/shares", 
    tags=["Sharing & Permissions"],
)


@app.get("/")
async def root():
    return {"message": "Welcome to the Document Management API", "docs": "/docs"}
