# dashboard_app.py
import streamlit as st
import requests
import pandas as pd
import time
import pydeck as pdk
from datetime import datetime

# --- CONFIG ---
API_URL = "http://localhost:8000/api/status"
REFRESH_INTERVAL = 5  # seconds
MAX_HISTORY = 50       # number of points to keep for trend charts

# --- STREAMLIT PAGE SETTINGS ---
st.set_page_config(
    page_title="Crowd Safety Intelligence Dashboard",
    page_icon="🚦",
    layout="wide",
)

st.markdown(
    """
    <style>
    .big-title { font-size:36px; font-weight:800; color:#0077b6; text-align:center; }
    .risk-card { border-radius:12px; padding:12px; text-align:center; color:white; font-weight:700; }
    </style>
    """,
    unsafe_allow_html=True
)

st.markdown("<div class='big-title'>🚦 Crowd Safety Intelligence System</div>", unsafe_allow_html=True)
st.caption("Real-time monitoring and predictive crowd risk visualization")

# --- STATE ---
if "history" not in st.session_state:
    st.session_state.history = {}

# --- Helper function to fetch data ---
def get_status():
    try:
        res = requests.get(API_URL, timeout=2)
        if res.status_code == 200:
            return res.json()
        else:
            st.error(f"Backend error: {res.status_code}")
    except requests.exceptions.RequestException:
        st.warning("⚠️ Cannot connect to backend. Is FastAPI running?")
    return None

# --- Color map for risk levels ---
RISK_COLORS = {
    "low": "#2ecc71",
    "medium": "#f1c40f",
    "high": "#e74c3c",
    "critical": "#8e44ad",
}

# --- Function to add trend data ---
def update_trend(zone_id, density):
    if zone_id not in st.session_state.history:
        st.session_state.history[zone_id] = []
    st.session_state.history[zone_id].append({
        "time": datetime.now().strftime("%H:%M:%S"),
        "density": density,
    })
    # Limit to max points
    if len(st.session_state.history[zone_id]) > MAX_HISTORY:
        st.session_state.history[zone_id] = st.session_state.history[zone_id][-MAX_HISTORY:]

# --- Main container ---
placeholder = st.empty()

while True:
    data = get_status()
    if data:
        zones = data.get("zones", [])
        alerts = data.get("alerts", [])

        with placeholder.container():
            st.subheader("📍 Zone Overview")
            cols = st.columns(len(zones))

            for i, z in enumerate(zones):
                color = RISK_COLORS.get(z["risk_level"], "#7f8c8d")
                update_trend(z["zone_id"], z["density"])

                with cols[i]:
                    st.markdown(f"### {z['display_name']}")
                    st.metric("Density", f"{int(z['density']*100)}%")
                    st.markdown(f"<div class='risk-card' style='background:{color}'>{z['risk_level'].upper()}</div>", unsafe_allow_html=True)
                    st.write(f"**Predicted:** {z['predicted_risk_level'].capitalize()}")
                    st.write(f"Trend: {z['trend'].capitalize()}")

            # --- Trend Charts Section ---
            st.divider()
            st.subheader("📈 Density Trends")
            for z in zones:
                df = pd.DataFrame(st.session_state.history[z["zone_id"]])
                if not df.empty:
                    st.line_chart(df.set_index("time"), y="density", height=200, use_container_width=True)

            # --- Map Section ---
            st.divider()
            st.subheader("🗺️ Zone Map Visualization")

            # Fake coordinates for demo (you can adjust per zone)
            map_data = pd.DataFrame([
                {"lat": 17.3871, "lon": 78.4917, "zone": "Main Gate A", "risk": z["risk_level"]}
                if z["zone_id"] == "gate_a"
                else {"lat": 17.3865, "lon": 78.4905, "zone": "Stage Front", "risk": z["risk_level"]}
                for z in zones
            ])
            map_data["color"] = map_data["risk"].map(lambda r: [255, 0, 0, 160] if r in ["high", "critical"] else [0, 255, 0, 160])

            st.pydeck_chart(
                pdk.Deck(
                    map_style="mapbox://styles/mapbox/light-v9",
                    initial_view_state=pdk.ViewState(latitude=17.387, longitude=78.491, zoom=16),
                    layers=[
                        pdk.Layer(
                            "ScatterplotLayer",
                            data=map_data,
                            get_position="[lon, lat]",
                            get_color="color",
                            get_radius=150,
                        )
                    ],
                )
            )

            # --- Alerts Section ---
            st.divider()
            st.subheader("🚨 Active Alerts")
            if alerts:
                for a in alerts:
                    st.error(f"**[{a['zone_id']}] {a['title']}** - {a['message']}")
            else:
                st.info("✅ No active alerts currently.")

    time.sleep(REFRESH_INTERVAL)
