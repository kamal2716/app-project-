"""Regression tests for authentication, booking, maintenance and report exports."""
import sys, unittest, tempfile
from pathlib import Path\nfrom uuid import uuid4
from datetime import date,timedelta
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from database.db import initialize_database, connection
from services.auth import authenticate, hash_password, verify_password
from services.maintenance import suggested_priority, create_request, update_status, list_requests
from services.bookings import create_booking, list_bookings, review_booking
from services.notifications import list_notifications, unread_count, mark_all_read
from utils.exporters import export_rows

class CampusIQTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls): initialize_database()
    def test_demo_login_and_password_hash_salt(self):
        self.assertIsNotNone(authenticate("admin","Admin@123"))
        self.assertIsNone(authenticate("admin","incorrect"))
        first,second=hash_password("StrongPassword123"),hash_password("StrongPassword123")
        self.assertNotEqual(first,second)
        self.assertTrue(verify_password("StrongPassword123",first))
    def test_seed_data(self):
        with connection() as conn:
            self.assertGreater(conn.execute("SELECT COUNT(*) FROM facilities").fetchone()[0],0)
            self.assertGreater(conn.execute("SELECT COUNT(*) FROM assets").fetchone()[0],0)
    def test_priority_rules(self):
        self.assertEqual(suggested_priority("Electrical","Sparking from exposed wire"),"Critical")
        self.assertEqual(suggested_priority("Furniture","Loose chair"),"Medium")
    def test_booking_conflict_and_review(self):
        future=(date.today()+timedelta(days=30 + uuid4().int % 300)).isoformat()
        with connection() as conn:
            facility=conn.execute("SELECT id FROM facilities LIMIT 1").fetchone()[0]
            user=conn.execute("SELECT id FROM users WHERE username='student'").fetchone()[0]
        create_booking(facility,user,future,"09:00","10:00","Regression test",2)
        booking=next(x for x in list_bookings(user) if x["purpose"]=="Regression test")
        with self.assertRaises(ValueError):
            create_booking(facility,user,future,"09:30","10:30","Conflict test",2)
        admin=authenticate("admin","Admin@123")
        review_booking(booking["id"],"Approved",admin["id"])
        self.assertEqual(next(x for x in list_bookings(user) if x["id"]==booking["id"])["status"],"Approved")
    def test_maintenance_and_notifications(self):
        user=authenticate("student","Student@123")
        with connection() as conn: facility=conn.execute("SELECT id FROM facilities LIMIT 1").fetchone()[0]
        request_id=create_request(user["id"],facility,None,"Electrical","Sparking from socket")
        self.assertTrue(any(x["id"]==request_id for x in list_requests(user["id"])))
        update_status(request_id,"Resolved",user["id"])
        self.assertGreater(unread_count(user["id"]),0)
        self.assertTrue(list_notifications(user["id"]))
        mark_all_read(user["id"])
        self.assertEqual(unread_count(user["id"]),0)
    def test_csv_export_to_requested_path(self):
        with tempfile.TemporaryDirectory() as folder:
            target=Path(folder)/"report.csv"
            result=export_rows(target,["A"],[(1,)])
            self.assertEqual(Path(result),target)
            self.assertIn("A",target.read_text(encoding="utf-8-sig"))
if __name__=="__main__": unittest.main()
