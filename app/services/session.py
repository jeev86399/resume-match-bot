import sqlite3
import json
from typing import Dict, Any, List, Optional
import os

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "session.db")

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS sessions (
            user_id INTEGER PRIMARY KEY,
            jd_text TEXT,
            jd_filename TEXT,
            jd_structured TEXT,
            resumes TEXT,
            reports TEXT,
            status TEXT
        )
    ''')
    conn.commit()
    conn.close()

def _get_session_raw(user_id: int):
    conn = get_db()
    c = conn.cursor()
    c.execute('SELECT * FROM sessions WHERE user_id = ?', (user_id,))
    row = c.fetchone()
    conn.close()
    return row

def get_session(user_id: int) -> Dict[str, Any]:
    row = _get_session_raw(user_id)
    if not row:
        return {
            "user_id": user_id,
            "jd_text": None,
            "jd_filename": None,
            "jd_structured": None,
            "resumes": [],
            "reports": [],
            "status": "waiting_for_jd"
        }
    
    return {
        "user_id": row["user_id"],
        "jd_text": row["jd_text"],
        "jd_filename": row["jd_filename"],
        "jd_structured": json.loads(row["jd_structured"]) if row["jd_structured"] else None,
        "resumes": json.loads(row["resumes"]) if row["resumes"] else [],
        "reports": json.loads(row["reports"]) if row["reports"] else [],
        "status": row["status"]
    }

def update_session(user_id: int, **kwargs):
    session = get_session(user_id)
    session.update(kwargs)
    
    conn = get_db()
    c = conn.cursor()
    
    jd_structured = json.dumps(session["jd_structured"]) if session.get("jd_structured") else None
    resumes = json.dumps(session["resumes"]) if session.get("resumes") else None
    reports = json.dumps(session["reports"]) if session.get("reports") else None
    
    c.execute('''
        INSERT OR REPLACE INTO sessions (user_id, jd_text, jd_filename, jd_structured, resumes, reports, status)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (
        user_id, 
        session.get("jd_text"), 
        session.get("jd_filename"), 
        jd_structured, 
        resumes, 
        reports, 
        session.get("status", "waiting_for_jd")
    ))
    conn.commit()
    conn.close()

def clear_session(user_id: int):
    conn = get_db()
    c = conn.cursor()
    c.execute('DELETE FROM sessions WHERE user_id = ?', (user_id,))
    conn.commit()
    conn.close()

init_db()
