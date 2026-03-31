"""
main.py — PawPal+ terminal testing ground.
Run:  python main.py
"""

from datetime import date
from pawpal_system import Task, Pet, Owner, Scheduler

# ---------------------------------------------------------------------------
# 1. Create Owner
# ---------------------------------------------------------------------------
owner = Owner(
    name="Jordan",
    available_minutes=90,
    preferred_times=["morning", "evening"],
    energy_level="medium",
)

# ---------------------------------------------------------------------------
# 2. Create Pets
# ---------------------------------------------------------------------------
mochi = Pet(name="Mochi", species="dog", breed="Shiba Inu", age_years=3, weight_lbs=22.0)
luna  = Pet(name="Luna",  species="cat", breed="Domestic Shorthair", age_years=5, weight_lbs=9.5)

luna.update_health_info("medication for hyperthyroid")

# ---------------------------------------------------------------------------
# 3. Add Tasks — intentionally OUT OF ORDER to test sort_by_time()
# ---------------------------------------------------------------------------

# Mochi's tasks (added evening → afternoon → morning, not chronological)
today = date.today()

mochi.add_task(Task("Brush Coat",      "grooming",   10, "low",    "evening"))
mochi.add_task(Task("Fetch / Playtime","enrichment", 15, "medium", "afternoon"))
mochi.add_task(Task("Dinner",          "feed",        5, "high",   "evening",   recurrence="daily",  due_date=today))
mochi.add_task(Task("Morning Walk",    "walk",        25, "high",   "morning",   recurrence="daily",  due_date=today))
mochi.add_task(Task("Breakfast",       "feed",        5, "high",   "morning",   recurrence="daily",  due_date=today))
mochi.add_task(Task("Evening Walk",    "walk",        20, "high",   "evening",   recurrence="daily",  due_date=today))
# Deliberate conflict: second "walk" for Mochi in the morning → same-pet conflict
mochi.add_task(Task("Park Sprint",     "walk",        10, "medium", "morning"))

# Luna's tasks (added evening → morning → afternoon, not chronological)
luna.add_task(Task("Dinner",           "feed",        5, "high",   "evening",   recurrence="daily",  due_date=today))
luna.add_task(Task("Thyroid Meds",     "med",         5, "high",   "morning",   recurrence="daily",  due_date=today,
                   notes="Mix into food, prescribed by Dr. Patel"))
luna.add_task(Task("Laser Pointer",    "enrichment", 10, "medium", "afternoon"))
luna.add_task(Task("Breakfast",        "feed",        5, "high",   "morning",   recurrence="daily",  due_date=today))
luna.add_task(Task("Litter Box",       "grooming",    5, "medium", "morning",   recurrence="weekly", due_date=today))

# ---------------------------------------------------------------------------
# 4. Register pets with owner
# ---------------------------------------------------------------------------
owner.add_pet(mochi)
owner.add_pet(luna)

# ---------------------------------------------------------------------------
# 5. Run the Scheduler
# ---------------------------------------------------------------------------
scheduler = Scheduler(owner)
scheduler.generate_plan()
summary   = scheduler.get_summary()

# ---------------------------------------------------------------------------
# 6. Print Today's Schedule — formatted for readability
# ---------------------------------------------------------------------------

DIVIDER     = "=" * 58
SECTION_SEP = "-" * 58

PRIORITY_LABEL = {"high": "[!!!]", "medium": "[ ! ]", "low": "[   ]"}
TIME_ORDER     = ["morning", "afternoon", "evening", "anytime"]

print()
print(DIVIDER)
print(f"  PawPal+  |  Today's Schedule  |  {summary['date']}")
print(f"  Owner : {summary['owner']}")
print(f"  Pets  : {', '.join(summary['pets'])}")
print(f"  Budget: {summary['total_minutes_available']} min available")
print(DIVIDER)

# Group scheduled tasks by time slot
slots: dict[str, list[dict]] = {slot: [] for slot in TIME_ORDER}
for entry in summary["scheduled"]:
    slots[entry["time_slot"]].append(entry)

for slot in TIME_ORDER:
    if not slots[slot]:
        continue
    print(f"\n  {slot.upper()}")
    print(f"  {SECTION_SEP}")
    for entry in slots[slot]:
        badge = PRIORITY_LABEL.get(entry["priority"], "[   ]")
        print(
            f"  {badge}  {entry['pet']:<6}  "
            f"{entry['task']:<25}  "
            f"{entry['duration_minutes']:>3} min  "
            f"({entry['category']})"
        )
        if entry["notes"]:
            print(f"           note: {entry['notes']}")

# Footer totals
print()
print(DIVIDER)
print(
    f"  Scheduled : {summary['tasks_scheduled']} tasks  "
    f"({summary['total_minutes_scheduled']} / {summary['total_minutes_available']} min used)"
)

if summary["skipped"]:
    print(f"  Skipped   : {summary['tasks_skipped']} tasks (not enough time)")
    for s in summary["skipped"]:
        print(f"    - [{s['pet']}] {s['task']}  ({s['duration_minutes']} min, {s['priority']})")
else:
    print("  Skipped   : none — all tasks fit in the budget!")

print(DIVIDER)
print()

# ---------------------------------------------------------------------------
# 7. sort_by_time() — tasks re-ordered morning → afternoon → evening → anytime
# ---------------------------------------------------------------------------
print()
print(DIVIDER)
print("  sort_by_time()  —  chronological order regardless of add order")
print(DIVIDER)
for entry in scheduler.sort_by_time():
    print(
        f"  [{entry['time_slot']:<10}]  {entry['pet'].name:<6}  "
        f"{entry['task'].name:<25}  {entry['task'].duration_minutes:>3} min"
    )
print()

# ---------------------------------------------------------------------------
# 8. filter_tasks() — by pet name, then by completion status
# ---------------------------------------------------------------------------
print(DIVIDER)
print("  filter_tasks(pet_name='Mochi')  —  Mochi's tasks only")
print(DIVIDER)
for entry in scheduler.filter_tasks(pet_name="Mochi"):
    print(f"  {entry['task'].name:<25}  slot: {entry['time_slot']}")

print()

# Mark one task done so the completion filter has something to show
scheduler.mark_task_done("Breakfast")

print(DIVIDER)
print("  filter_tasks(completed=True)  —  tasks marked done so far")
print(DIVIDER)
done = scheduler.filter_tasks(completed=True)
if done:
    for entry in done:
        print(f"  [DONE]  {entry['pet'].name}  —  {entry['task'].name}")
else:
    print("  (none completed yet)")

print()
print(DIVIDER)
print("  filter_tasks(completed=False)  —  tasks still pending")
print(DIVIDER)
for entry in scheduler.filter_tasks(completed=False):
    print(
        f"  [ -- ]  {entry['pet'].name:<6}  "
        f"{entry['task'].name:<25}  ({entry['task'].priority})"
    )
print(DIVIDER)
print()

# ---------------------------------------------------------------------------
# 9. Recurrence — mark recurring tasks done, verify next occurrence is queued
# ---------------------------------------------------------------------------
print(DIVIDER)
print("  Recurrence — completing daily/weekly tasks auto-spawns next occurrence")
print(DIVIDER)

recurring_demos = ["Morning Walk", "Litter Box"]   # daily + weekly examples
for task_name in recurring_demos:
    scheduler.mark_task_done(task_name)
    print(f"  Marked '{task_name}' complete.")

print()
print("  Next occurrences now queued on each pet:")
for pet in owner.pets:
    pending = pet.get_pending_tasks()
    next_tasks = [t for t in pending if t.due_date is not None and t.due_date > today]
    for t in next_tasks:
        print(
            f"    [{pet.name}]  {t.name:<25}  "
            f"recurrence={t.recurrence:<7}  due={t.due_date}"
        )

print(DIVIDER)
print()

# ---------------------------------------------------------------------------
# 10. detect_conflicts() — verify warnings print, program does NOT crash
# ---------------------------------------------------------------------------
print(DIVIDER)
print("  detect_conflicts()  --  scheduling conflict warnings")
print(DIVIDER)
conflicts = scheduler.detect_conflicts()
if conflicts:
    for warning in conflicts:
        print(f"  !! {warning}")
else:
    print("  No conflicts detected.")
print(DIVIDER)
print()
