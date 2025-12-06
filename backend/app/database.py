"""
SQLite Database for Contract Persistence
Simple file-based storage for contract sessions.
"""
import sqlite3
import json
from datetime import datetime
from typing import Dict, Any, List, Optional
from pathlib import Path

# Database file location
DB_PATH = Path(__file__).parent.parent / "contracts.db"


def get_connection() -> sqlite3.Connection:
    """Get a database connection."""
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Initialize the database and create tables if they don't exist."""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sessions (
            session_id TEXT PRIMARY KEY,
            contract_spec TEXT,
            contract_text TEXT,
            chat_history TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    conn.commit()
    conn.close()
    print(f"[Database] Initialized at {DB_PATH}")


def save_session(
    session_id: str,
    contract_spec: Optional[Dict[str, Any]] = None,
    contract_text: Optional[str] = None,
    chat_history: Optional[List[Dict[str, Any]]] = None
):
    """Save or update a session in the database."""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Check if session exists
    cursor.execute("SELECT session_id FROM sessions WHERE session_id = ?", (session_id,))
    exists = cursor.fetchone() is not None
    
    now = datetime.now().isoformat()
    
    if exists:
        # Update existing session
        updates = ["updated_at = ?"]
        params = [now]
        
        if contract_spec is not None:
            updates.append("contract_spec = ?")
            params.append(json.dumps(contract_spec, default=str))
        
        if contract_text is not None:
            updates.append("contract_text = ?")
            params.append(contract_text)
        
        if chat_history is not None:
            updates.append("chat_history = ?")
            params.append(json.dumps(chat_history, default=str))
        
        params.append(session_id)
        
        cursor.execute(
            f"UPDATE sessions SET {', '.join(updates)} WHERE session_id = ?",
            params
        )
    else:
        # Insert new session
        cursor.execute(
            """
            INSERT INTO sessions (session_id, contract_spec, contract_text, chat_history, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                session_id,
                json.dumps(contract_spec, default=str) if contract_spec else None,
                contract_text,
                json.dumps(chat_history, default=str) if chat_history else "[]",
                now,
                now
            )
        )
    
    conn.commit()
    conn.close()


def get_session(session_id: str) -> Optional[Dict[str, Any]]:
    """Get a session from the database."""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM sessions WHERE session_id = ?", (session_id,))
    row = cursor.fetchone()
    conn.close()
    
    if row is None:
        return None
    
    return {
        "session_id": row["session_id"],
        "contract_spec": json.loads(row["contract_spec"]) if row["contract_spec"] else None,
        "contract_text": row["contract_text"],
        "chat_history": json.loads(row["chat_history"]) if row["chat_history"] else [],
        "created_at": row["created_at"],
        "updated_at": row["updated_at"],
    }


def list_sessions(limit: int = 50) -> List[Dict[str, Any]]:
    """List all sessions, most recent first."""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        """
        SELECT session_id, contract_spec, contract_text, created_at, updated_at
        FROM sessions
        ORDER BY updated_at DESC
        LIMIT ?
        """,
        (limit,)
    )
    
    rows = cursor.fetchall()
    conn.close()
    
    sessions = []
    for row in rows:
        spec = json.loads(row["contract_spec"]) if row["contract_spec"] else {}
        sessions.append({
            "session_id": row["session_id"],
            "title": spec.get("title", "Untitled Contract"),
            "freelancer_name": spec.get("freelancer", {}).get("name") if spec.get("freelancer") else None,
            "client_name": spec.get("client", {}).get("name") if spec.get("client") else None,
            "has_contract": row["contract_text"] is not None,
            "created_at": row["created_at"],
            "updated_at": row["updated_at"],
        })
    
    return sessions


def delete_session(session_id: str) -> bool:
    """Delete a session from the database."""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("DELETE FROM sessions WHERE session_id = ?", (session_id,))
    deleted = cursor.rowcount > 0
    
    conn.commit()
    conn.close()
    
    return deleted


def add_chat_message(session_id: str, message: Dict[str, Any]):
    """Add a chat message to a session's history."""
    session = get_session(session_id)
    if session:
        chat_history = session.get("chat_history", [])
        chat_history.append(message)
        save_session(session_id, chat_history=chat_history)

