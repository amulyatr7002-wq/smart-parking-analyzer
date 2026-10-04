import torch
from ultralytics import YOLO

from src.config import YOLO_MODEL, CONFIDENCE, IOU, VEHICLE_CLASS_IDS, VEHICLE_NAMES


class VehicleDetector:
    def __init__(self):
        self.model = YOLO(YOLO_MODEL)
        self.device = 0 if torch.cuda.is_available() else "cpu"

    def detect(self, frame):
        result = self.model.predict(
            frame,
            conf=CONFIDENCE,
            iou=IOU,
            device=self.device,
            verbose=False
        )[0]

        detections = []
        if result.boxes is None:
            return detections

        for i in range(len(result.boxes)):
            cls_id = int(result.boxes.cls[i].item())
            if cls_id not in VEHICLE_CLASS_IDS:
                continue

            detections.append({
                "bbox": result.boxes.xyxy[i].tolist(),
                "confidence": float(result.boxes.conf[i].item()),
                "class_id": cls_id,
                "name": VEHICLE_NAMES.get(cls_id, str(cls_id))
            })
        return detections
