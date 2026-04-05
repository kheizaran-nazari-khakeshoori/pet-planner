#!/usr/bin/env python3
"""Pet Planner CLI application with SQLite persistence."""
from __future__ import annotations
import sqlite3
from dataclasses import dataclass, field
from datetime import datetime, time
from typing import List, Optional

DB_FILE = "pet_planner.db"

@dataclass
class Pet:
    id: int
    name: str
    type: str
    age: Optional[int] = None

@dataclass
class Task:
    id: int
    pet_id: int
    title: str
    description: str
    due_time: Optional[time] = None
    frequency: str = "once"
    status: str = "pending"
    created_at: datetime = field(default_factory=datetime.now)

class PetPlanner:
    def __init__(self) -> None:
        self.db = sqlite3.connect(DB_FILE)
        self.db.row_factory = sqlite3.Row
        self._ensure_db()
        self.pets: List[Pet] = []
        self.tasks: List[Task] = []
        self.next_pet_id = 1
        self.next_task_id = 1
        self._load_data()

    def _ensure_db(self) -> None:
        cursor = self.db.cursor()
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
        self.db.commit()

    def _load_data(self) -> None:
        cursor = self.db.cursor()
        cursor.execute("SELECT id, name, type, age FROM pets")
        self.pets = [Pet(id=row[0], name=row[1], type=row[2], age=row[3]) for row in cursor.fetchall()]
        cursor.execute(
            "SELECT id, pet_id, title, description, due_time, frequency, status, created_at FROM tasks"
        )
        self.tasks = [
            Task(
                id=row[0],
                pet_id=row[1],
                title=row[2],
                description=row[3] or "",
                due_time=self._parse_time(row[4]) if row[4] else None,
                frequency=row[5],
                status=row[6],
                created_at=datetime.fromisoformat(row[7]),
            )
            for row in cursor.fetchall()
        ]
        self.next_pet_id = max((pet.id for pet in self.pets), default=0) + 1
        self.next_task_id = max((task.id for task in self.tasks), default=0) + 1

    def run(self) -> None:
        while True:
            print("\nPet Planner CLI")
            print("1) List pets")
            print("2) Add pet")
            print("3) Edit pet")
            print("4) Delete pet")
            print("5) List tasks")
            print("6) Add task")
            print("7) Edit task")
            print("8) Delete task")
            print("9) Mark task complete")
            print("10) List today's tasks")
            print("11) Exit")
            choice = input("Choose an option: ").strip()

            if choice == "1":
                self._list_pets()
            elif choice == "2":
                self._add_pet()
            elif choice == "3":
                self._edit_pet()
            elif choice == "4":
                self._delete_pet()
            elif choice == "5":
                self._list_tasks()
            elif choice == "6":
                self._add_task()
            elif choice == "7":
                self._edit_task()
            elif choice == "8":
                self._delete_task()
            elif choice == "9":
                self._mark_task_complete()
            elif choice == "10":
                self._list_today_tasks()
            elif choice == "11":
                print("Goodbye!")
                break
            else:
                print("Invalid choice. Please try again.")

    def _list_pets(self) -> None:
        if not self.pets:
            print("No pets available.")
            return
        print("\nPets:")
        for pet in self.pets:
            age_text = f", age {pet.age}" if pet.age is not None else ""
            print(f"- [{pet.id}] {pet.name} ({pet.type}{age_text})")

    def _add_pet(self) -> None:
        name = input("Pet name: ").strip()
        pet_type = input("Pet type: ").strip()
        age_str = input("Pet age (optional): ").strip()
        age = int(age_str) if age_str.isdigit() else None
        cursor = self.db.cursor()
        cursor.execute(
            "INSERT INTO pets (name, type, age) VALUES (?, ?, ?)",
            (name, pet_type, age),
        )
        self.db.commit()
        pet_id = cursor.lastrowid
        pet = Pet(id=pet_id, name=name, type=pet_type, age=age)
        self.pets.append(pet)
        self.next_pet_id = max(self.next_pet_id, pet_id + 1)
        print(f"Added pet [{pet.id}] {pet.name}.")

    def _edit_pet(self) -> None:
        pet = self._select_pet("edit")
        if pet is None:
            return
        pet.name = input(f"New name ({pet.name}): ").strip() or pet.name
        pet.type = input(f"New type ({pet.type}): ").strip() or pet.type
        age_str = input(f"New age ({pet.age if pet.age is not None else 'none'}): ").strip()
        pet.age = int(age_str) if age_str.isdigit() else pet.age
        cursor = self.db.cursor()
        cursor.execute(
            "UPDATE pets SET name = ?, type = ?, age = ? WHERE id = ?",
            (pet.name, pet.type, pet.age, pet.id),
        )
        self.db.commit()
        print(f"Updated pet [{pet.id}] {pet.name}.")

    def _delete_pet(self) -> None:
        pet = self._select_pet("delete")
        if pet is None:
            return
        cursor = self.db.cursor()
        cursor.execute("DELETE FROM tasks WHERE pet_id = ?", (pet.id,))
        cursor.execute("DELETE FROM pets WHERE id = ?", (pet.id,))
        self.db.commit()
        self.pets.remove(pet)
        self.tasks = [task for task in self.tasks if task.pet_id != pet.id]
        print(f"Deleted pet [{pet.id}] and removed associated tasks.")

    def _list_tasks(self) -> None:
        if not self.tasks:
            print("No tasks available.")
            return
        print("\nTasks:")
        for task in self.tasks:
            due_text = task.due_time.strftime("%H:%M") if task.due_time else "No due time"
            pet_name = self._get_pet_name(task.pet_id)
            print(
                f"- [{task.id}] {task.title} for pet {pet_name} | {task.frequency} | {due_text} | {task.status}"
            )

    def _add_task(self) -> None:
        if not self.pets:
            print("Add a pet before creating tasks.")
            return
        pet = self._select_pet("assign this task to")
        if pet is None:
            return
        title = input("Task title: ").strip()
        description = input("Task description: ").strip()
        due_time = self._parse_time(input("Due time (HH:MM) optional: ").strip())
        frequency = input("Frequency [once/daily/weekly/custom]: ").strip() or "once"
        created_at = datetime.now().isoformat()
        due_time_str = self._time_to_string(due_time)
        cursor = self.db.cursor()
        cursor.execute(
            """
            INSERT INTO tasks (pet_id, title, description, due_time, frequency, status, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (pet.id, title, description, due_time_str, frequency, "pending", created_at),
        )
        self.db.commit()
        task_id = cursor.lastrowid
        task = Task(
            id=task_id,
            pet_id=pet.id,
            title=title,
            description=description,
            due_time=due_time,
            frequency=frequency,
            status="pending",
            created_at=datetime.fromisoformat(created_at),
        )
        self.tasks.append(task)
        self.next_task_id = max(self.next_task_id, task_id + 1)
        print(f"Added task [{task.id}] {task.title} for pet [{pet.id}] {pet.name}.")

    def _edit_task(self) -> None:
        task = self._select_task("edit")
        if task is None:
            return
        task.title = input(f"New title ({task.title}): ").strip() or task.title
        task.description = input(f"New description ({task.description}): ").strip() or task.description
        due_time_input = input("New due time (HH:MM) leave blank to keep: ").strip()
        due_time = self._parse_time(due_time_input) if due_time_input else task.due_time
        task.due_time = due_time
        task.frequency = input(f"New frequency ({task.frequency}): ").strip() or task.frequency
        cursor = self.db.cursor()
        cursor.execute(
            "UPDATE tasks SET title = ?, description = ?, due_time = ?, frequency = ? WHERE id = ?",
            (task.title, task.description, self._time_to_string(task.due_time), task.frequency, task.id),
        )
        self.db.commit()
        print(f"Updated task [{task.id}] {task.title}.")

    def _delete_task(self) -> None:
        task = self._select_task("delete")
        if task is None:
            return
        cursor = self.db.cursor()
        cursor.execute("DELETE FROM tasks WHERE id = ?", (task.id,))
        self.db.commit()
        self.tasks.remove(task)
        print(f"Deleted task [{task.id}] {task.title}.")

    def _mark_task_complete(self) -> None:
        task = self._select_task("mark as complete")
        if task is None:
            return
        task.status = "completed"
        cursor = self.db.cursor()
        cursor.execute("UPDATE tasks SET status = ? WHERE id = ?", (task.status, task.id))
        self.db.commit()
        print(f"Task [{task.id}] {task.title} marked as completed.")

    def _list_today_tasks(self) -> None:
        today_tasks = [task for task in self.tasks if self._is_task_due_today(task)]
        if not today_tasks:
            print("No tasks due today.")
            return
        print("\nToday's Tasks:")
        for task in today_tasks:
            due_text = task.due_time.strftime("%H:%M") if task.due_time else "No due time"
            pet_name = self._get_pet_name(task.pet_id)
            print(
                f"- [{task.id}] {task.title} for pet {pet_name} | {task.frequency} | {due_text} | {task.status}"
            )

    def _is_task_due_today(self, task: Task) -> bool:
        if task.status != "pending":
            return False
        if task.frequency in {"daily", "weekly", "custom", "once"}:
            return True
        return False

    def _get_pet_name(self, pet_id: int) -> str:
        for pet in self.pets:
            if pet.id == pet_id:
                return pet.name
        return f"Unknown({pet_id})"

    def _select_pet(self, action: str) -> Optional[Pet]:
        self._list_pets()
        pet_id_str = input(f"Enter pet ID to {action}: ").strip()
        if not pet_id_str.isdigit():
            print("Invalid pet ID.")
            return None
        pet_id = int(pet_id_str)
        for pet in self.pets:
            if pet.id == pet_id:
                return pet
        print("Pet not found.")
        return None

    def _select_task(self, action: str) -> Optional[Task]:
        self._list_tasks()
        task_id_str = input(f"Enter task ID to {action}: ").strip()
        if not task_id_str.isdigit():
            print("Invalid task ID.")
            return None
        task_id = int(task_id_str)
        for task in self.tasks:
            if task.id == task_id:
                return task
        print("Task not found.")
        return None

    def _parse_time(self, value: Optional[str]) -> Optional[time]:
        if not value:
            return None
        try:
            return datetime.strptime(value, "%H:%M").time()
        except ValueError:
            print("Invalid time format. Use HH:MM.")
            return None

    def _time_to_string(self, value: Optional[time]) -> Optional[str]:
        return value.strftime("%H:%M") if value else None

if __name__ == "__main__":
    PetPlanner().run()
