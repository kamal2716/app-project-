"""Database-backed dashboard metrics and reporting queries."""
from database.db import connection
def dashboard_metrics():
    queries={"buildings":"SELECT COUNT(*) FROM buildings","facilities":"SELECT COUNT(*) FROM facilities","assets":"SELECT COUNT(*) FROM assets","pending":"SELECT COUNT(*) FROM maintenance_requests WHERE status NOT IN ('Resolved','Closed')","bookings":"SELECT COUNT(*) FROM facility_bookings WHERE booking_date=date('now') AND status IN ('Approved','Pending')","damaged":"SELECT COUNT(*) FROM assets WHERE condition IN ('Damaged','Needs Repair')"}
    with connection() as conn:
        result={key:conn.execute(sql).fetchone()[0] for key,sql in queries.items()}
        result["energy"]=conn.execute("SELECT COALESCE(SUM(consumption_kwh),0) FROM energy_records WHERE substr(recorded_on,1,7)=strftime('%Y-%m','now')").fetchone()[0]
        result["recent"]=[dict(row) for row in conn.execute("""SELECT m.id,m.category,m.description,m.priority,m.status,m.reported_at,COALESCE(f.name,a.name,'Campus item') item FROM maintenance_requests m LEFT JOIN facilities f ON f.id=m.facility_id LEFT JOIN assets a ON a.id=m.asset_id ORDER BY m.id DESC LIMIT 6""")]
        result["facility_types"]=[dict(row) for row in conn.execute("SELECT facility_type label,COUNT(*) total FROM facilities GROUP BY facility_type ORDER BY total DESC")]
        result["energy_by_building"]=[dict(row) for row in conn.execute("SELECT b.name,COALESCE(SUM(e.consumption_kwh),0) kwh FROM buildings b LEFT JOIN energy_records e ON e.building_id=b.id GROUP BY b.id")]
    return result
