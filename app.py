import streamlit as st
from pawpal_system import Task, Pet, Owner, Scheduler

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")
st.title("🐾 PawPal+")
st.caption("Smart pet care scheduling — powered by your backend logic.")

# ── Session state init ────────────────────────────────────────────────────────
if "owner" not in st.session_state:
    st.session_state.owner = None
if "scheduler" not in st.session_state:
    st.session_state.scheduler = None

# ── Section 1: Owner + Pet Setup ──────────────────────────────────────────────
st.header("1. Owner & Pet Setup")

col1, col2 = st.columns(2)
with col1:
    owner_name = st.text_input("Owner name", value="Jordan")
    available_minutes = st.number_input(
        "Daily time budget (minutes)", min_value=10, max_value=480, value=120
    )
with col2:
    pet_name = st.text_input("Pet name", value="Mochi")
    species = st.selectbox("Species", ["dog", "cat", "bird", "other"])

if st.button("💾 Save Owner & Pet"):
    pet = Pet(name=pet_name, species=species)
    owner = Owner(name=owner_name, available_minutes=int(available_minutes))
    owner.add_pet(pet)
    st.session_state.owner = owner
    st.session_state.scheduler = Scheduler(owner)
    st.success(f"✅ Saved! {owner_name} owns {pet_name} the {species}.")

if st.session_state.owner is None:
    st.info("Set up your owner and pet above to get started.")
    st.stop()

owner = st.session_state.owner
scheduler = st.session_state.scheduler
current_pet = owner.pets[0]

st.divider()

# ── Section 2: Add Tasks ──────────────────────────────────────────────────────
st.header("2. Add Care Tasks")

col1, col2, col3 = st.columns(3)
with col1:
    task_desc = st.text_input("Task description", value="Morning walk")
    task_time = st.text_input("Time (HH:MM)", value="08:00")
with col2:
    duration = st.number_input("Duration (min)", min_value=1, max_value=240, value=20)
    priority = st.selectbox("Priority", ["High", "Medium", "Low"])
with col3:
    frequency = st.selectbox("Frequency", ["daily", "weekly", "once"])

if st.button("➕ Add Task"):
    task = Task(
        description=task_desc,
        time=task_time,
        duration=int(duration),
        priority=priority,
        frequency=frequency,
    )
    current_pet.add_task(task)
    st.success(f"✅ Added: {task_desc} @ {task_time}")

# Show current tasks
all_tasks = owner.get_all_tasks()
if all_tasks:
    st.markdown("**Current tasks:**")
    priority_emoji = {"High": "🔴", "Medium": "🟡", "Low": "🟢"}
    rows = []
    for pet_name_t, task in all_tasks:
        rows.append({
            "Pet": pet_name_t,
            "Task": task.description,
            "Time": task.time,
            "Duration": f"{task.duration} min",
            "Priority": f"{priority_emoji.get(task.priority, '')} {task.priority}",
            "Frequency": task.frequency,
            "Done": "✅" if task.is_complete else "⬜",
        })
    st.table(rows)
else:
    st.info("No tasks yet. Add one above.")

st.divider()

# ── Section 3: Generate Schedule ─────────────────────────────────────────────
st.header("3. Generate Daily Plan")

if st.button("📅 Generate Schedule"):
    if not owner.get_all_tasks():
        st.warning("Add at least one task first.")
    else:
        plan = scheduler.generate_daily_plan()
        conflicts = scheduler.detect_conflicts()

        # Conflict warnings
        if conflicts:
            for warning in conflicts:
                st.warning(warning)

        # Scheduled tasks
        st.subheader("✅ Scheduled Tasks")
        st.caption(
            f"Time used: **{plan['used_minutes']} / {plan['available_minutes']} min**"
        )

        if plan["scheduled"]:
            for pet_name_t, task in plan["scheduled"]:
                priority_emoji = {"High": "🔴", "Medium": "🟡", "Low": "🟢"}
                emoji = priority_emoji.get(task.priority, "")
                st.success(
                    f"{emoji} **{task.description}** ({pet_name_t}) "
                    f"@ {task.time} — {task.duration} min — {task.priority} priority"
                )
        else:
            st.info("No tasks fit within the time budget.")

        # Overflow tasks
        if plan["overflow"]:
            st.subheader("⏭ Overflow (didn't fit)")
            for pet_name_t, task in plan["overflow"]:
                st.error(
                    f"**{task.description}** ({pet_name_t}) "
                    f"— {task.duration} min — {task.priority} priority"
                )

        # Reasoning
        st.subheader("🧠 Why this plan?")
        st.markdown(
            f"Tasks were sorted by **priority** (High → Medium → Low), "
            f"then by **scheduled time**. The scheduler greedily added tasks "
            f"until the {plan['available_minutes']}-minute daily budget was reached. "
            f"Any remaining tasks moved to overflow."
        )

st.divider()

# ── Section 4: Complete a Task ────────────────────────────────────────────────
st.header("4. Complete a Task")

pending = [
    (pname, task)
    for pname, task in owner.get_all_tasks()
    if not task.is_complete
]

if pending:
    options = {
        f"{task.description} ({pname}) @ {task.time}": (pname, task)
        for pname, task in pending
    }
    selected = st.selectbox("Select a task to complete", list(options.keys()))

    if st.button("✅ Mark Complete"):
        pname, task = options[selected]
        pet_obj = next(p for p in owner.pets if p.name == pname)
        next_task = scheduler.handle_recurring(task, pet_obj)
        st.success(f"✅ Marked complete: {task.description}")
        if next_task:
            st.info(f"🔁 Next occurrence scheduled for: {next_task.due_date}")
        else:
            st.info("🗑 One-time task — no recurrence.")
else:
    st.info("No pending tasks.")