import time
import cv2
import streamlit as st

from src.database import get_session, Camera
from src.monitor import ParkingMonitor

if st.session_state.get("user") is None:
    st.warning("Please log in.")
    st.stop()

st.title("🎥 Live Parking Monitor")

db = get_session()
try:
    cameras = db.query(Camera).filter(Camera.enabled == True).all()
finally:
    db.close()

if not cameras:
    st.info("Add a camera first from the Cameras page.")
    st.stop()

labels = [f"{c.id} — {c.name}" for c in cameras]
choice = st.selectbox("Camera", labels)
camera = cameras[labels.index(choice)]

fps_limit = st.slider("Display FPS limit", 1, 30, 10)
run = st.checkbox("Start monitoring")

frame_area = st.empty()
metrics_area = st.empty()

if run:
    try:
        monitor = ParkingMonitor(
            camera.id,
            camera.source,
            camera.slots_path
        )
        cap = monitor.open()

        while run:
            ok, frame = cap.read()
            if not ok:
                st.error("Camera stream ended or could not be read.")
                break

            processed, stats = monitor.process_frame(frame)

            frame_area.image(processed, channels="BGR", use_container_width=True)

            c1, c2, c3, c4 = metrics_area.columns(4)
            c1.metric("Spaces", stats["total"])
            c2.metric("Occupied", stats["occupied"])
            c3.metric("Free", stats["free"])
            c4.metric("Occupancy", f"{stats['percent']:.1f}%")

            time.sleep(1 / fps_limit)

        cap.release()

    except Exception as e:
        st.error(str(e))
