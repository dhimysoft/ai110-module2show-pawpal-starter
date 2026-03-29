# 🐾 PawPal+ Project Reflection

---

## 1. System Design

### a. Initial Design

The system was designed around three core user actions:

- **Adding a pet** — allowing the owner to register animals with basic identifying information  
- **Scheduling care tasks** — including time, duration, priority, and frequency  
- **Viewing a daily plan** — presenting a clear, prioritized schedule within the owner's time constraints  

To support these actions, I designed four classes: **Task, Pet, Owner, and Scheduler**.

- **Task** represents a single care activity and stores attributes such as time, duration, priority, frequency, due date, and completion status.  
- **Pet** acts as a container for tasks and represents a single animal.  
- **Owner** manages multiple pets and defines the available time budget.  
- **Scheduler** is the central logic component responsible for sorting, filtering, conflict detection, and scheduling.  

The relationships are hierarchical: an Owner contains Pets, Pets contain Tasks, and the Scheduler operates externally as a controller. This separation keeps the data model clean and focused.

---

### b. Design Changes

During implementation, I made several refinements:

- I added a **duration attribute** to the Task class. Without duration, the scheduler could not determine whether tasks fit within the owner's time budget.  
- I ensured all mutable fields used `field(default_factory=list)` to avoid shared state issues in Python dataclasses.  
- I updated the role of `mark_complete()`, which evolved from a simple flag update to supporting recurring task workflows via the Scheduler.  

---

## 2. Scheduling Logic and Tradeoffs

### a. Constraints and Priorities

The scheduler considers two main constraints:

- **Priority level (High → Medium → Low)**  
- **Available time budget**

Tasks are sorted first by priority and then by scheduled time. A **greedy algorithm** is used to add tasks sequentially until the time budget is reached. Remaining tasks are placed in an overflow list.

Priority was chosen as the dominant constraint because the system is designed for a busy user, ensuring critical tasks are always scheduled first.

---

### b. Tradeoffs

The scheduler uses **exact time-string matching** for conflict detection.

- Tasks only conflict if they share the same start time (e.g., both at "09:00")  
- It does NOT detect overlapping intervals (e.g., 09:00–09:30 vs 09:15)

This simplification keeps the implementation readable and efficient for an initial version, while still catching common scheduling mistakes.

---

## 3. AI Collaboration

### a. How AI Was Used

AI (Copilot) was used primarily during the design phase:

- Generated a **Mermaid.js UML diagram** from class descriptions  
- Produced **docstrings** across the codebase  

Providing full file context improved the quality and consistency of AI-generated output.

---

### b. Judgment and Verification

Not all AI suggestions were accepted:

- I rejected the use of a **heapq priority queue** because it added unnecessary complexity  
- I chose `sorted()` with a lambda function for better readability  
- I reviewed and adjusted AI-generated docstrings, especially for evolving methods like `mark_complete()`  

---

## 4. Testing and Verification

### a. What Was Tested

I tested the following behaviors:

- Task completion and recurrence  
- Task addition to pets  
- Sorting correctness  
- Conflict detection  
- Daily plan time constraints  

These tests ensure the scheduler behaves correctly in both normal and edge cases.

---

### b. Confidence

I am confident in the core functionality of the system.

Future tests could include:

- Pets with no tasks  
- Overlapping task intervals  
- Tasks with future due dates  
- Date edge cases (e.g., end-of-month recurrence)  

---

## 5. Reflection

### a. What Went Well

The separation between the **data layer** and the **logic layer** worked extremely well.

Using a **CLI-first workflow** allowed me to validate the backend logic before integrating the UI, making debugging easier and more efficient.

---

### b. What I Would Improve

I would implement **interval-based conflict detection** to handle overlapping tasks more accurately. The system already contains the necessary data (time and duration), so this would be a natural next step.

---

### c. Key Takeaway

AI is most effective as a **design collaborator**, not just a code generator.

Using AI early in the process helped validate system architecture, while later-stage suggestions required careful review to maintain clarity and simplicity.

---