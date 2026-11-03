"""Seed a safe demonstration dataset and a first-run admin account."""
import hashlib
from database.db import connection

def _hash(password):
    return hashlib.pbkdf2_hmac("sha256", password.encode(), b"campus-iq-demo-salt", 180_000).hex()

def seed_database():
    with connection() as conn:
        if conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]:
            return
        users = [
            ("admin", _hash("Admin@123"), "Administrator", "Campus Administrator", "admin@campus.local"),
            ("faculty", _hash("Faculty@123"), "Faculty", "Dr. Meera Raman", "meera@campus.local"),
            ("student", _hash("Student@123"), "Student", "Arun Kumar", "arun@campus.local"),
            ("labassistant", _hash("Lab@123"), "Lab Assistant", "Nisha Devi", "nisha@campus.local"),
            ("maintenance", _hash("Fix@123"), "Maintenance Staff", "Ravi Kumar", "ravi@campus.local"),
        ]
        conn.executemany("INSERT INTO users(username,password_hash,role,full_name,email) VALUES(?,?,?,?,?)", users)
        conn.executemany("INSERT INTO departments(name,code) VALUES(?,?)", [
            ("Computer Science & Engineering","CSE"),("Electronics & Communication","ECE"),
            ("Mechanical Engineering","MECH"),("Administration","ADMIN")])
        conn.executemany("INSERT INTO buildings(code,name,location,floors,condition) VALUES(?,?,?,?,?)", [
            ("A","Innovation Block","North Campus",4,"Good"),("B","Technology Centre","Central Campus",3,"Good"),
            ("C","Science Block","East Campus",3,"Needs Inspection")])
        conn.executemany("INSERT INTO facilities(building_id,room_code,name,facility_type,floor_number,capacity,equipment,status,condition) VALUES(?,?,?,?,?,?,?,?,?)", [
            (1,"A-101","CSE Smart Classroom","Classroom",1,60,"Projector, Smart board","Available","Good"),
            (1,"A-204","AI & Computing Lab","Laboratory",2,40,"40 Workstations, Projector","Available","Good"),
            (2,"B-301","Innovation Auditorium","Seminar Hall",3,180,"Audio system, Projector","Available","Good"),
            (3,"C-102","Electronics Lab","Laboratory",1,32,"Oscilloscopes, Power supplies","Available","Needs Inspection"),
            (2,"B-110","Faculty Meeting Room","Meeting Room",1,18,"Display, Video conferencing","Available","Good")])
        conn.execute("INSERT INTO laboratories(facility_id,assistant_user_id,lab_type,notes) VALUES(2,4,'Computing','Demo laboratory')")
        conn.execute("INSERT INTO laboratories(facility_id,assistant_user_id,lab_type,notes) VALUES(4,4,'Electronics','Demo laboratory')")
        conn.executemany("INSERT INTO assets(asset_code,name,category,serial_number,building_id,facility_id,purchase_date,purchase_price,warranty_expiry,condition,status) VALUES(?,?,?,?,?,?,?,?,?,?,?)", [
            ("AST-1001","Dell OptiPlex Workstation","Computer","DEMO-PC-001",1,2,"2025-01-10",62000,"2028-01-10","Good","Available"),
            ("AST-1002","Epson Projector","Projector","DEMO-PRJ-001",1,1,"2024-08-14",48000,"2027-08-14","Good","Available"),
            ("AST-1003","Digital Oscilloscope","Lab Instrument","DEMO-OSC-001",3,4,"2023-06-01",75000,"2026-06-01","Needs Repair","Under Maintenance"),
            ("AST-1004","HP Laser Printer","Printer","DEMO-PRN-001",2,5,"2025-03-15",22000,"2027-03-15","Good","Available")])
        conn.executemany("INSERT INTO energy_records(building_id,meter_id,recorded_on,consumption_kwh,cost,source) VALUES(?,?,?,?,?,?)", [
            (1,"MTR-A","2026-10-01",420,3360,"Demo"),(2,"MTR-B","2026-10-01",365,2920,"Demo"),
            (3,"MTR-C","2026-10-01",298,2384,"Demo")])
        conn.executemany("INSERT INTO maintenance_requests(reported_by,facility_id,asset_id,category,description,priority,assigned_to,status,due_date) VALUES(?,?,?,?,?,?,?,?,?)", [
            (2,4,None,"Electrical","One lab power outlet requires inspection","High",5,"Assigned","2026-11-06"),
            (4,None,3,"Equipment","Oscilloscope display is intermittently flickering","Medium",5,"In Progress","2026-11-08")])
