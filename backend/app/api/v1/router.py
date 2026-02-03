from fastapi import APIRouter
from app.api.v1.routers.members import router as members_router
from app.api.v1.routers.admin import router as admin_router

router = APIRouter()
router.include_router(members_router)
router.include_router(admin_router)
