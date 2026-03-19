# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

- Briefly describe your initial UML design.
  
The three main actions a user should be able to perform are:

- Add a pet — the owner needs to register their animal with basic details like name and species so the system knows who it is managing care for.
- Schedule a care task — the owner should be able to create activities like walks, feedings, or medications with a time, duration, and priority level so the system can plan around them.
- View today's plan — the owner needs to see a clear, prioritised daily schedule that fits within their available time, so they know exactly what to do and in what order.


- What classes did you include, and what responsibilities did you assign to each?
  
To support this, I designed four classes: Task, Pet, Owner, and Scheduler.
Task holds all the details of a single care activity — what it is, when it happens, how long it takes, how urgent it is, and how often it repeats. Pet stores the animal's identity and owns a list of its tasks. Owner represents the human user — they have a daily time budget and a list of pets, but they don't manage tasks directly. Scheduler is the brain: it takes an Owner and does all the algorithmic work like sorting, filtering, and planning.

I kept Scheduler as a plain class instead of a dataclass because it holds logic, not stored data. The relationships flow downward: Owner contains Pets, Pets contain Tasks, and Scheduler sits outside that hierarchy — it references an Owner to do its work without being part of the data model.


**b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.

After generating the skeleton with Copilot, I made two changes based on review.

At first, I didn’t think I needed a duration attribute on Task, but I realized the scheduler wouldn’t work without it. Without knowing how long each task takes, the system can’t determine whether tasks fit within the owner’s available time. I added duration to make generate_daily_plan() functional.

Second, I confirmed that the tasks and pets lists use field(default_factory=list) rather than a plain list default. This avoids a shared-state bug in Python dataclasses where all instances would share the same list object if a mutable default is used directly.

I also noticed that mark_complete() is currently documented as only flipping the completion flag, but in Phase 2 it will also need to create the next occurrence for daily and weekly recurring tasks. I flagged this docstring for revision rather than leaving it as a permanent description of incomplete behavior.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)
  
  The scheduler considers two main constraints: priority level and the owner's available time budget. Tasks are ranked High, Medium, and Low. Within the same priority tier, earlier scheduled time is used as a tiebreaker. Tasks are only included in the daily plan if they fit within the owner's available_minutes — anything that doesn't fit is moved to an overflow list rather than silently dropped.

- How did you decide which constraints mattered most?

I chose priority as the primary sort key because the scenario describes a busy owner. When time is limited, the system should protect High priority items like medications and meals before considering enrichment or grooming activities.

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
  
  The scheduler uses exact time-string matching for conflict detection — two tasks conflict only if their time strings are identical, such as two tasks both scheduled at "09:00". This means a 30-minute task at 09:00 and a task at 09:15 are not flagged as a conflict even though they overlap in real time.

- Why is that tradeoff reasonable for this scenario?

This is a deliberate simplification. Implementing true interval-based overlap detection would require converting time strings to datetime objects and comparing ranges, which adds complexity that is not necessary for a first version. The current approach still catches the most common real conflicts, like accidentally scheduling two feedings at the same time. A future version should upgrade to interval-based detection.

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?

I used Copilot at two specific points in Phase 1.
First, I gave Copilot a description of my four classes with their attributes and methods and asked it to generate a Mermaid.js class diagram. This let me visually verify that the relationships — Owner contains Pets, Pets contain Tasks, Scheduler references Owner — matched my design intent before writing any code.

- What kinds of prompts or questions were most helpful?

 after writing my skeleton, I used Copilot's Generate Documentation feature to produce docstrings for every class and method. The most useful prompt pattern was giving Copilot the full file with context rather than one method at a time, because it could then write docstrings that referenced how each method connects to the rest of the system.


**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.

I did not accept the generated docstrings as final without review. The most important example was mark_complete(). Copilot documented it as: "This flips the completion flag so scheduling logic can treat the task as done." That is accurate for the skeleton, but incomplete for the final system — in Phase 2, mark_complete() will also need to return a new Task for recurring activities. I kept the docstring for now but flagged it explicitly for revision after Phase 2 implementation, rather than leaving a misleading description in place permanently.

- How did you evaluate or verify what the AI suggested?
  
I also rejected an earlier Copilot suggestion to use a heapq priority queue for sorting tasks. While technically correct, the task list for a single pet owner will never be large enough to need that data structure, and the code would be significantly harder to read and explain. I used sorted() with a lambda key instead, which does the same job in one readable line.

---

## 4. Testing and Verification

**a. What you tested**z

- What behaviors did you test?

I tested five categories of behavior: task completion and recurrence, pet task management, sorting correctness, conflict detection, and daily plan constraints.

- Why were these tests important?

Task completion and recurrence was the most critical to test because a bug there would cause tasks to silently disappear or duplicate uncontrollably. Conflict detection was important to verify both directions — that same-time tasks produce a warning and that different-time tasks do not. The daily plan tests confirmed that the scheduler never exceeds the owner's available_minutes and that High priority tasks are scheduled before lower priority ones when the budget is tight.


**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

The happy paths and most important edge cases are covered. Tests I would add next include: a pet with zero tasks to ensure no crashes on empty lists, two pets with conflicting tasks at the same time since current detection is per-pet only, a task whose due_date is in the future to verify it is excluded from the daily plan, and recurrence across a month boundary to catch date arithmetic edge cases like January 31 plus one day.

I am confident in the basic functionality, but I would test edge cases like overlapping tasks or limited time.

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

The clean separation between the data layer (Task, Pet, Owner) and the logic layer (Scheduler) worked well from the start. Because all scheduling logic lived in one place, I could verify the backend was correct by running main.py in the terminal before writing a single line of Streamlit UI. This CLI-first workflow made bugs much easier to isolate and fix.

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

I would upgrade the conflict detection from exact time-string matching to interval-based detection. The current approach flags two tasks at "09:00" but misses a 30-minute task at "09:00" overlapping with a task at "09:15". The data is already there — every Task has both a time and a duration — so this is purely an algorithmic upgrade that would make the conflict warnings genuinely reliable.

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?

The most important thing I learned was that AI is most useful as a design reviewer early in the process, not just a code generator. When I used Copilot to challenge my class structure and generate the UML diagram before writing any code, it surfaced design questions that were much cheaper to answer at that stage. By contrast, asking AI to generate code late in the project produced output that needed significant review and revision. The lesson is to front-load AI collaboration on design and reasoning, and be more selective when it comes to accepting implementation suggestions directly.
