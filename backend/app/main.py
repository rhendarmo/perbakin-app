from fastapi import FastAPI
from app.core.config import settings
from app.api.router import router as api_router

app = FastAPI(title=settings.APP_NAME)

# API router already mounts /v1 inside it, so here we mount only /api
app.include_router(api_router, prefix="/api")
