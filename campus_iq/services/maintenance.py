"""Maintenance intake, status workflow and notifications."""
from database.db import connection
def suggested_priority(category,description):
    text=(category+" "+description).lower()
    if any(k in text for k in ("smoke","fire","electric shock","sparking","exposed wire","flood")): return "Critical"
    if any(k in text for k in ("power failure","network down","projector broken","leak","not working")): return "High"
    return "Medium"
def create_request(user_id,facility_id,asset_id,category,description,priority=None):
    if not facility_id and not asset_id: raise ValueError("Select a facility or an asset.")
    if not category.strip() or not description.strip(): raise ValueError("Category and description are required.")
    with connection() as conn:
        cur=conn.execute("""INSERT INTO maintenance_requests(reported_by,facility_id,asset_id,category,description,priority) VALUES(?,?,?,?,?,?)""",(user_id,facility_id or None,asset_id or None,category,description.strip(),priority or suggested_priority(category,description)))
        conn.execute("INSERT INTO notifications(user_id,title,message,category) VALUES(NULL,?,?,?)",("New maintenance request",f"Maintenance request #{cur.lastrowid} has been reported.","Maintenance"))
        return cur.lastrowid
def update_status(request_id,status,assigned_to=None,resolution=None):
    if status not in {"Reported","Assigned","In Progress","Resolved","Closed"}: raise ValueError("Invalid maintenance status.")
    with connection() as conn:
        row=conn.execute("SELECT reported_by,status FROM maintenance_requests WHERE id=?",(request_id,)).fetchone()
        if not row: raise ValueError("Maintenance request was not found.")
        if status in ("Resolved","Closed") and not (resolution or "").strip(): resolution="Marked complete by maintenance team"
        conn.execute("""UPDATE maintenance_requests SET status=?,assigned_to=COALESCE(?,assigned_to),resolution=COALESCE(?,resolution),resolved_at=CASE WHEN ? IN ('Resolved','Closed') THEN CURRENT_TIMESTAMP ELSE resolved_at END WHERE id=?""",(status,assigned_to,resolution,status,request_id))
        conn.execute("INSERT INTO notifications(user_id,title,message,category) VALUES(?,?,?,?)",(row["reported_by"],"Maintenance update",f"Your request #{request_id} is now {status.lower()}.","Maintenance"))
        conn.execute("INSERT INTO activity_logs(user_id,action,entity,entity_id) VALUES(?,?,?,?)",(assigned_to,"Maintenance status: "+status,"maintenance_request",request_id))
def list_requests(user_id=None):
    sql="""SELECT m.id,m.reported_by,m.category,m.description,m.priority,m.status,m.reported_at,COALESCE(f.name,a.name,'Campus item') item,u.full_name reporter FROM maintenance_requests m LEFT JOIN facilities f ON f.id=m.facility_id LEFT JOIN assets a ON a.id=m.asset_id JOIN users u ON u.id=m.reported_by"""
    params=()
    if user_id is not None: sql+=" WHERE m.reported_by=?"; params=(user_id,)
    sql+=" ORDER BY m.id DESC"
    with connection() as conn: return [dict(r) for r in conn.execute(sql,params)]
