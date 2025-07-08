import numpy as np
from PIL import Image
import torch
import torchvision.models as models
from typing import Callable, List, Optional
import os
from enum import Enum
import torchvision.transforms as T

class DiagnosisClass(Enum):
    bkl = "Benign keratosis-like lesions"
    nv = "Melanocytic nevi"
    df = "Dermatofibroma"
    mel = "Melanoma"
    vasc = "Vascular lesions"
    bcc = "Basal cell carcinoma"
    akiec = "Actinic keratoses and intraepithelial carcinoma"

# Default constants
DEFAULT_CLASS_NAMES = [e.name for e in DiagnosisClass]
MODEL_PATH = os.path.join(os.path.dirname(__file__), "model", "densenet_pret.pth")
RESNET_MODEL_PATH = os.path.join(os.path.dirname(__file__), "model", "resnet_pret.pth")
DEFAULT_MODEL = None
DEFAULT_RESNET_MODEL = None
if os.path.exists(MODEL_PATH):
    DEFAULT_MODEL = models.densenet121(pretrained=False)
    DEFAULT_MODEL.classifier = torch.nn.Linear(DEFAULT_MODEL.classifier.in_features, len(DEFAULT_CLASS_NAMES))
    DEFAULT_MODEL.load_state_dict(torch.load(MODEL_PATH, map_location="cpu"))
    DEFAULT_MODEL = DEFAULT_MODEL.float()
    DEFAULT_MODEL.eval()
if os.path.exists(RESNET_MODEL_PATH):
    DEFAULT_RESNET_MODEL = models.resnet50(pretrained=False)
    DEFAULT_RESNET_MODEL.fc = torch.nn.Linear(DEFAULT_RESNET_MODEL.fc.in_features, len(DEFAULT_CLASS_NAMES))
    DEFAULT_RESNET_MODEL.load_state_dict(torch.load(RESNET_MODEL_PATH, map_location="cpu"))
    DEFAULT_RESNET_MODEL = DEFAULT_RESNET_MODEL.float()
    DEFAULT_RESNET_MODEL.eval()

val_test_transform = T.Compose([
    T.Resize((224, 224)),
    T.ToTensor(),
    T.Normalize([0.77148203, 0.55764165, 0.58345652], [0.12655577, 0.14245141, 0.15189891])
])

def default_preprocess(image: Image.Image) -> np.ndarray:
    tensor = val_test_transform(image.convert('RGB'))
    return tensor.unsqueeze(0).numpy()  # Add batch dimension and convert to numpy

DEFAULT_PREPROCESS = default_preprocess

def load_model(model_path: str, num_classes: int):
    model = models.densenet121(pretrained=False)
    model.classifier = torch.nn.Linear(model.classifier.in_features, num_classes)
    model.load_state_dict(torch.load(model_path, map_location="cpu"))
    model = model.float()
    model.eval()
    return model


def predict(
    image: Image.Image,
    model=DEFAULT_MODEL,
    preprocess: Callable[[Image.Image], np.ndarray] = DEFAULT_PREPROCESS,
    class_names: Optional[List[str]] = None
) -> dict:
    """
    Preprocess the image, use the provided model, and return the prediction result.
    """
    if model is None:
        raise ValueError("Model is not loaded. Please check the model path or load the model explicitly.")
    if class_names is None:
        class_names = DEFAULT_CLASS_NAMES
    processed_image = preprocess(image)
    with torch.no_grad():
        input_tensor = torch.from_numpy(processed_image).float()
        output = model(input_tensor)
        probabilities = torch.softmax(output, dim=1).cpu().numpy()[0]
        predictions = [
            {
                "class": DiagnosisClass[cls].value,
                "short_name": cls,
                "confidence": float(prob)
            }
            for cls, prob in zip(class_names, probabilities)
        ]
        top_idx = int(np.argmax(probabilities))
        top_prediction = predictions[top_idx]
        return {
            "predictions": predictions,
            "top_prediction": top_prediction
        } 