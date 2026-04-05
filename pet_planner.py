#!/usr/bin/env python3
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, time
from typing import List, Optional

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
        self.pets: List[Pet] = []
        self.tasks: List[Task] = []
        self.next_pet_id = 1
        self.next_task_id = 1

    def run(self) -> None:
        while True:
            print("\nPet Planner CLI")
            print("1) List pets")
            print("2) List tasks")
            print("3) Exit")
            choice = input("Choose an option: ").strip()

            if choice == "1":
                self._list_pets()
            elif choice == "2":
                self._list_tasks()
            elif choice == "3":
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
            print(f"- [{pet.id}] {pet.name} ({pet.type})")

    def _list_tasks(self) -> None:
        if not self.tasks:
            print("No tasks available.")
            return
        print("\nTasks:")
        for task in self.tasks:
            print(f"- [{task.id}] {task.title} for pet {task.pet_id} ({task.status})")

if __name__ == "__main__":
    PetPlanner().run()
