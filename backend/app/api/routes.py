from fastapi import APIRouter
from app.api.endpoints import group, meetings, resources, trusted_servants

api_router = APIRouter()

api_router.include_router(group.router, prefix="/group", tags=["group"])
api_router.include_router(trusted_servants.router, prefix="/trusted-servants", tags=["trusted-servants"])
api_router.include_router(meetings.router, prefix="/meetings", tags=["meetings"])
api_router.include_router(resources.router, prefix="/resources", tags=["resources"])
