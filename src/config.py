from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "parking.db"

YOLO_MODEL = "yolo26n.pt"
CONFIDENCE = 0.30
IOU = 0.50
OCCUPANCY_THRESHOLD = 0.20
PROCESS_EVERY_N_FRAMES = 2
PLATE_OCR_INTERVAL_SECONDS = 2.0

VEHICLE_CLASS_IDS = {2, 3, 5, 7}
VEHICLE_NAMES = {
    2: "car",
    3: "motorcycle",
    5: "bus",
    7: "truck",
}

SNAPSHOT_DIR = BASE_DIR / "data" / "snapshots"
OUTPUT_DIR = BASE_DIR / "outputs"
SLOT_DIR = BASE_DIR / "data" / "slots"

SNAPSHOT_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
SLOT_DIR.mkdir(parents=True, exist_ok=True)
