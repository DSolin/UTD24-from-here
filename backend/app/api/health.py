from fastapi import APIRouter
router = APIRouter(prefix="/health", tags=["Health"])

@router.get("")
async def health_check():
    return {"status": "ok", "service": "UTD from here", "version": "0.1.0"}

@router.get("/db")
async def db_health_check():
    return {"status": "ok", "database": "connected"}
