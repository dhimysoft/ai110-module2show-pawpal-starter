from pawpal_system import Task, Pet, Owner, Scheduler
from datetime import timedelta


def test_recurring_task_creates_next_instance():
    owner = Owner("TestOwner", available_minutes=100)
    pet = Pet("Buddy", "dog")
    owner.add_pet(pet)

    task = Task(
        description="Feed Buddy",
        time="08:00",
        duration=10,
        priority="High",
        frequency="daily",
    )

    pet.add_task(task)
    scheduler = Scheduler(owner)

    next_task = scheduler.handle_recurring(task, pet)

    assert task.is_complete is True
    assert next_task is not None
    assert next_task.due_date == task.due_date + timedelta(days=1)


def test_sort_by_time_orders_correctly():
    owner = Owner("TestOwner", 100)
    pet = Pet("Buddy", "dog")
    owner.add_pet(pet)

    t1 = Task("Late task", "10:00", 10, "Low", "once")
    t2 = Task("Early task", "08:00", 10, "High", "once")

    pet.add_task(t1)
    pet.add_task(t2)

    scheduler = Scheduler(owner)
    sorted_tasks = scheduler.sort_by_time()

    assert sorted_tasks[0][1].time == "08:00"


def test_conflict_detection_finds_duplicates():
    owner = Owner("TestOwner", 100)
    pet = Pet("Buddy", "dog")
    owner.add_pet(pet)

    t1 = Task("Task 1", "08:00", 10, "High", "once")
    t2 = Task("Task 2", "08:00", 15, "High", "once")

    pet.add_task(t1)
    pet.add_task(t2)

    scheduler = Scheduler(owner)
    conflicts = scheduler.detect_conflicts()

    assert len(conflicts) == 1