import streamlit as st
from src.database import get_session, Camera

if st.session_state.get("user") is None:
    st.warning("Please log in.")
    st.stop()

st.title("📹 Camera Management")

with st.form("add_camera"):
    name = st.text_input("Camera name", "Main Parking Camera")
    source = st.text_input(
        "Source",
        "0",
        help="Use 0 for webcam, a video path, or an RTSP URL."
    )
    slots_path = st.text_input(
        "Slots JSON path",
        "data/slots/slots.json"
    )
    add = st.form_submit_button("Add camera")

if add:
    db = get_session()
    try:
        db.add(Camera(name=name, source=source, slots_path=slots_path))
        db.commit()
        st.success("Camera added.")
    finally:
        db.close()

db = get_session()
try:
    cams = db.query(Camera).order_by(Camera.id.desc()).all()
    for cam in cams:
        st.markdown(f"### {cam.name}")
        st.write(f"Source: `{cam.source}`")
        st.write(f"Slots: `{cam.slots_path}`")
        st.write(f"Enabled: `{cam.enabled}`")
finally:
    db.close()
