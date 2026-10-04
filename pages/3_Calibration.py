import streamlit as st
from pathlib import Path

from src.calibration import automatic_calibration
from src.slots import load_slots, save_slots

if st.session_state.get("user") is None:
    st.warning("Please log in.")
    st.stop()

st.title("🎯 Automatic Parking-Slot Calibration")

st.warning(
    "Automatic calibration proposes slots from recurring vehicle positions. "
    "Always review the generated polygons before relying on them."
)

source = st.text_input(
    "Camera/video source",
    "data/videos/parking.mp4"
)
output = st.text_input(
    "Output slots JSON",
    "data/slots/slots.json"
)
frames = st.slider("Calibration samples", 10, 150, 40)

if st.button("Run Automatic Calibration", type="primary"):
    try:
        with st.spinner("Sampling source and clustering parking positions..."):
            slots, frame = automatic_calibration(
                source, output, frames
            )

        st.success(f"Created {len(slots)} parking-slot proposals.")
        st.image(frame, channels="BGR")
        st.json({"slots": slots})
        st.info(
            "Review/edit the generated JSON or use the slot editor script "
            "described in the project README."
        )
    except Exception as e:
        st.error(str(e))
