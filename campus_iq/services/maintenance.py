"""Maintenance intake, status workflow and prioritization."""
from database.db import connection
from datetime import date

def suggested_priority(category,description):
    text=(category+" "+description).lower()
    if any(k in text for k in ("smoke","fire","electric shock","sparking","exposed wire","flood")): return "Critical"
    if any(k in text for k in ("power failure","network down","projector broken","leak","not working")): return "High"
    return "Medium"

def create_request(user_id,facility_id,asset_id,category,description,priority=None):
    if not facility_id and not asset_id: raise ValueError("Select a facility or an asset.")
    chosen=priority or suggested_priority(category,description)
    with connection() as conn:
        cur=conn.execute("""INSERT INTO maintenance_requests(reported_by,facility_id,asset_id,category,description,priority)
            VALUES(?,?,?,?,?,?)""",(user_id,facility_id or None,asset_id or None,category,description,chosen))
        return cur.lastrowid

def update_status(request_id,status,assigned_to=None,resolution=None):
    allowed={"Reported","Assigned","In Progress","Resolved","Closed"}
    if status not in allowed: raise ValueError("Invalid maintenance status.")
    with connection() as conn:
        conn.execute("""UPDATE maintenance_requests SET status=?,assigned_to=COALESCE(?,assigned_to),
            resolution=COALESCE(?,resolution),resolved_at=CASE WHEN ?='Resolved' THEN CURRENT_TIMESTAMP ELSE resolved_at END
            WHERE id=?""",(status,assigned_to,resolution,status,request_id))
