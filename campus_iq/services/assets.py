"""Asset registry and safe CRUD helpers."""
from database.db import connection

def list_assets():
    with connection() as conn:
        return [dict(r) for r in conn.execute("""SELECT a.*,b.name building,f.name room FROM assets a
            LEFT JOIN buildings b ON b.id=a.building_id LEFT JOIN facilities f ON f.id=a.facility_id ORDER BY a.id DESC""")]

def add_asset(code,name,category,serial,building_id,facility_id,condition="Good"):
    if not code.strip() or not name.strip(): raise ValueError("Asset code and name are required.")
    with connection() as conn:
        conn.execute("""INSERT INTO assets(asset_code,name,category,serial_number,building_id,facility_id,condition)
            VALUES(?,?,?,?,?,?,?)""",(code.strip(),name.strip(),category,serial.strip() or None,building_id or None,facility_id or None,condition))

def set_asset_condition(asset_id,condition):
    status="Under Maintenance" if condition in ("Damaged","Needs Repair") else "Available"
    with connection() as conn:
        conn.execute("UPDATE assets SET condition=?,status=? WHERE id=?",(condition,status,asset_id))
