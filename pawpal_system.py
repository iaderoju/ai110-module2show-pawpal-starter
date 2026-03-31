"""
PawPal+ — Logic Layer
Backend classes for the pet care planning assistant.
"""

from dataclasses import dataclass, field
from typing import Optional
from datetime import date as Date


# ---------------------------------------------------------------------------
# Task
# ---------------------------------------------------------------------------

@dataclass
class Task:
    """A single pet care activity (walk, feeding, medication, grooming, etc.)."""

    name: str
    category: str                          # walk | feed | med | enrichment | grooming
    duration_minutes: int
    priority: str                          # low | medium | high
    preferred_time_of_day: str = "anytime" # morning | afternoon | evening | anytime
    frequency_per_day: int = 1
    notes: str = ""
    completed: bool = False

    def is_high_priority(self) -> bool:
        """Return True if this task is marked high priority."""
        return self.priority == "high"

    def get_priority_score(self) -> int:
        """Return a numeric score (3=high, 2=medium, 1=low) for scheduler ranking."""
        scores = {"high": 3, "medium": 2, "low": 1}
        return scores.get(self.priority, 1)

    def mark_complete(self) -> None:
        """Mark this task as completed."""
        self.completed = True

    def __repr__(self) -> str:
        """Return a compact string representation showing name, category, priority, and status."""
        status = "done" if self.completed else "pending"
        return (
            f"Task({self.name!r}, {self.category}, "
            f"{self.duration_minutes}min, {self.priority}, {status})"
        )


# ---------------------------------------------------------------------------
# Pet
# ---------------------------------------------------------------------------

@dataclass
class Pet:
    """Stores pet profile and owns a list of care Tasks."""

    name: str
    species: str                           # dog | cat | other
    breed: str = "unknown"
    age_years: int = 0
    weight_lbs: float = 0.0
    health_conditions: list[str] = field(default_factory=list)
    tasks: list[Task] = field(default_factory=list)

    # -- Task management ---------------------------------------------------

    def add_task(self, task: Task) -> None:
        """Append a Task to this pet's task list."""
        self.tasks.append(task)

    def remove_task(self, task_name: str) -> None:
        """Remove a task by name (no-op if not found)."""
        self.tasks = [t for t in self.tasks if t.name != task_name]

    def get_pending_tasks(self) -> list[Task]:
        """Return all tasks that are not yet completed."""
        return [t for t in self.tasks if not t.completed]

    # -- Smart defaults ----------------------------------------------------

    def get_care_requirements(self) -> list[Task]:
        """Return a species-appropriate default task list for bootstrapping a new pet's schedule."""
        defaults: list[Task] = []

        if self.species == "dog":
            defaults = [
                Task("Morning Walk",  "walk",        20, "high",   "morning"),
                Task("Evening Walk",  "walk",        20, "high",   "evening"),
                Task("Feeding",       "feed",         5, "high",   "morning", frequency_per_day=2),
                Task("Water Refresh", "feed",         2, "medium", "anytime", frequency_per_day=3),
            ]
        elif self.species == "cat":
            defaults = [
                Task("Feeding",       "feed",         5, "high",   "morning", frequency_per_day=2),
                Task("Litter Box",    "grooming",     5, "medium", "morning"),
                Task("Playtime",      "enrichment",  15, "medium", "evening"),
                Task("Water Refresh", "feed",         2, "medium", "anytime", frequency_per_day=2),
            ]
        else:
            defaults = [
                Task("Feeding",       "feed",         5, "high",   "morning"),
                Task("Check-in",      "enrichment",  10, "medium", "evening"),
            ]

        # Add medication task for each flagged health condition
        for condition in self.health_conditions:
            if "medication" in condition.lower() or "med" in condition.lower():
                defaults.append(
                    Task(
                        f"Medication ({condition})", "med",
                        5, "high", "morning",
                        notes=f"As prescribed for {condition}",
                    )
                )

        return defaults

    def update_health_info(self, condition: str) -> None:
        """Add a health condition to this pet's profile (no duplicates)."""
        if condition not in self.health_conditions:
            self.health_conditions.append(condition)

    def __repr__(self) -> str:
        """Return a compact string showing the pet's name, species, age, and task count."""
        return (
            f"Pet({self.name!r}, {self.species}, "
            f"age={self.age_years}yr, {len(self.tasks)} tasks)"
        )


# ---------------------------------------------------------------------------
# Owner
# ---------------------------------------------------------------------------

class Owner:
    """
    Manages one or more Pets and exposes their combined task list
    to the Scheduler. Also stores the owner's time and energy constraints.
    """

    def __init__(
        self,
        name: str,
        available_minutes: int = 60,
        preferred_times: Optional[list[str]] = None,
        energy_level: str = "medium",       # low | medium | high
    ):
        """Initialize an Owner with a time budget, preferred slots, and energy level."""
        self.name = name
        self.available_minutes = available_minutes
        self.preferred_times: list[str] = preferred_times or ["morning", "evening"]
        self.energy_level = energy_level    # affects which slots are offered
        self.preferences: dict = {}
        self.pets: list[Pet] = []

    # -- Pet management ----------------------------------------------------

    def add_pet(self, pet: Pet) -> None:
        """Register a pet with this owner."""
        self.pets.append(pet)

    def remove_pet(self, pet_name: str) -> None:
        """Unregister a pet by name."""
        self.pets = [p for p in self.pets if p.name != pet_name]

    # -- Task access (used by Scheduler) -----------------------------------

    def get_all_tasks(self) -> list[tuple[Pet, Task]]:
        """Return every (Pet, Task) pair across all registered pets."""
        return [(pet, task) for pet in self.pets for task in pet.tasks]

    def get_pending_tasks(self) -> list[tuple[Pet, Task]]:
        """Return only incomplete (Pet, Task) pairs across all pets."""
        return [(pet, task) for pet, task in self.get_all_tasks() if not task.completed]

    # -- Constraint helpers ------------------------------------------------

    def add_constraint(self, key: str, value) -> None:
        """Store an arbitrary scheduling constraint (e.g. no_walks_before='8am')."""
        self.preferences[key] = value

    def update_preferences(self, key: str, value) -> None:
        """Update a named preference."""
        self.preferences[key] = value

    def get_available_slots(self) -> list[str]:
        """Return the time-of-day slots the owner can use, adjusted by energy level."""
        slots = list(self.preferred_times)
        if self.energy_level == "low":
            slots = [s for s in slots if s != "morning"]
        elif self.energy_level == "high" and "afternoon" not in slots:
            slots.append("afternoon")
        return slots or ["anytime"]

    def __repr__(self) -> str:
        """Return a compact string showing the owner's name, pet count, budget, and energy level."""
        return (
            f"Owner({self.name!r}, {len(self.pets)} pets, "
            f"{self.available_minutes}min available, energy={self.energy_level})"
        )


# ---------------------------------------------------------------------------
# Scheduler
# ---------------------------------------------------------------------------

class Scheduler:
    """
    The brain of PawPal+.

    Talks to Owner.get_pending_tasks() to retrieve all (Pet, Task) pairs,
    ranks them by priority and preferred time, then fits as many as possible
    within the owner's available_minutes budget.

    How Scheduler talks to Owner:
        pairs = self.owner.get_pending_tasks()   # [(Pet, Task), ...]
    This keeps the Scheduler decoupled — it never touches pets directly.
    """

    TIME_ORDER = ["morning", "afternoon", "evening", "anytime"]

    def __init__(self, owner: Owner, date: Optional[str] = None):
        """Initialize the Scheduler with an Owner and an optional date string (defaults to today)."""
        self.owner = owner
        self.date = date or str(Date.today())
        self.scheduled: list[dict] = []   # {"pet": Pet, "task": Task, "time_slot": str}
        self.skipped: list[dict] = []     # {"pet": Pet, "task": Task, "reason": str}
        self._time_used: int = 0

    # -- Internal helpers --------------------------------------------------

    def _collect_tasks(self) -> list[tuple[Pet, Task]]:
        """Fetch all pending (Pet, Task) pairs from the Owner — the sole entry point to pet data."""
        return self.owner.get_pending_tasks()

    def _rank_tasks(
        self, tasks: list[tuple[Pet, Task]]
    ) -> list[tuple[Pet, Task]]:
        """Sort tasks by descending priority score, then by how well their time slot fits the owner."""
        available_slots = self.owner.get_available_slots()

        def sort_key(pair: tuple[Pet, Task]):
            _, task = pair
            # Prefer tasks whose preferred slot matches an owner-available slot
            slot_match = 0 if task.preferred_time_of_day in available_slots else 1
            time_rank = (
                self.TIME_ORDER.index(task.preferred_time_of_day)
                if task.preferred_time_of_day in self.TIME_ORDER
                else len(self.TIME_ORDER)
            )
            return (-task.get_priority_score(), slot_match, time_rank)

        return sorted(tasks, key=sort_key)

    def _assign_slot(self, task: Task) -> str:
        """Return the task's preferred time slot if the owner is free then, otherwise the first available slot."""
        available = self.owner.get_available_slots()
        if task.preferred_time_of_day in available:
            return task.preferred_time_of_day
        return available[0] if available else "anytime"

    # -- Public API --------------------------------------------------------

    def generate_plan(self) -> None:
        """Rank all pending tasks by priority and greedily schedule them within the owner's time budget."""
        self.scheduled = []
        self.skipped = []
        self._time_used = 0
        budget = self.owner.available_minutes

        for pet, task in self._rank_tasks(self._collect_tasks()):
            if self._time_used + task.duration_minutes <= budget:
                slot = self._assign_slot(task)
                self.scheduled.append({"pet": pet, "task": task, "time_slot": slot})
                self._time_used += task.duration_minutes
            else:
                remaining = budget - self._time_used
                reason = (
                    f"Only {remaining} min left in budget; "
                    f"task needs {task.duration_minutes} min"
                )
                self.skipped.append({"pet": pet, "task": task, "reason": reason})

    def explain_plan(self) -> str:
        """Return a human-readable narrative grouping scheduled tasks by slot and listing skipped tasks."""
        if not self.scheduled and not self.skipped:
            return "No plan generated yet — call generate_plan() first."

        lines = [
            f"Daily Care Plan for {self.owner.name}  |  {self.date}",
            "=" * 55,
        ]

        for slot in self.TIME_ORDER:
            slot_entries = [e for e in self.scheduled if e["time_slot"] == slot]
            if slot_entries:
                lines.append(f"\n{slot.capitalize()}:")
                for entry in slot_entries:
                    lines.append(
                        f"  • [{entry['pet'].name}] {entry['task'].name}"
                        f" — {entry['task'].duration_minutes} min"
                        f" ({entry['task'].priority} priority)"
                    )
                    if entry["task"].notes:
                        lines.append(f"      note: {entry['task'].notes}")

        lines.append(
            f"\nTime used: {self._time_used} / {self.owner.available_minutes} min"
        )

        if self.skipped:
            lines.append("\nSkipped (not enough time):")
            for entry in self.skipped:
                lines.append(
                    f"  x [{entry['pet'].name}] {entry['task'].name}"
                    f" -- {entry['reason']}"
                )

        return "\n".join(lines)

    def get_summary(self) -> dict:
        """Return a structured dict summary of the plan for use by the Streamlit UI."""
        return {
            "date": self.date,
            "owner": self.owner.name,
            "pets": [p.name for p in self.owner.pets],
            "total_minutes_available": self.owner.available_minutes,
            "total_minutes_scheduled": self._time_used,
            "tasks_scheduled": len(self.scheduled),
            "tasks_skipped": len(self.skipped),
            "scheduled": [
                {
                    "pet": e["pet"].name,
                    "task": e["task"].name,
                    "category": e["task"].category,
                    "duration_minutes": e["task"].duration_minutes,
                    "priority": e["task"].priority,
                    "time_slot": e["time_slot"],
                    "notes": e["task"].notes,
                }
                for e in self.scheduled
            ],
            "skipped": [
                {
                    "pet": e["pet"].name,
                    "task": e["task"].name,
                    "duration_minutes": e["task"].duration_minutes,
                    "priority": e["task"].priority,
                    "reason": e["reason"],
                }
                for e in self.skipped
            ],
        }

    def mark_task_done(self, task_name: str) -> bool:
        """Find a scheduled task by name, mark it complete, and return True; return False if not found."""
        for entry in self.scheduled:
            if entry["task"].name == task_name:
                entry["task"].mark_complete()
                return True
        return False

    def __repr__(self) -> str:
        """Return a compact string showing the owner, date, and scheduled/skipped task counts."""
        return (
            f"Scheduler(owner={self.owner.name!r}, date={self.date}, "
            f"scheduled={len(self.scheduled)}, skipped={len(self.skipped)})"
        )
