from dataclasses import dataclass, field
from datetime import date, timedelta


@dataclass
class Task:
    """Represent a scheduled pet care task with timing, duration, and repetition details.

    Attributes:
        description: A short description of the care activity.
        time: The clock time when the task is scheduled, in HH:MM 24-hour format.
        duration: How long the task is expected to take, in minutes.
        priority: The urgency of the task — High, Medium, or Low.
        frequency: How often the task repeats — once, daily, or weekly.
        due_date: The calendar date when the task is next due.
        is_complete: Whether the task has been completed for the current due date.
    """
    description: str
    time: str           # "HH:MM"
    duration: int       # minutes
    priority: str       # "High", "Medium", "Low"
    frequency: str      # "once", "daily", "weekly"
    due_date: date = field(default_factory=date.today)
    is_complete: bool = False

    def mark_complete(self):
        """Mark the task as completed for its current due date."""
        self.is_complete = True


@dataclass
class Pet:
    """Represent a single animal and the care tasks associated with it.

    Attributes:
        name: The pet's name as shown to the owner.
        species: The type of animal, such as dog, cat, or bird.
        tasks: The list of care tasks assigned to this pet.
    """
    name: str
    species: str
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task):
        """Attach a new care task to this pet."""
        self.tasks.append(task)

    def remove_task(self, task: Task):
        """Detach an existing care task from this pet."""
        if task in self.tasks:
            self.tasks.remove(task)


@dataclass
class Owner:
    """Represent a human user who cares for one or more pets.

    Attributes:
        name: The owner's display name.
        available_minutes: How many minutes the owner can spend on pet care per day.
        pets: The list of pets that belong to this owner.
    """
    name: str
    available_minutes: int = 120
    pets: list[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet):
        """Register a new pet under this owner."""
        self.pets.append(pet)

    def get_all_tasks(self) -> list[tuple[str, Task]]:
        """Collect all tasks across all pets as (pet_name, task) tuples."""
        result = []
        for pet in self.pets:
            for task in pet.tasks:
                result.append((pet.name, task))
        return result


class Scheduler:
    """Coordinate and plan pet care tasks for a single owner.

    Attributes:
        owner: The owner whose pets and tasks are being scheduled.
    """

    def __init__(self, owner: Owner):
        """Create a scheduler bound to a specific owner."""
        self.owner = owner

    def sort_by_time(self) -> list[tuple[str, Task]]:
        """Return all tasks ordered by scheduled time as (pet_name, task) tuples."""
        tasks = self.owner.get_all_tasks()
        return sorted(tasks, key=lambda pair: pair[1].time)

    def filter_tasks(self, pet_name: str = None, status: str = None) -> list[tuple[str, Task]]:
        """Select tasks matching the given pet name and/or completion status.

        Returns list of (pet_name, task) tuples.
        """
        if pet_name:
            tasks = [
                (pname, task)
                for pname, task in self.owner.get_all_tasks()
                if pname == pet_name
            ]
        else:
            tasks = self.owner.get_all_tasks()

        if status == "complete":
            tasks = [(pname, t) for pname, t in tasks if t.is_complete]
        elif status == "pending":
            tasks = [(pname, t) for pname, t in tasks if not t.is_complete]

        return tasks

    def detect_conflicts(self) -> list[str]:
        """Identify tasks scheduled at the same time and return warning strings."""
        sorted_tasks = self.sort_by_time()
        conflicts = []
        seen: dict = {}

        for pet_name, task in sorted_tasks:
            if task.time in seen:
                prev_pet, prev_task = seen[task.time]
                conflicts.append(
                    f"⚠️  CONFLICT at {task.time}: "
                    f"'{prev_task.description}' ({prev_pet}) "
                    f"vs '{task.description}' ({pet_name})"
                )
            else:
                seen[task.time] = (pet_name, task)

        return conflicts

    def generate_daily_plan(self) -> dict:
        """Build a feasible daily care plan within the owner's time budget.

        Returns dict with keys:
            scheduled         — (pet_name, task) tuples that fit
            overflow          — (pet_name, task) tuples that didn't fit
            used_minutes      — total minutes consumed
            available_minutes — the owner's daily budget
        """
        tasks = self.owner.get_all_tasks()
        priority_order = {"High": 0, "Medium": 1, "Low": 2}
        tasks.sort(key=lambda pair: (priority_order.get(pair[1].priority, 3), pair[1].time))

        scheduled = []
        overflow = []
        used = 0

        for pet_name, task in tasks:
            if used + task.duration <= self.owner.available_minutes:
                scheduled.append((pet_name, task))
                used += task.duration
            else:
                overflow.append((pet_name, task))

        return {
            "scheduled": scheduled,
            "overflow": overflow,
            "used_minutes": used,
            "available_minutes": self.owner.available_minutes,
        }

    def handle_recurring(self, task: Task, pet: Pet) -> Task | None:
        """Mark a task complete and schedule the next occurrence if recurring.

        Returns the new Task if created, or None for one-time tasks.
        """
        task.mark_complete()

        if task.frequency == "daily":
            next_task = Task(
                description=task.description,
                time=task.time,
                duration=task.duration,
                priority=task.priority,
                frequency=task.frequency,
                due_date=task.due_date + timedelta(days=1),
            )
            pet.add_task(next_task)
            return next_task

        elif task.frequency == "weekly":
            next_task = Task(
                description=task.description,
                time=task.time,
                duration=task.duration,
                priority=task.priority,
                frequency=task.frequency,
                due_date=task.due_date + timedelta(weeks=1),
            )
            pet.add_task(next_task)
            return next_task

        return None