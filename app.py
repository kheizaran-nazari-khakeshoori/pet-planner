"""Flask web interface for the Pet Planner application."""
from __future__ import annotations
import sqlite3
from datetime import datetime
from flask import Flask, g, render_template

# File name of the SQLite database used by this application.
DB_FILE = "pet_planner.db"

# Create the Flask application instance.
app = Flask(__name__)


def get_db() -> sqlite3.Connection:
    """Return the database connection for the current request."""
    if "db" not in g:
        # Open a new SQLite connection and store it in the Flask context.
        g.db = sqlite3.connect(DB_FILE)
        g.db.row_factory = sqlite3.Row
    return g.db


def _task_due_today(task: sqlite3.Row) -> bool:
    """Return True when a task should appear in today's overview."""
    frequency = task["frequency"].strip().lower()
    if frequency == "daily":
        return True
    if frequency == "once":
        return task["status"] == "pending"
    if frequency == "weekly":
        created_at = task.get("created_at")
        if created_at:
            weekday = datetime.fromisoformat(created_at).weekday()
            return weekday == datetime.now().weekday()
        return False
    if frequency.startswith("custom:"):
        _, spec = frequency.split(":", 1)
        days = [token.strip().lower() for token in spec.split(",") if token.strip()]
        today_name = datetime.now().strftime("%A").lower()
        normalized_days = {day[:3] for day in days}
        return today_name[:3] in normalized_days
    return False


@app.teardown_appcontext
def close_db(exception: Exception | None) -> None:
    """Close the database connection at the end of the request."""
    db = g.pop("db", None)
    if db is not None:
        db.close()


@app.route("/")
def index() -> str:
    """Render the main dashboard with pets and tasks."""
    db = get_db()
    pets = db.execute("SELECT id, name, type, age FROM pets").fetchall()
    tasks = db.execute(
        "SELECT id, pet_id, title, description, due_time, frequency, status, created_at FROM tasks"
    ).fetchall()
    # Render the template with the pet and task data from the database.
    return render_template("index.html", pets=pets, tasks=tasks)


@app.route("/today")
def today() -> str:
    """Render the page showing tasks due today."""
    db = get_db()
    tasks = db.execute(
        "SELECT id, pet_id, title, description, due_time, frequency, status, created_at FROM tasks"
    ).fetchall()
    today_tasks = [task for task in tasks if _task_due_today(task)]
    return render_template("today.html", tasks=today_tasks)


if __name__ == "__main__":
    # Run the Flask development server when executed directly.
    app.run(debug=True)
