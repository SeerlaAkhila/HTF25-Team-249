from .schemas import IngestData, SystemStatus, ZoneStatus, Alert
from datetime import datetime

# This is our "in-memory database" for the hackathon
# It will store the latest counts.
# We'll key it by source_id (e.g., 'cam_01')
current_counts = {}

def process_new_data(data: IngestData):
    """
    This function is called by the /api/ingest endpoint.
    It updates our "in-memory database".
    """
    
    # We just received data, let's print it to see it working!
    print(f"Received data: {data.source_id}, Count: {data.data.count}")
    
    # Store the latest count
    current_counts[data.source_id] = data.data.count

def get_system_status() -> SystemStatus:
    """
    This function is called by the /api/status endpoint.
    It builds the status object for the frontend.
    
    --- FAKE DATA ---
    Right now, we are hardcoding this. In the next step,
    we will make this REAL based on the data in 'current_counts'.
    """
    
    # --- FAKE IT 'TIL YOU MAKE IT ---
    # We will pretend 'cam_01' is 'gate_a'
    gate_a_count = current_counts.get("cam_01", 0)
    
    # Simple logic: map count to density/risk
    density = min(gate_a_count / 200.0, 1.0) # Assume 200 is "full"
    risk = "low"
    if density > 0.5: risk = "medium"
    if density > 0.8: risk = "high"
    
    # Build the fake zones
    zone1 = ZoneStatus(
        zone_id="gate_a",
        display_name="Main Gate A",
        density=density,
        risk_level=risk,
        predicted_risk_level=risk, # Just copy for now
        trend="stable" # Fake for now
    )
    
    zone2 = ZoneStatus(
        zone_id="stage_front",
        display_name="Stage Front",
        density=0.4, # Hardcoded
        risk_level="medium",
        predicted_risk_level="medium",
        trend="stable"
    )
    
    # No alerts for now
    active_alerts = []

    return SystemStatus(zones=[zone1, zone2], alerts=active_alerts)