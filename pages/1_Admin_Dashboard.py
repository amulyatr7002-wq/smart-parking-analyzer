import streamlit as st
from sqlalchemy import func

from src.database import get_session, Camera, OccupancySnapshot, ParkingEvent, PlateRead
from src.analytics import occupancy_dataframe, events_dataframe, plates_dataframe

if st.session_state.get("user") is None:
    st.warning("Please log in.")
    st.stop()

st.title("📊 Admin Dashboard")

db = get_session()
try:
    cameras = db.query(Camera).filter(Camera.enabled == True).all()

    latest = []
    for cam in cameras:
        row = (
            db.query(OccupancySnapshot)
            .filter(OccupancySnapshot.camera_id == cam.id)
            .order_by(OccupancySnapshot.created_at.desc())
            .first()
        )
        if row:
            latest.append((cam, row))
finally:
    db.close()

total_spaces = sum(r.total_spaces for _, r in latest)
occupied = sum(r.occupied_spaces for _, r in latest)
free = total_spaces - occupied
pct = occupied / total_spaces * 100 if total_spaces else 0

c1, c2, c3, c4 = st.columns(4)
c1.metric("Total Spaces", total_spaces)
c2.metric("Occupied", occupied)
c3.metric("Free", free)
c4.metric("Occupancy", f"{pct:.1f}%")

st.subheader("Current camera status")
for cam, row in latest:
    st.write(
        f"**{cam.name}** — {row.occupied_spaces}/{row.total_spaces} occupied "
        f"({row.occupancy_percent:.1f}%)"
    )

df = occupancy_dataframe()
if not df.empty:
    st.subheader("Occupancy history")
    chart = df.copy()
    chart["time"] = chart["time"].astype(str)
    st.line_chart(chart.set_index("time")[["occupied_spaces", "free_spaces"]])

    st.subheader("Average occupancy by hour")
    df["hour"] = df["time"].dt.hour
    hourly = df.groupby("hour")["occupancy_percent"].mean().round(2)
    st.bar_chart(hourly)

events = events_dataframe()
plates = plates_dataframe()

st.subheader("Recent parking events")
if events.empty:
    st.info("No events recorded yet.")
else:
    st.dataframe(events.head(50), use_container_width=True)
    st.download_button(
        "Download parking events CSV",
        events.to_csv(index=False),
        "parking_events.csv",
        "text/csv"
    )

st.subheader("Recent number-plate reads")
if plates.empty:
    st.info("No plate reads recorded yet.")
else:
    st.dataframe(plates.head(50), use_container_width=True)
    st.download_button(
        "Download plate reads CSV",
        plates.to_csv(index=False),
        "plate_reads.csv",
        "text/csv"
    )

if not df.empty:
    st.download_button(
        "Download occupancy CSV",
        df.to_csv(index=False),
        "occupancy_history.csv",
        "text/csv"
    )
