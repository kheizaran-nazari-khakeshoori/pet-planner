"""Flask web interface for the Pet Planner application."""
from __future__ import annotations
import sqlite3
from datetime import datetime
from flask import Flask, g, render_template

DB_FILE = "pet_planner.db"

app = Flask(__name__)


def get_db() -> sqlite3.Connection:
    if "db" not in g:
        g.db = sqlite3.connect(DB_FILE)
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def close_db(exception: Exception | None) -> None:
    db = g.pop("db", None)
    if db is not None:
        db.close()


@app.route("/")
def index() -> str:
    db = get_db()
    pets = db.execute("SELECT id, name, type, age FROM pets").fetchall()
    tasks = db.execute(
        "SELECT id, pet_id, title, description, due_time, frequency, status FROM tasks"
    ).fetchall()
    return render_template("index.html", pets=pets, tasks=tasks)


if __name__ == "__main__":
    app.run(debug=True)
