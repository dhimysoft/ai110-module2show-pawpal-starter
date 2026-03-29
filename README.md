# 🐾 PawPal+ (Module 2 Project)

PawPal+ is a smart pet care scheduling system that helps owners organize daily pet tasks based on time constraints, priorities, and recurring needs.

---

## 📌 Overview

This app allows a pet owner to:

- Track daily pet care tasks (feeding, walking, grooming, etc.)
- Assign priorities and durations to tasks
- Automatically generate a daily plan based on available time
- Detect scheduling conflicts
- Handle recurring tasks (daily and weekly)
- View a clear, structured schedule in a Streamlit UI

---

## 🧩 Starter Code Acknowledgment

I started from the provided Streamlit starter file, which included basic UI components but no backend logic.  
I extended it by implementing backend classes (`Task`, `Pet`, `Owner`, `Scheduler`) and connected them to the UI to generate schedules, detect conflicts, and manage recurring tasks.

---

## ⚙️ Features

### ✅ Task Management
- Add tasks with:
  - Time (HH:MM)
  - Duration (minutes)
  - Priority (High, Medium, Low)
  - Frequency (once, daily, weekly)

### 📅 Smart Scheduling
- Tasks are sorted by:
  - **Priority (High → Medium → Low)**
  - Then by **scheduled time**
- Uses a **greedy algorithm** to fit tasks into the owner's time budget

### ⚠️ Conflict Detection
- Detects tasks scheduled at the same time
- Displays warnings in both CLI and UI

### 🔁 Recurring Tasks
- Daily tasks automatically reschedule for the next day
- Weekly tasks reschedule for the next week

### 🧠 Plan Explanation
- Explains how the schedule was generated:
  - Priority-based sorting
  - Time budget constraints
  - Overflow handling

---

## 🧪 Testing PawPal+

Run tests using:

```bash
python -m pytest