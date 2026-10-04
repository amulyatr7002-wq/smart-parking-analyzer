import cv2
import numpy as np
from sklearn.cluster import DBSCAN

from src.detector import VehicleDetector
from src.slots import save_slots


def automatic_calibration(source, output_slots, frames_to_sample=40):
    """
    Creates parking-slot proposals from recurring vehicle positions.

    It is deliberately called a proposal/calibration system rather than
    claiming perfect discovery of every empty parking space.
    """
    detector = VehicleDetector()
    cap = cv2.VideoCapture(source)

    if not cap.isOpened():
        raise RuntimeError(f"Cannot open source: {source}")

    positions = []
    latest_frame = None

    total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    step = max(1, total // max(1, frames_to_sample)) if total else 5

    index = 0
    sampled = 0

    while sampled < frames_to_sample:
        ok, frame = cap.read()
        if not ok:
            break

        if index % step == 0:
            latest_frame = frame.copy()
            detections = detector.detect(frame)

            for d in detections:
                x1, y1, x2, y2 = d["bbox"]
                cx = (x1 + x2) / 2
                cy = (y1 + y2) / 2
                bw = max(20, x2 - x1)
                bh = max(20, y2 - y1)
                positions.append([cx, cy, bw, bh])
            sampled += 1

        index += 1

    cap.release()

    if latest_frame is None or not positions:
        raise RuntimeError("No vehicle detections were found during calibration.")

    X = np.array([[p[0], p[1]] for p in positions], dtype=np.float32)

    # Cluster recurring parking positions.
    # eps is adaptive to image width.
    h, w = latest_frame.shape[:2]
    eps = max(25, min(w, h) * 0.035)

    labels = DBSCAN(eps=eps, min_samples=max(2, frames_to_sample // 15)).fit_predict(X)

    slots = []
    slot_id = 1

    for label in sorted(set(labels)):
        if label == -1:
            continue

        group = np.array(
            [positions[i] for i, lab in enumerate(labels) if lab == label],
            dtype=np.float32
        )

        cx, cy, bw, bh = np.median(group, axis=0)

        # Give the proposed slot slightly more area than the median car box.
        sw = max(35, bw * 1.18)
        sh = max(35, bh * 1.25)

        pts = [
            [int(cx - sw/2), int(cy - sh/2)],
            [int(cx + sw/2), int(cy - sh/2)],
            [int(cx + sw/2), int(cy + sh/2)],
            [int(cx - sw/2), int(cy + sh/2)],
        ]

        slots.append({"id": slot_id, "points": pts, "source": "auto_calibration"})
        slot_id += 1

    save_slots(output_slots, slots)

    return slots, latest_frame
