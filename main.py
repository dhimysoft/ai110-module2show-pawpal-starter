from datetime import date, timedelta
from pawpal_system import Task, Pet, Owner, Scheduler

# ── 1. Create owner and pets ──────────────────────────────────────────────────
owner = Owner("John", available_minutes=60)

buddy = Pet("Buddy", "dog")
whiskers = Pet("Whiskers", "cat")
owner.add_pet(buddy)
owner.add_pet(whiskers)

# ── 2. Add tasks (intentionally out of order to test sorting) ─────────────────
task1 = Task("Feed Buddy",      "08:00", 15, "High",   "daily")
task2 = Task("Walk Buddy",      "09:00", 30, "High",   "daily")
task3 = Task("Play with Buddy", "10:00", 20, "Low",    "once")
task4 = Task("Feed Whiskers",   "08:00", 10, "High",   "daily")  # conflict with task1
task5 = Task("Groom Whiskers",  "11:00", 25, "Medium", "weekly")

buddy.add_task(task1)
buddy.add_task(task2)
buddy.add_task(task3)
whiskers.add_task(task4)
whiskers.add_task(task5)

# ── 3. Scheduler ──────────────────────────────────────────────────────────────
scheduler = Scheduler(owner)

# ── 4. All tasks ──────────────────────────────────────────────────────────────
print("=" * 50)
print("ALL TASKS")
print("=" * 50)
for pet_name, task in owner.get_all_tasks():
    print(f"  [{task.priority}] {task.description} ({pet_name}) @ {task.time} ({task.duration} min)")

# ── 5. Sorted schedule ────────────────────────────────────────────────────────
print("\n" + "=" * 50)
print("SORTED BY TIME")
print("=" * 50)
for pet_name, task in scheduler.sort_by_time():
    print(f"  {task.time}  {task.description} ({pet_name}, {task.priority})")

# ── 6. Daily plan ─────────────────────────────────────────────────────────────
print("\n" + "=" * 50)
print("DAILY PLAN  (budget: 60 min)")
print("=" * 50)
plan = scheduler.generate_daily_plan()
print(f"  Time used : {plan['used_minutes']} / {plan['available_minutes']} min")
print("  Scheduled :")
for pet_name, task in plan["scheduled"]:
    print(f"    ✅ {task.description} ({pet_name}) @ {task.time} ({task.duration} min, {task.priority})")
if plan["overflow"]:
    print("  Overflow (didn't fit):")
    for pet_name, task in plan["overflow"]:
        print(f"    ⏭  {task.description} ({pet_name}) ({task.duration} min, {task.priority})")

# ── 7. Conflict detection ─────────────────────────────────────────────────────
print("\n" + "=" * 50)
print("CONFLICT DETECTION")
print("=" * 50)
conflicts = scheduler.detect_conflicts()
if conflicts:
    for warning in conflicts:
        print(f"  {warning}")
else:
    print("  ✅ No conflicts found.")

# ── 8. Recurring task demo ────────────────────────────────────────────────────
print("\n" + "=" * 50)
print("RECURRING TASK DEMO")
print("=" * 50)

def complete_and_reschedule(task: Task, pet: Pet):
    next_task = scheduler.handle_recurring(task, pet)
    print(f"  ✅ Completed: {task.description}")
    if next_task:
        print(f"  🔁 Next occurrence scheduled for: {next_task.due_date}")
    else:
        print("  🗑  No recurrence (one-time task)")

complete_and_reschedule(task1, buddy)     # daily
print()
complete_and_reschedule(task5, whiskers)  # weekly
print()
complete_and_reschedule(task3, buddy)     # once

print("\n" + "=" * 50)
print("DONE")
print("=" * 50)