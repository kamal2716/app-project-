"""Normalized CAMPUS IQ database schema."""
SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
 id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT NOT NULL UNIQUE,
 password_hash TEXT NOT NULL, role TEXT NOT NULL, full_name TEXT NOT NULL,
 email TEXT UNIQUE, active INTEGER NOT NULL DEFAULT 1,
 created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS departments (
 id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL UNIQUE, code TEXT NOT NULL UNIQUE
);
CREATE TABLE IF NOT EXISTS buildings (
 id INTEGER PRIMARY KEY AUTOINCREMENT, code TEXT NOT NULL UNIQUE, name TEXT NOT NULL,
 location TEXT, floors INTEGER NOT NULL DEFAULT 1, condition TEXT NOT NULL DEFAULT 'Good'
);
CREATE TABLE IF NOT EXISTS facilities (
 id INTEGER PRIMARY KEY AUTOINCREMENT, building_id INTEGER NOT NULL REFERENCES buildings(id),
 room_code TEXT NOT NULL, name TEXT NOT NULL, facility_type TEXT NOT NULL,
 floor_number INTEGER NOT NULL DEFAULT 1, capacity INTEGER NOT NULL DEFAULT 1,
 equipment TEXT DEFAULT '', status TEXT NOT NULL DEFAULT 'Available',
 condition TEXT NOT NULL DEFAULT 'Good', UNIQUE(building_id, room_code)
);
CREATE TABLE IF NOT EXISTS facility_bookings (
 id INTEGER PRIMARY KEY AUTOINCREMENT, facility_id INTEGER NOT NULL REFERENCES facilities(id),
 user_id INTEGER NOT NULL REFERENCES users(id), booking_date TEXT NOT NULL,
 start_time TEXT NOT NULL, end_time TEXT NOT NULL, purpose TEXT NOT NULL,
 attendees INTEGER NOT NULL DEFAULT 1, status TEXT NOT NULL DEFAULT 'Pending',
 created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP, CHECK(start_time < end_time)
);
CREATE INDEX IF NOT EXISTS idx_booking_slot ON facility_bookings(facility_id, booking_date, start_time, end_time);
CREATE TABLE IF NOT EXISTS assets (
 id INTEGER PRIMARY KEY AUTOINCREMENT, asset_code TEXT NOT NULL UNIQUE,
 name TEXT NOT NULL, category TEXT NOT NULL, serial_number TEXT UNIQUE,
 building_id INTEGER REFERENCES buildings(id), facility_id INTEGER REFERENCES facilities(id),
 purchase_date TEXT, purchase_price REAL DEFAULT 0, warranty_expiry TEXT,
 condition TEXT NOT NULL DEFAULT 'Good', status TEXT NOT NULL DEFAULT 'Available',
 created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS laboratories (
 id INTEGER PRIMARY KEY AUTOINCREMENT, facility_id INTEGER NOT NULL UNIQUE REFERENCES facilities(id),
 assistant_user_id INTEGER REFERENCES users(id), lab_type TEXT, notes TEXT DEFAULT ''
);
CREATE TABLE IF NOT EXISTS laboratory_sessions (
 id INTEGER PRIMARY KEY AUTOINCREMENT, laboratory_id INTEGER NOT NULL REFERENCES laboratories(id),
 faculty_user_id INTEGER NOT NULL REFERENCES users(id), session_date TEXT NOT NULL,
 start_time TEXT NOT NULL, end_time TEXT NOT NULL, subject TEXT NOT NULL,
 batch_name TEXT, status TEXT NOT NULL DEFAULT 'Scheduled'
);
CREATE TABLE IF NOT EXISTS maintenance_requests (
 id INTEGER PRIMARY KEY AUTOINCREMENT, reported_by INTEGER NOT NULL REFERENCES users(id),
 facility_id INTEGER REFERENCES facilities(id), asset_id INTEGER REFERENCES assets(id),
 category TEXT NOT NULL, description TEXT NOT NULL, priority TEXT NOT NULL DEFAULT 'Medium',
 assigned_to INTEGER REFERENCES users(id), status TEXT NOT NULL DEFAULT 'Reported',
 reported_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP, due_date TEXT, resolved_at TEXT,
 resolution TEXT, CHECK(facility_id IS NOT NULL OR asset_id IS NOT NULL)
);
CREATE TABLE IF NOT EXISTS maintenance_records (
 id INTEGER PRIMARY KEY AUTOINCREMENT, request_id INTEGER NOT NULL REFERENCES maintenance_requests(id),
 technician_id INTEGER REFERENCES users(id), work_date TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
 details TEXT NOT NULL, cost REAL NOT NULL DEFAULT 0
);
CREATE TABLE IF NOT EXISTS energy_records (
 id INTEGER PRIMARY KEY AUTOINCREMENT, building_id INTEGER NOT NULL REFERENCES buildings(id),
 meter_id TEXT NOT NULL, recorded_on TEXT NOT NULL, consumption_kwh REAL NOT NULL,
 cost REAL NOT NULL DEFAULT 0, source TEXT NOT NULL DEFAULT 'Manual',
 UNIQUE(building_id, meter_id, recorded_on)
);
CREATE TABLE IF NOT EXISTS notifications (
 id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER REFERENCES users(id),
 title TEXT NOT NULL, message TEXT NOT NULL, category TEXT DEFAULT 'General',
 is_read INTEGER NOT NULL DEFAULT 0, created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS announcements (
 id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT NOT NULL, body TEXT NOT NULL,
 audience TEXT NOT NULL DEFAULT 'All', created_by INTEGER REFERENCES users(id),
 published_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP, active INTEGER NOT NULL DEFAULT 1
);
CREATE TABLE IF NOT EXISTS asset_assignments (
 id INTEGER PRIMARY KEY AUTOINCREMENT, asset_id INTEGER NOT NULL REFERENCES assets(id),
 assigned_to INTEGER REFERENCES users(id), department_id INTEGER REFERENCES departments(id),
 assigned_on TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP, returned_on TEXT, notes TEXT DEFAULT ''
);
CREATE TABLE IF NOT EXISTS activity_logs (
 id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER REFERENCES users(id),
 action TEXT NOT NULL, entity TEXT, entity_id INTEGER, created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
"""
