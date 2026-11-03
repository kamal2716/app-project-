"""Smoke tests for database setup and core service logic."""
import sys, tempfile, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from database.db import initialize_database, connection
from services.auth import authenticate
from services.maintenance import suggested_priority

class CampusIQTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        initialize_database()
    def test_demo_admin_login(self):
        self.assertIsNotNone(authenticate("admin","Admin@123"))
        self.assertIsNone(authenticate("admin","wrong"))
    def test_seeded_data(self):
        with connection() as conn:
            self.assertGreater(conn.execute("SELECT COUNT(*) FROM facilities").fetchone()[0],0)
            self.assertGreater(conn.execute("SELECT COUNT(*) FROM assets").fetchone()[0],0)
    def test_priority_rules(self):
        self.assertEqual(suggested_priority("Electrical","Sparking from exposed wire"),"Critical")
        self.assertEqual(suggested_priority("Furniture","Loose chair"),"Medium")

if __name__=="__main__": unittest.main()
