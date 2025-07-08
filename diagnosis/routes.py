from fastapi import APIRouter, UploadFile, File, Query, HTTPException
from PIL import Image
import io
from diagnosis.services import predict, DiagnosisClass, DEFAULT_MODEL, DEFAULT_RESNET_MODEL

router = APIRouter(prefix="/diagnosis", tags=["diagnosis"])

@router.post("/")
async def diagnose(
    file: UploadFile = File(...),
    model_type: str = Query("densenet", enum=["densenet", "resnet"], description="Choose which model to use: densenet or resnet.")
):
    try:
        contents = await file.read()
        image = Image.open(io.BytesIO(contents)).convert("RGB")
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid image file")
    if model_type == "densenet":
        model = DEFAULT_MODEL
        if model is None:
            raise HTTPException(status_code=500, detail="DenseNet model not available.")
    else:
        model = DEFAULT_RESNET_MODEL
        if model is None:
            raise HTTPException(status_code=500, detail="ResNet model not available.")
    result = predict(image, model=model)
    return result 