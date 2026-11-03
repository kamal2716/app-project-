"""Facility booking rules, visibility and approval workflow."""
from datetime import date, datetime
from database.db import connection
def list_facilities():
    with connection() as conn:
        return [dict(r) for r in conn.execute("""SELECT f.*,b.name AS building_name FROM facilities f JOIN buildings b ON b.id=f.building_id ORDER BY b.name,f.room_code""")]
def create_booking(facility_id,user_id,booking_date,start_time,end_time,purpose,attendees):
    try:
        day=date.fromisoformat(booking_date); start=datetime.strptime(start_time,"%H:%M").time(); end=datetime.strptime(end_time,"%H:%M").time()
    except ValueError: raise ValueError("Enter a valid date (YYYY-MM-DD) and time (HH:MM).")
    if day < date.today(): raise ValueError("Bookings cannot be created for a past date.")
    if start >= end: raise ValueError("End time must be later than start time.")
    if not purpose.strip(): raise ValueError("Please enter the booking purpose.")
    with connection() as conn:
        facility=conn.execute("SELECT capacity,status FROM facilities WHERE id=?",(facility_id,)).fetchone()
        if not facility: raise ValueError("Selected facility does not exist.")
        if facility["status"]!="Available": raise ValueError("This facility is not available.")
        if not 1 <= attendees <= facility["capacity"]: raise ValueError(f"Attendance must be between 1 and {facility['capacity']}.")
        conflict=conn.execute("""SELECT 1 FROM facility_bookings WHERE facility_id=? AND booking_date=? AND status IN ('Pending','Approved') AND start_time < ? AND end_time > ? LIMIT 1""",(facility_id,booking_date,end_time,start_time)).fetchone()
        if conflict: raise ValueError("This time slot overlaps an existing booking.")
        cur=conn.execute("""INSERT INTO facility_bookings(facility_id,user_id,booking_date,start_time,end_time,purpose,attendees) VALUES(?,?,?,?,?,?,?)""",(facility_id,user_id,booking_date,start_time,end_time,purpose.strip(),attendees))
        conn.execute("INSERT INTO notifications(user_id,title,message,category) VALUES(NULL,?,?,?)",("New booking request",f"Booking request #{cur.lastrowid} requires administrator review.","Booking"))
def list_bookings(user_id=None):
    sql="""SELECT x.*,f.name facility,b.name building,u.full_name requester FROM facility_bookings x JOIN facilities f ON f.id=x.facility_id JOIN buildings b ON b.id=f.building_id JOIN users u ON u.id=x.user_id"""
    params=()
    if user_id is not None: sql+=" WHERE x.user_id=?"; params=(user_id,)
    sql+=" ORDER BY booking_date DESC,start_time DESC LIMIT 300"
    with connection() as conn: return [dict(r) for r in conn.execute(sql,params)]
def review_booking(booking_id,decision,reviewer_id):
    if decision not in ("Approved","Rejected"): raise ValueError("Invalid booking decision.")
    with connection() as conn:
        row=conn.execute("SELECT user_id,status FROM facility_bookings WHERE id=?",(booking_id,)).fetchone()
        if not row: raise ValueError("Booking request was not found.")
        if row["status"]!="Pending": raise ValueError("Only pending requests can be reviewed.")
        conn.execute("UPDATE facility_bookings SET status=? WHERE id=?",(decision,booking_id))
        conn.execute("INSERT INTO notifications(user_id,title,message,category) VALUES(?,?,?,?)",(row["user_id"],"Booking "+decision.lower(),f"Your booking request #{booking_id} was {decision.lower()}.","Booking"))
        conn.execute("INSERT INTO activity_logs(user_id,action,entity,entity_id) VALUES(?,?,?,?)",(reviewer_id,"Booking "+decision.lower(),"facility_booking",booking_id))
