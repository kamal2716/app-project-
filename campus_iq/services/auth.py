"""Authentication with PBKDF2 password hashing."""
import hashlib, hmac
from database.db import connection

_DEMO_SALT = b"campus-iq-demo-salt"

def verify_password(password, stored_hash):
    candidate = hashlib.pbkdf2_hmac("sha256", password.encode(), _DEMO_SALT, 180_000).hex()
    return hmac.compare_digest(candidate, stored_hash)

def authenticate(username, password):
    with connection() as conn:
        row = conn.execute("SELECT * FROM users WHERE username=? AND active=1", (username.strip(),)).fetchone()
    if row and verify_password(password, row["password_hash"]):
        return dict(row)
    return None
