from ultralytics import YOLO

from src.config import YOLO_MODEL, CONFIDENCE


class VehicleTracker:
    """YOLO tracking wrapper for persistent vehicle IDs."""

    def __init__(self):
        self.model = YOLO(YOLO_MODEL)

    def track(self, frame):
        results = self.model.track(
            frame,
            conf=CONFIDENCE,
            persist=True,
            tracker="bytetrack.yaml",
            verbose=False
        )
        result = results[0]
        objects = []

        if result.boxes is None:
            return objects

        for i in range(len(result.boxes)):
            cls_id = int(result.boxes.cls[i].item())
            if cls_id not in {2, 3, 5, 7}:
                continue

            track_id = None
            if result.boxes.id is not None:
                track_id = int(result.boxes.id[i].item())

            objects.append({
                "track_id": track_id,
                "bbox": result.boxes.xyxy[i].tolist(),
                "confidence": float(result.boxes.conf[i].item()),
                "class_id": cls_id,
            })
        return objects
