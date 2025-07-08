from fastapi import APIRouter

router = APIRouter(prefix="/diagnosis", tags=["diagnosis"])

@router.post("/")
async def pseudo_diagnose():
    """Pseudo endpoint for skin disease diagnosis (static data)."""
    return {
        "predictions": [
            {"class": "NV", "confidence": 0.82},
            {"class": "BKL", "confidence": 0.10},
            {"class": "MEL", "confidence": 0.08}
        ],
        "top_prediction": {"class": "NV", "confidence": 0.82}
    } 