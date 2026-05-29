"""Initialize the SQLite database with the required tables.

Run this script to create the database file and schema before starting the app.
"""
from __future__ import annotations
import sqlite3

DB_FILE = "pet_planner.db"

def main() -> None:
    db = sqlite3.connect(DB_FILE)
    cursor = db.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS pets (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            type TEXT NOT NULL,
            age INTEGER
        )
        """
    )
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY,
            pet_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            description TEXT,
            due_time TEXT,
            frequency TEXT NOT NULL,
            status TEXT NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY(pet_id) REFERENCES pets(id)
        )
        """
    )
    db.commit()
    db.close()
    print(f"Initialized database: {DB_FILE}")

if __name__ == "__main__":
    main()
