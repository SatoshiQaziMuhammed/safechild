from fastapi import APIRouter

router = APIRouter(tags=["Health Check"])

@router.get("/", include_in_schema=False)
@router.get("/health")
def health_check():
    return {
        "message": "SafeChild Law Firm API",
        "status": "operational",
        "version": "1.0.0"
    }
