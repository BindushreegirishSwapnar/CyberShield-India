from datetime import datetime
import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'cybercrime.db')

def log_audit_event(user_email, user_role, action, target_entity, target_id, details, ip_address="127.0.0.1"):
    """Record an audit trail event in the SQLite database."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS audit_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                user_email TEXT NOT NULL,
                user_role TEXT NOT NULL,
                action TEXT NOT NULL,
                target_entity TEXT,
                target_id TEXT,
                details TEXT,
                ip_address TEXT
            )
        ''')
        
        now_str = datetime.now().strftime("%d %b %Y, %I:%M %p")
        cursor.execute('''
            INSERT INTO audit_logs (timestamp, user_email, user_role, action, target_entity, target_id, details, ip_address)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (now_str, user_email or "anonymous", user_role or "Viewer", action, target_entity, target_id, details, ip_address))
        
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Audit log failure: {e}")

def get_recent_audit_logs(limit=50, action=None):
    """Retrieve audit trail logs with optional action filtering."""
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        query = 'SELECT * FROM audit_logs WHERE 1=1'
        params = []
        if action and action != 'All':
            query += ' AND action = ?'
            params.append(action)
            
        query += ' ORDER BY id DESC LIMIT ?'
        params.append(limit)
        
        cursor.execute(query, params)
        rows = [dict(r) for r in cursor.fetchall()]
        conn.close()
        return rows
    except Exception as e:
        print(f"Error fetching audit logs: {e}")
        return []
