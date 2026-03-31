"""
main.py — PawPal+ terminal testing ground.
Run:  python main.py
"""

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
# 3. Add Tasks (mix of times and priorities)
# ---------------------------------------------------------------------------

# Mochi's tasks
mochi.add_task(Task("Morning Walk",    "walk",       25, "high",   "morning"))
mochi.add_task(Task("Evening Walk",    "walk",       20, "high",   "evening"))
mochi.add_task(Task("Breakfast",       "feed",        5, "high",   "morning"))
mochi.add_task(Task("Dinner",          "feed",        5, "high",   "evening"))
mochi.add_task(Task("Fetch / Playtime","enrichment", 15, "medium", "afternoon"))
mochi.add_task(Task("Brush Coat",      "grooming",   10, "low",    "evening"))

# Luna's tasks
luna.add_task(Task("Breakfast",        "feed",        5, "high",   "morning"))
luna.add_task(Task("Dinner",           "feed",        5, "high",   "evening"))
luna.add_task(Task("Thyroid Meds",     "med",         5, "high",   "morning",
                   notes="Mix into food, prescribed by Dr. Patel"))
luna.add_task(Task("Litter Box",       "grooming",    5, "medium", "morning"))
luna.add_task(Task("Laser Pointer",    "enrichment", 10, "medium", "afternoon"))

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
