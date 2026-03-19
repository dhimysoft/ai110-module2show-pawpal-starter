"""
pawpal_system.py
Core backend logic for PawPal+ — Owner, Pet, Task, and Scheduler classes.
"""

from dataclasses import dataclass, field
from datetime import date, timedelta
from typing import Optional


# ---------------------------------------------------------------------------
# Task
# ---------------------------------------------------------------------------

@dataclass
class Task:
    """Represents a single pet care activity."""

    description: str
    time: str                        # "HH:MM" 24-hour format
    duration: int                    # minutes
    priority: str                    # "High", "Medium", "Low"
    frequency: str                   # "once", "daily", "weekly"
    category: str = "general"        # walk, feeding, medication, grooming, enrichment, etc.
    due_date: date = field(default_factory=date.today)
    is_complete: bool = False

    def mark_complete(self) -> Optional["Task"]:
        """
        Mark this task complete.
        For recurring tasks, returns a new Task scheduled for the next occurrence.
        For one-time tasks, returns None.
        """
        self.is_complete = True
        if self.frequency == "daily":
            return Task(
                description=self.description,
                time=self.time,
                duration=self.duration,
                priority=self.priority,
                frequency=self.frequency,
                category=self.category,
                due_date=self.due_date + timedelta(days=1),
            )
        if self.frequency == "weekly":
            return Task(
                description=self.description,
                time=self.time,
                duration=self.duration,
                priority=self.priority,
                frequency=self.frequency,
                category=self.category,
                due_date=self.due_date + timedelta(weeks=1),
            )
        return None  # "once" — no recurrence

    def priority_rank(self) -> int:
        """Return a numeric rank for sorting (lower = higher priority)."""
        return {"High": 0, "Medium": 1, "Low": 2}.get(self.priority, 3)

    def __str__(self) -> str:
        status = "✅" if self.is_complete else "⬜"
        return (
            f"{status} [{self.priority}] {self.time} — {self.description} "
            f"({self.duration} min, {self.frequency})"
        )


# ---------------------------------------------------------------------------
# Pet
# ---------------------------------------------------------------------------

@dataclass
class Pet:
    """Stores pet details and a list of associated tasks."""

    name: str
    species: str
    breed: str = ""
    age: int = 0
    tasks: list = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Add a task to this pet's task list."""
        self.tasks.append(task)

    def remove_task(self, task: Task) -> None:
        """Remove a task from this pet's task list if present."""
        if task in self.tasks:
            self.tasks.remove(task)

    def pending_tasks(self) -> list:
        """Return only incomplete tasks for today."""
        return [t for t in self.tasks if not t.is_complete and t.due_date <= date.today()]

    def __str__(self) -> str:
        return f"{self.name} ({self.species}, age {self.age})"


# ---------------------------------------------------------------------------
# Owner
# ---------------------------------------------------------------------------

@dataclass
class Owner:
    """Manages one or more pets and provides aggregate task access."""

    name: str
    available_minutes: int = 120   # total daily minutes the owner has for pet care
    pets: list = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to the owner's household."""
        self.pets.append(pet)

    def get_all_tasks(self) -> list:
        """Return all tasks across every pet, tagged with the pet's name."""
        tasks = []
        for pet in self.pets:
            for task in pet.tasks:
                tasks.append((pet.name, task))
        return tasks

    def get_pending_tasks(self) -> list:
        """Return only incomplete tasks for today, across all pets."""
        return [(pet_name, t) for pet_name, t in self.get_all_tasks()
                if not t.is_complete and t.due_date <= date.today()]


# ---------------------------------------------------------------------------
# Scheduler
# ---------------------------------------------------------------------------

class Scheduler:
    """
    The 'brain' of PawPal+.
    Retrieves, organises, and intelligently schedules tasks for an owner's pets.
    """

    def __init__(self, owner: Owner):
        self.owner = owner

    # ------------------------------------------------------------------ #
    # Retrieval
    # ------------------------------------------------------------------ #

    def get_all_tasks(self) -> list:
        """Return all (pet_name, Task) tuples from the owner."""
        return self.owner.get_all_tasks()

    def get_pending_tasks(self) -> list:
        """Return only pending (pet_name, Task) tuples for today."""
        return self.owner.get_pending_tasks()

    # ------------------------------------------------------------------ #
    # Sorting & filtering
    # ------------------------------------------------------------------ #

    def sort_by_time(self, tasks: Optional[list] = None) -> list:
        """Return tasks sorted chronologically by HH:MM time string."""
        tasks = tasks if tasks is not None else self.get_pending_tasks()
        return sorted(tasks, key=lambda pair: pair[1].time)

    def sort_by_priority(self, tasks: Optional[list] = None) -> list:
        """Return tasks sorted by priority (High → Medium → Low), then by time."""
        tasks = tasks if tasks is not None else self.get_pending_tasks()
        return sorted(tasks, key=lambda pair: (pair[1].priority_rank(), pair[1].time))

    def filter_tasks(
        self,
        pet_name: Optional[str] = None,
        status: Optional[bool] = None,
        category: Optional[str] = None,
    ) -> list:
        """
        Filter tasks by pet name, completion status, and/or category.
        Pass status=False for incomplete, status=True for complete.
        """
        result = self.get_all_tasks()
        if pet_name:
            result = [(p, t) for p, t in result if p.lower() == pet_name.lower()]
        if status is not None:
            result = [(p, t) for p, t in result if t.is_complete == status]
        if category:
            result = [(p, t) for p, t in result if t.category.lower() == category.lower()]
        return result

    # ------------------------------------------------------------------ #
    # Conflict detection
    # ------------------------------------------------------------------ #

    def detect_conflicts(self) -> list:
        """
        Detect tasks (per pet) scheduled at the same time.
        Returns a list of human-readable warning strings.
        """
        warnings = []
        for pet in self.owner.pets:
            seen: dict = {}
            for task in pet.tasks:
                if not task.is_complete:
                    if task.time in seen:
                        warnings.append(
                            f"⚠️  Conflict for {pet.name}: "
                            f"'{task.description}' and '{seen[task.time].description}' "
                            f"both at {task.time}"
                        )
                    else:
                        seen[task.time] = task
        return warnings

    # ------------------------------------------------------------------ #
    # Recurring task management
    # ------------------------------------------------------------------ #

    def handle_recurring(self, task: Task, pet: Pet) -> Optional[Task]:
        """
        Mark a task complete and, if recurring, add the next occurrence to the pet.
        Returns the new Task if one was created, else None.
        """
        next_task = task.mark_complete()
        if next_task:
            pet.add_task(next_task)
        return next_task

    # ------------------------------------------------------------------ #
    # Smart daily plan
    # ------------------------------------------------------------------ #

    def generate_daily_plan(self) -> dict:
        """
        Generate a prioritised daily plan that fits within the owner's
        available minutes.

        Strategy:
          1. Sort by priority (High first), then by scheduled time.
          2. Greedily add tasks until available_minutes is exhausted.
          3. Tasks that don't fit go into an 'overflow' list.
          4. Detect and surface any time conflicts.

        Returns a dict with keys: scheduled, overflow, conflicts, reasoning.
        """
        pending = self.sort_by_priority()
        conflicts = self.detect_conflicts()

        scheduled = []
        overflow = []
        used_minutes = 0
        reasoning = []

        for pet_name, task in pending:
            if used_minutes + task.duration <= self.owner.available_minutes:
                scheduled.append((pet_name, task))
                used_minutes += task.duration
                reasoning.append(
                    f"✔ Added '{task.description}' for {pet_name} "
                    f"({task.priority} priority, {task.duration} min)"
                )
            else:
                overflow.append((pet_name, task))
                reasoning.append(
                    f"✖ Skipped '{task.description}' for {pet_name} — "
                    f"not enough time remaining ({self.owner.available_minutes - used_minutes} min left)"
                )

        return {
            "scheduled": scheduled,
            "overflow": overflow,
            "conflicts": conflicts,
            "reasoning": reasoning,
            "used_minutes": used_minutes,
            "available_minutes": self.owner.available_minutes,
        }
    
    