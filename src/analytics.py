import pandas as pd
from sqlalchemy import func
from src.database import get_session, OccupancySnapshot, ParkingEvent, PlateRead


def occupancy_dataframe(camera_id=None, limit=10000):
    db = get_session()
    try:
        q = db.query(OccupancySnapshot).order_by(
            OccupancySnapshot.created_at.asc()
        )
        if camera_id is not None:
            q = q.filter(OccupancySnapshot.camera_id == camera_id)
        rows = q.limit(limit).all()

        return pd.DataFrame([{
            "time": r.created_at,
            "camera_id": r.camera_id,
            "total_spaces": r.total_spaces,
            "occupied_spaces": r.occupied_spaces,
            "free_spaces": r.free_spaces,
            "occupancy_percent": r.occupancy_percent,
            "vehicle_count": r.vehicle_count,
        } for r in rows])
    finally:
        db.close()


def events_dataframe(camera_id=None, limit=5000):
    db = get_session()
    try:
        q = db.query(ParkingEvent).order_by(ParkingEvent.created_at.desc())
        if camera_id is not None:
            q = q.filter(ParkingEvent.camera_id == camera_id)
        rows = q.limit(limit).all()

        return pd.DataFrame([{
            "time": r.created_at,
            "camera_id": r.camera_id,
            "slot_id": r.slot_id,
            "event": r.event_type,
            "plate": r.plate,
            "confidence": r.confidence,
        } for r in rows])
    finally:
        db.close()


def plates_dataframe(camera_id=None, limit=5000):
    db = get_session()
    try:
        q = db.query(PlateRead).order_by(PlateRead.created_at.desc())
        if camera_id is not None:
            q = q.filter(PlateRead.camera_id == camera_id)
        rows = q.limit(limit).all()

        return pd.DataFrame([{
            "time": r.created_at,
            "camera_id": r.camera_id,
            "plate": r.plate_text,
            "confidence": r.confidence,
        } for r in rows])
    finally:
        db.close()
