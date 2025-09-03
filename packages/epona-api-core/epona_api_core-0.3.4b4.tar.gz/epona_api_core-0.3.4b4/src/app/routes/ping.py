from fastapi import APIRouter, Depends

from src.app.config import Settings, get_settings

router = APIRouter()


@router.get("/health-check")
async def health_check(settings: Settings = Depends(get_settings)):
    return {
        "status": "Running",
        "environment": settings.environment,
        "testing": settings.testing,
    }
