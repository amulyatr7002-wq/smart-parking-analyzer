import json
import cv2
import numpy as np


def load_slots(path):
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data.get("slots", data)


def save_slots(path, slots):
    with open(path, "w", encoding="utf-8") as f:
        json.dump({"slots": slots}, f, indent=2)


def polygon_area(points):
    return abs(cv2.contourArea(np.array(points, dtype=np.float32)))


def overlap_ratio(bbox, polygon):
    x1, y1, x2, y2 = map(int, bbox)
    if x2 <= x1 or y2 <= y1:
        return 0.0

    area = polygon_area(polygon)
    if area <= 0:
        return 0.0

    # Raster intersection in the bounding-box coordinate frame.
    shifted = []
    for x, y in polygon:
        shifted.append([
            max(0, min(x2-x1, int(x-x1))),
            max(0, min(y2-y1, int(y-y1)))
        ])

    mask = np.zeros((y2-y1+1, x2-x1+1), np.uint8)
    cv2.fillPoly(mask, [np.array(shifted, np.int32)], 255)
    return cv2.countNonZero(mask) / area


def analyze_slots(slots, detections, threshold=0.20):
    output = []
    for slot in slots:
        best = 0.0
        best_det = None
        for det in detections:
            r = overlap_ratio(det["bbox"], slot["points"])
            if r > best:
                best = r
                best_det = det
        output.append({
            "id": slot["id"],
            "points": slot["points"],
            "occupied": best >= threshold,
            "ratio": best,
            "detection": best_det,
        })
    return output


def draw_slots(frame, results):
    for r in results:
        pts = np.array(r["points"], dtype=np.int32)
        color = (0, 0, 255) if r["occupied"] else (0, 200, 0)
        cv2.polylines(frame, [pts], True, color, 2)
        center = tuple(np.mean(pts, axis=0).astype(int))
        cv2.putText(
            frame,
            f"#{r['id']} {'FULL' if r['occupied'] else 'FREE'}",
            center,
            cv2.FONT_HERSHEY_SIMPLEX,
            0.52, color, 2
        )
