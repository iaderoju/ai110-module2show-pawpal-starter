# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Smarter Scheduling

The `Scheduler` class has been extended with three algorithmic improvements:

### Sort by time slot — `sort_by_time()`
Returns the scheduled task list ordered chronologically (morning → afternoon → evening → anytime) using Python's `sorted()` with a lambda key. Tasks can be added in any order; the output is always time-coherent.

### Filter tasks — `filter_tasks(completed, pet_name)`
Returns a filtered view of the schedule without mutating it. Both parameters are optional and composable:
- `filter_tasks(pet_name="Mochi")` — one pet's tasks only
- `filter_tasks(completed=False)` — pending tasks only
- `filter_tasks(completed=True, pet_name="Luna")` — Luna's completed tasks

### Conflict detection — `detect_conflicts()`
Scans the plan after `generate_plan()` and returns a list of warning strings — never crashes the program. Two conflict types are caught:
- **Same-pet conflict** — one pet has two tasks of the same category in the same slot (e.g. two walks in the morning)
- **Cross-pet conflict** — different pets require the same category of care in the same slot, double-booking the owner

### Recurring tasks — `Task.next_occurrence()`
Tasks can be marked `recurrence="daily"` or `recurrence="weekly"`. When `Scheduler.mark_task_done()` completes a recurring task, it automatically appends a fresh copy to the pet's task list with the next `due_date` calculated via Python's `timedelta`.

## Testing PawPal+

### Running the test suite

```bash
python -m pytest
```

To see verbose output with each test name:

```bash
python -m pytest -v
```

### What the tests cover

| Area | Tests |
|------|-------|
| **Task completion** | `mark_complete()` flips status to `True`; calling it twice is safe (idempotent) |
| **Task addition** | `add_task()` increases count by one; multiple additions tracked correctly; task is retrievable from `pet.tasks` |
| **Scheduler budget** | Scheduled minutes never exceed `available_minutes`; tasks are skipped when the budget is full |
| **Sorting correctness** | `sort_by_time()` returns tasks in morning → afternoon → evening → anytime order regardless of add order; returns `[]` on an empty schedule |
| **Recurrence logic** | Completing a `recurrence="daily"` task appends a new task due the next day with `completed=False`; non-recurring tasks do not spawn new tasks |
| **Conflict detection** | Same-pet duplicate category/slot flagged as `"same pet"` conflict; two different pets needing the same category in the same slot flagged as `"cross-pet"` conflict |

### Confidence level

**★★★★☆ (4/5)**

The scheduler's core behaviors — budget enforcement, priority ranking, sorting, recurrence, and conflict detection — are all covered by passing tests. Confidence is high for the happy-path and the most important edge cases (empty schedule, non-recurring tasks, double-completion). One star is withheld because time-slot tie-breaking within the same priority level and multi-pet budget interaction under low energy levels are not yet tested.

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.
