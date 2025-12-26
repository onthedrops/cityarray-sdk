"""
CITYARRAY Local Database
SQLite storage for detections, patterns, and events
"""

import sqlite3
from datetime import datetime
from pathlib import Path

DB_PATH = Path.home() / "cityarray" / "cityarray.db"

def get_connection():
    """Get database connection."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize database tables."""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Detections table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS detections (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            object_class TEXT NOT NULL,
            confidence REAL NOT NULL,
            action_taken TEXT,
            was_correct INTEGER,
            image_path TEXT
        )
    """)
    
    # Patterns table (learned behaviors)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS patterns (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            conditions TEXT NOT NULL,
            action TEXT NOT NULL,
            success_rate REAL DEFAULT 0,
            times_used INTEGER DEFAULT 0,
            created_at TEXT NOT NULL,
            signed_by TEXT
        )
    """)
    
    # Alerts table (messages displayed)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS alerts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            tier TEXT NOT NULL,
            message TEXT NOT NULL,
            languages TEXT,
            trigger_detection_id INTEGER,
            authorized_by TEXT,
            FOREIGN KEY (trigger_detection_id) REFERENCES detections(id)
        )
    """)
    
    # Queries table (voice interactions)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS queries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            question TEXT NOT NULL,
            response TEXT NOT NULL,
            source TEXT
        )
    """)
    
    conn.commit()
    conn.close()
    print(f"Database initialized: {DB_PATH}")

def log_detection(object_class, confidence, image_path=None):
    """Log a detection event."""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO detections (timestamp, object_class, confidence, image_path)
        VALUES (?, ?, ?, ?)
    """, (datetime.now().isoformat(), object_class, confidence, image_path))
    
    detection_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return detection_id

def get_recent_detections(limit=10):
    """Get recent detections."""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT * FROM detections 
        ORDER BY timestamp DESC 
        LIMIT ?
    """, (limit,))
    
    rows = cursor.fetchall()
    conn.close()
    
    return [dict(row) for row in rows]

def get_detection_summary():
    """Get summary of what's been detected."""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT object_class, COUNT(*) as count, AVG(confidence) as avg_conf
        FROM detections
        GROUP BY object_class
        ORDER BY count DESC
    """)
    
    rows = cursor.fetchall()
    conn.close()
    
    return [dict(row) for row in rows]

def log_alert(tier, message, languages=None, detection_id=None, authorized_by=None):
    """Log an alert that was displayed."""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO alerts (timestamp, tier, message, languages, trigger_detection_id, authorized_by)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (datetime.now().isoformat(), tier, message, languages, detection_id, authorized_by))
    
    alert_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return alert_id

def log_query(question, response, source="voice"):
    """Log a voice/text query."""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO queries (timestamp, question, response, source)
        VALUES (?, ?, ?, ?)
    """, (datetime.now().isoformat(), question, response, source))
    
    conn.commit()
    conn.close()

# Initialize on import
if __name__ == "__main__":
    init_db()
    print("Database ready!")
