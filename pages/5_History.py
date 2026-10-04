import streamlit as st
from src.analytics import occupancy_dataframe, events_dataframe, plates_dataframe

if st.session_state.get("user") is None:
    st.warning("Please log in.")
    st.stop()

st.title("🗃️ Parking History")

df = occupancy_dataframe()

if df.empty:
    st.info("No occupancy data has been recorded yet.")
else:
    st.subheader("Occupancy percentage")
    st.line_chart(df.set_index("time")[["occupancy_percent"]])

    st.subheader("Occupied vs free spaces")
    st.line_chart(df.set_index("time")[["occupied_spaces", "free_spaces"]])

    st.subheader("Vehicle count")
    st.line_chart(df.set_index("time")[["vehicle_count"]])

events = events_dataframe()
plates = plates_dataframe()

st.subheader("Parking events")
st.dataframe(events, use_container_width=True)

st.subheader("Plate recognition history")
st.dataframe(plates, use_container_width=True)
