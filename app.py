import os
from pathlib import Path

import streamlit as st

from src.auth import authenticate, ensure_default_admin
from src.database import init_db

init_db()
ensure_default_admin()

st.set_page_config(
    page_title="Smart Parking Analyzer",
    page_icon="🅿️",
    layout="wide",
)

if "user" not in st.session_state:
    st.session_state.user = None

if st.session_state.user is None:
    st.title("🅿️ Smart Parking Analyzer")
    st.subheader("Administrator Login")

    with st.form("login"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submit = st.form_submit_button("Login")

    if submit:
        user = authenticate(username, password)
        if user:
            st.session_state.user = user
            st.rerun()
        else:
            st.error("Invalid username or password.")

    st.info("Demo login: admin / admin123 — change it before deployment.")
    st.stop()

user = st.session_state.user

with st.sidebar:
    st.success(f"Logged in as {user['username']}")
    if st.button("Logout"):
        st.session_state.user = None
        st.rerun()

st.title("🅿️ Smart Parking Analyzer")
st.write("Use the pages in the sidebar to manage cameras, calibrate slots, monitor CCTV, and inspect history.")

st.markdown("""
### System modules

- **Admin Dashboard** — occupancy KPIs and history
- **Cameras** — add/manage CCTV, RTSP, webcam and video sources
- **Calibration** — automatically propose parking spaces
- **Live Monitor** — real-time vehicle and parking analysis
- **History** — occupancy, events and number-plate records

### Recommended workflow

**Add Camera → Automatic Calibration → Review slots → Live Monitor → Dashboard**
""")
