import time
from datetime import datetime

import cv2

from src.config import OCCUPANCY_THRESHOLD, PROCESS_EVERY_N_FRAMES, PLATE_OCR_INTERVAL_SECONDS
from src.detector import VehicleDetector
from src.plate import PlateRecognizer
from src.slots import load_slots, analyze_slots, draw_slots
from src.database import (
    get_session, OccupancySnapshot, ParkingEvent, PlateRead
)


class ParkingMonitor:
    def __init__(self, camera_id, source, slots_path):
        self.camera_id = camera_id
        self.source = source
        self.slots = load_slots(slots_path)
        self.detector = VehicleDetector()
        self.plate_reader = PlateRecognizer()
        self.last_plates = {}
        self.last_slot_state = {}
        self.frame_index = 0

    def open(self):
        cap = cv2.VideoCapture(self.source)
        if not cap.isOpened():
            raise RuntimeError(f"Cannot open camera/source: {self.source}")
        return cap

    def process_frame(self, frame):
        self.frame_index += 1

        detections = self.detector.detect(frame)
        results = analyze_slots(
            self.slots, detections, OCCUPANCY_THRESHOLD
        )

        occupied = sum(r["occupied"] for r in results)
        total = len(results)
        free = total - occupied
        pct = occupied / total * 100 if total else 0

        # Persist an occupancy sample every processed frame.
        db = get_session()
        try:
            db.add(OccupancySnapshot(
                camera_id=self.camera_id,
                total_spaces=total,
                occupied_spaces=occupied,
                free_spaces=free,
                occupancy_percent=pct,
                vehicle_count=len(detections),
            ))

            # Detect slot state changes.
            for r in results:
                previous = self.last_slot_state.get(r["id"])
                current = r["occupied"]
                if previous is not None and previous != current:
                    db.add(ParkingEvent(
                        camera_id=self.camera_id,
                        slot_id=r["id"],
                        event_type="occupied" if current else "freed",
                    ))
                self.last_slot_state[r["id"]] = current

            # OCR periodically.
            now = time.time()
            if now - self.last_plates.get("_last_run", 0) >= PLATE_OCR_INTERVAL_SECONDS:
                self.last_plates["_last_run"] = now
                for d in detections[:8]:
                    read = self.plate_reader.read_vehicle(frame, d["bbox"])
                    if read:
                        text, conf = read
                        if conf >= 0.35:
                            db.add(PlateRead(
                                camera_id=self.camera_id,
                                plate_text=text,
                                confidence=conf,
                            ))

            db.commit()
        finally:
            db.close()

        # Draw result.
        draw_slots(frame, results)

        for d in detections:
            x1, y1, x2, y2 = map(int, d["bbox"])
            cv2.rectangle(frame, (x1,y1), (x2,y2), (255,180,0), 2)
            cv2.putText(
                frame,
                f"{d['name']} {d['confidence']:.2f}",
                (x1, max(20, y1-5)),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5, (255,180,0), 2
            )

        cv2.rectangle(frame, (0,0), (450,90), (25,25,25), -1)
        cv2.putText(frame, f"Spaces: {total}", (10,25),
                    cv2.FONT_HERSHEY_SIMPLEX, .6, (255,255,255), 2)
        cv2.putText(frame, f"Occupied: {occupied} | Free: {free}",
                    (10,52), cv2.FONT_HERSHEY_SIMPLEX, .6,
                    (255,255,255), 2)
        cv2.putText(frame, f"Occupancy: {pct:.1f}%",
                    (10,78), cv2.FONT_HERSHEY_SIMPLEX, .6,
                    (255,255,255), 2)

        return frame, {
            "total": total,
            "occupied": occupied,
            "free": free,
            "percent": pct,
            "vehicles": len(detections)
        }
