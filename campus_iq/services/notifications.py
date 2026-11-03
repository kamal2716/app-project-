"""In-app notification centre."""
from database.db import connection
def list_notifications(user_id,limit=100):
    with connection() as conn: return [dict(r) for r in conn.execute("SELECT * FROM notifications WHERE user_id IS NULL OR user_id=? ORDER BY created_at DESC LIMIT ?",(user_id,limit))]
def unread_count(user_id):
    with connection() as conn: return conn.execute("SELECT COUNT(*) FROM notifications WHERE is_read=0 AND (user_id IS NULL OR user_id=?)",(user_id,)).fetchone()[0]
def mark_read(notification_id,user_id):
    with connection() as conn: conn.execute("UPDATE notifications SET is_read=1 WHERE id=? AND (user_id IS NULL OR user_id=?)",(notification_id,user_id))
def mark_all_read(user_id):
    with connection() as conn: conn.execute("UPDATE notifications SET is_read=1 WHERE is_read=0 AND (user_id IS NULL OR user_id=?)",(user_id,))
