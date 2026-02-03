from fastapi import FastAPI
from app.core.config import settings
from app.api.router import router as api_router

app = FastAPI(title=settings.APP_NAME)

app.include_router(api_router, prefix=settings.API_V1_PREFIX)
