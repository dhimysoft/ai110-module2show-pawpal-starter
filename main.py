

from pawpal_system import Task, Pet, Owner, Scheduler

task1 = Task("Feed dog", "08:00", 15, "High", "daily")
task2 = Task("Walk dog", "09:00", 30, "High", "daily")
task3 = Task("Play", "10:00", 20, "Low", "daily")

pet = Pet("Buddy", "dog")
pet.add_task(task1)
pet.add_task(task2)
pet.add_task(task3)

owner = Owner("John", available_minutes=60)
owner.add_pet(pet)

scheduler = Scheduler(owner)

print("ALL TASKS:", owner.get_all_tasks())
print("SORTED:", scheduler.sort_by_time())
print("PLAN:", scheduler.generate_daily_plan())