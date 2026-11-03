"""Per-user salted password hashing with legacy demo-hash migration."""
import hashlib, hmac, secrets
from database.db import connection
ITERATIONS = 310_000
LEGACY_SALT = b"campus-iq-demo-salt"
def hash_password(password):
    salt = secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, ITERATIONS)
    return "pbkdf2_sha256$" + str(ITERATIONS) + "$" + salt.hex() + "$" + digest.hex()
def verify_password(password, stored_hash):
    if stored_hash.startswith("pbkdf2_sha256$"):
        try:
            _, rounds, salt_hex, digest_hex = stored_hash.split("$", 3)
            candidate = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), bytes.fromhex(salt_hex), int(rounds)).hex()
            return hmac.compare_digest(candidate, digest_hex)
        except (ValueError, TypeError): return False
    legacy = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), LEGACY_SALT, 180_000).hex()
    return hmac.compare_digest(legacy, stored_hash)
def authenticate(username, password):
    with connection() as conn:
        row = conn.execute("SELECT * FROM users WHERE username=? AND active=1", (username.strip(),)).fetchone()
        if not row or not verify_password(password, row["password_hash"]): return None
        user = dict(row)
        if not row["password_hash"].startswith("pbkdf2_sha256$"):
            conn.execute("UPDATE users SET password_hash=? WHERE id=?", (hash_password(password), row["id"]))
        return user
def change_password(user_id, current_password, new_password):
    if len(new_password) < 10: raise ValueError("New password must contain at least 10 characters.")
    with connection() as conn:
        row=conn.execute("SELECT password_hash FROM users WHERE id=? AND active=1",(user_id,)).fetchone()
        if not row or not verify_password(current_password,row["password_hash"]): raise ValueError("Current password is incorrect.")
        conn.execute("UPDATE users SET password_hash=? WHERE id=?",(hash_password(new_password),user_id))
