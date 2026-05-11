# Pet Planner

Pet Planner is a lightweight Python application for tracking pet care tasks with an intuitive Flask web interface and SQLite persistence. It is designed for small pet owners who want a clean, job-oriented approach to managing daily and recurring pet tasks.

## Features

- Add, edit, and delete pets
- Create and manage tasks for each pet
- Track task status as pending or completed
- View today's tasks and filter by pet, status, or due date
- Simple undo support for deleted tasks and pets
- Stores data locally in `pet_planner.db`

## Getting Started

### Prerequisites

- Python 3.11+ or compatible Python 3 runtime
- A virtual environment configured for the project

### Install dependencies

```bash
cd /home/kheizaran/Github/pet-planner
source .venv/bin/activate
pip install -r requirements.txt
```

### Run the app

```bash
python app.py
```

Open the application in your browser at:

```text
http://127.0.0.1:5000
```

## Project Structure

- `app.py` — application entry point
- `pet_planner.py` — core planner logic with SQLite persistence and CLI support
- `requirements.txt` — Python dependencies
- `templates/` — Flask HTML templates for the web UI
- `pet_planner.db` — SQLite database file generated at runtime

## Usage

The web UI allows you to manage pets and tasks from the browser. The core planner also supports a command-line interface for task and pet management.

## Notes

- Data is persisted in `pet_planner.db`.
- The current implementation focuses on essential pet task management with straightforward workflow and scheduling.
