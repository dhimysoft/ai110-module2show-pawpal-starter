from dataclasses import dataclass, field
from datetime import date


@dataclass
class Task:
    """Represent a scheduled pet care task with timing, duration, and repetition details.

    This class describes individual care activities so they can be tracked,
    planned, and completed over time.

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
        """Mark the task as completed for its current due date.

        This flips the completion flag so scheduling logic can treat
        the task as done. Will be updated in Phase 2 to also create
        the next occurrence for recurring tasks.
        """
        self.is_complete = True


@dataclass
class Pet:
    """Represent a single animal and the care tasks associated with it.

    This class groups care activities under one pet so scheduling can
    be organized by animal.

    Attributes:
        name: The pet's name as shown to the owner.
        species: The type of animal, such as dog, cat, or bird.
        tasks: The list of care tasks assigned to this pet.
    """
    name: str
    species: str
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task):
        """Attach a new care task to this pet.

        This records the activity in the pet's task list so it can
        be scheduled and tracked.
        """
        self.tasks.append(task)

    def remove_task(self, task: Task):
        """Detach an existing care task from this pet.

        This removes the activity from the pet's task list so it is
        no longer scheduled.
        """
        if task in self.tasks:
            self.tasks.remove(task)


@dataclass
class Owner:
    """Represent a human user who cares for one or more pets.

    This class holds the owner's time budget and the pets they manage
    so scheduling can respect daily limits.

    Attributes:
        name: The owner's display name.
        available_minutes: How many minutes the owner can spend on
            pet care in a typical day.
        pets: The list of pets that belong to this owner.
    """
    name: str
    available_minutes: int = 120
    pets: list[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet):
        """Register a new pet under this owner.

        This adds the pet to the owner's collection so its tasks are
        included in scheduling.
        """
        self.pets.append(pet)

    def get_all_tasks(self) -> list:
        """Collect all tasks across all of the owner's pets.

        This flattens each pet's task list into a single list so the
        scheduler can plan the day.
        """
        tasks = []
        for pet in self.pets:
            tasks.extend(pet.tasks)
        return tasks


class Scheduler:
    """Coordinate and plan pet care tasks for a single owner.

    This class inspects the owner's pets and tasks to sort, filter,
    and build a conflict-aware daily schedule.

    Attributes:
        owner: The owner whose pets and tasks are being scheduled.
    """

    def __init__(self, owner: Owner):
        """Create a scheduler bound to a specific owner.

        This stores the owner so later methods can read their pets,
        tasks, and time limits.
        """
        self.owner = owner

    def sort_by_time(self) -> list:
        """Return all tasks for the owner ordered by scheduled time.

        Sorts using the HH:MM string directly — alphabetical order on
        zero-padded time strings is the same as chronological order.
        """
        tasks = self.owner.get_all_tasks()
        return sorted(tasks, key=lambda t: t.time)

    def filter_tasks(self, pet_name=None, status=None) -> list:
        """Select tasks that match the given pet name and status.

        Pass pet_name to restrict results to one animal.
        Pass status as 'complete' or 'pending' to filter by completion.
        Omit both to return all tasks.
        """
        # Start from pet-specific list if a name is given,
        # otherwise use all tasks across all pets
        if pet_name:
            tasks = [
                task
                for pet in self.owner.pets
                if pet.name == pet_name
                for task in pet.tasks
            ]
        else:
            tasks = self.owner.get_all_tasks()

        # Apply completion filter if requested
        if status == "complete":
            tasks = [t for t in tasks if t.is_complete]
        elif status == "pending":
            tasks = [t for t in tasks if not t.is_complete]

        return tasks

    def detect_conflicts(self) -> list:
        """Identify tasks scheduled at the same time.

        Returns a list of (task_a, task_b) tuples where both tasks
        share the same HH:MM time string. Uses exact-match only —
        interval-based overlap is a known limitation for Phase 4.
        """
        tasks = self.sort_by_time()
        conflicts = []
        seen_times = {}

        for task in tasks:
            if task.time in seen_times:
                # Found two tasks at the same time — flag as conflict
                conflicts.append((seen_times[task.time], task))
            else:
                seen_times[task.time] = task

        return conflicts

    def generate_daily_plan(self) -> dict:
        """Build a feasible daily care plan within the owner's time budget.

        Sorts tasks by priority (High first), then by time within each
        priority tier. Greedily adds tasks until available_minutes is
        exhausted. Tasks that do not fit go into the overflow list.

        Returns a dict with keys:
            scheduled    — tasks that fit within the time budget
            overflow     — tasks that were skipped due to time limits
            total_time_used — total minutes consumed by scheduled tasks
        """
        tasks = self.owner.get_all_tasks()

        # Priority sort: High=0, Medium=1, Low=2, then time as tiebreaker
        priority_order = {"High": 0, "Medium": 1, "Low": 2}
        tasks.sort(key=lambda t: (priority_order.get(t.priority, 3), t.time))

        scheduled = []
        overflow = []
        total_time = 0

        for task in tasks:
            if total_time + task.duration <= self.owner.available_minutes:
                scheduled.append(task)
                total_time += task.duration
            else:
                # Task does not fit — move to overflow rather than drop silently
                overflow.append(task)

        return {
            "scheduled": scheduled,
            "overflow": overflow,
            "total_time_used": total_time,
        }