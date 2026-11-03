"""Facility booking rules and conflict prevention."""
from database.db import connection
from datetime import date

def list_facilities():
    with connection() as conn:
        return [dict(r) for r in conn.execute("""SELECT f.*,b.name AS building_name FROM facilities f
            JOIN buildings b ON b.id=f.building_id ORDER BY b.name,f.room_code""")]

def create_booking(facility_id,user_id,booking_date,start_time,end_time,purpose,attendees):
    if booking_date < date.today().isoformat():
        raise ValueError("Bookings cannot be created for a past date.")
    if not start_time < end_time:
        raise ValueError("End time must be later than start time.")
    with connection() as conn:
        facility=conn.execute("SELECT capacity,status FROM facilities WHERE id=?",(facility_id,)).fetchone()
        if not facility: raise ValueError("Selected facility does not exist.")
        if facility["status"] != "Available": raise ValueError("This facility is not available.")
        if attendees < 1 or attendees > facility["capacity"]:
            raise ValueError(f"Attendance must be between 1 and {facility['capacity']}.")
        conflict=conn.execute("""SELECT 1 FROM facility_bookings WHERE facility_id=? AND booking_date=?
            AND status IN ('Pending','Approved') AND start_time < ? AND end_time > ? LIMIT 1""",
            (facility_id,booking_date,end_time,start_time)).fetchone()
        if conflict: raise ValueError("This time slot overlaps an existing booking.")
        conn.execute("""INSERT INTO facility_bookings(facility_id,user_id,booking_date,start_time,end_time,purpose,attendees)
            VALUES(?,?,?,?,?,?,?)""",(facility_id,user_id,booking_date,start_time,end_time,purpose,attendees))

def list_bookings():
    with connection() as conn:
        return [dict(r) for r in conn.execute("""SELECT x.*,f.name facility,b.name building,u.full_name requester
            FROM facility_bookings x JOIN facilities f ON f.id=x.facility_id
            JOIN buildings b ON b.id=f.building_id JOIN users u ON u.id=x.user_id
            ORDER BY booking_date DESC,start_time DESC LIMIT 300""")]
