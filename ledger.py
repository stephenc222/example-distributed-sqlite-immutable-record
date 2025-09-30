"""
Ledger module for managing SQLite-based immutable records.

This module provides functions to initialize SQLite databases as append-only ledgers
and add records to them. Each record gets a timestamp and unique identifier to ensure
immutability and ordering.
"""

import sqlite3
import time


def init_db(db_file: str) -> sqlite3.Connection:
    """
    Initialize a SQLite database with a ledger table.
    
    The ledger table stores records as an append-only log with:
    - id: auto-incrementing primary key (ensures ordering)
    - timestamp: Unix timestamp when record was added
    - data: the actual record content
    - hash: SHA256 hash of the record for integrity
    
    Args:
        db_file: Path to the SQLite database file
        
    Returns:
        sqlite3.Connection: Connection to the initialized database
    """
    conn = sqlite3.connect(db_file)
    
    # Create the ledger table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS ledger (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp REAL NOT NULL,
            data TEXT NOT NULL,
            hash TEXT NOT NULL
        )
    """)
    
    # Create index on hash for faster lookups
    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_ledger_hash ON ledger(hash)
    """)
    
    conn.commit()
    return conn


def add_record(conn: sqlite3.Connection, data: str) -> int:
    """
    Add a new record to the ledger.
    
    This function creates an immutable record by:
    1. Generating a timestamp
    2. Computing a hash of the data
    3. Inserting into the ledger table
    
    Args:
        conn: SQLite database connection
        data: The data to store in the ledger
        
    Returns:
        int: The ID of the inserted record
    """
    import hashlib
    
    timestamp = time.time()
    
    # Create hash of the data for integrity
    record_hash = hashlib.sha256(data.encode('utf-8')).hexdigest()
    
    cursor = conn.execute("""
        INSERT INTO ledger (timestamp, data, hash)
        VALUES (?, ?, ?)
    """, (timestamp, data, record_hash))
    
    conn.commit()
    return cursor.lastrowid


def get_all_records(conn: sqlite3.Connection) -> list[tuple]:
    """
    Retrieve all records from the ledger in order.
    
    Args:
        conn: SQLite database connection
        
    Returns:
        list[tuple]: List of (id, timestamp, data, hash) tuples
    """
    cursor = conn.execute("""
        SELECT id, timestamp, data, hash
        FROM ledger
        ORDER BY id
    """)
    return cursor.fetchall()


def get_record_count(conn: sqlite3.Connection) -> int:
    """
    Get the total number of records in the ledger.
    
    Args:
        conn: SQLite database connection
        
    Returns:
        int: Number of records in the ledger
    """
    cursor = conn.execute("SELECT COUNT(*) FROM ledger")
    return cursor.fetchone()[0]


