"""
tests/test_pawpal.py — Unit tests for PawPal+ logic layer.
Run with:  python -m pytest
"""

import pytest
from pawpal_system import Task, Pet, Owner, Scheduler


# ---------------------------------------------------------------------------
# Fixtures — reusable test objects
# ---------------------------------------------------------------------------

@pytest.fixture
def sample_task():
    return Task(
        name="Morning Walk",
        category="walk",
        duration_minutes=20,
        priority="high",
        preferred_time_of_day="morning",
    )


@pytest.fixture
def sample_pet():
    return Pet(name="Mochi", species="dog", breed="Shiba Inu", age_years=3)


@pytest.fixture
def sample_owner(sample_pet):
    owner = Owner(name="Jordan", available_minutes=60)
    owner.add_pet(sample_pet)
    return owner


# ---------------------------------------------------------------------------
# Test 1 — Task Completion
# ---------------------------------------------------------------------------

def test_mark_complete_changes_status(sample_task):
    """mark_complete() should flip completed from False to True."""
    assert sample_task.completed is False, "Task should start as not completed"
    sample_task.mark_complete()
    assert sample_task.completed is True, "Task should be completed after mark_complete()"


def test_mark_complete_is_idempotent(sample_task):
    """Calling mark_complete() twice should not raise and should stay True."""
    sample_task.mark_complete()
    sample_task.mark_complete()
    assert sample_task.completed is True


# ---------------------------------------------------------------------------
# Test 2 — Task Addition
# ---------------------------------------------------------------------------

def test_add_task_increases_count(sample_pet):
    """add_task() should increase the pet's task list by exactly one."""
    initial_count = len(sample_pet.tasks)
    new_task = Task("Evening Walk", "walk", 20, "high", "evening")
    sample_pet.add_task(new_task)
    assert len(sample_pet.tasks) == initial_count + 1


def test_add_multiple_tasks(sample_pet):
    """Adding three tasks should increase the count by three."""
    initial_count = len(sample_pet.tasks)
    for name in ("Breakfast", "Dinner", "Playtime"):
        sample_pet.add_task(Task(name, "feed", 5, "medium"))
    assert len(sample_pet.tasks) == initial_count + 3


def test_added_task_is_retrievable(sample_pet):
    """The task added to a pet should appear in pet.tasks."""
    task = Task("Grooming", "grooming", 10, "low", "evening")
    sample_pet.add_task(task)
    assert task in sample_pet.tasks


# ---------------------------------------------------------------------------
# Bonus — Scheduler smoke tests
# ---------------------------------------------------------------------------

def test_scheduler_respects_budget(sample_owner, sample_pet):
    """Scheduler should never schedule more minutes than the owner's budget."""
    for i in range(10):
        sample_pet.add_task(Task(f"Task {i}", "enrichment", 15, "medium"))

    scheduler = Scheduler(sample_owner)
    scheduler.generate_plan()
    summary = scheduler.get_summary()

    assert summary["total_minutes_scheduled"] <= sample_owner.available_minutes


def test_scheduler_skips_when_full(sample_owner, sample_pet):
    """When tasks exceed the budget, some should be skipped."""
    # Fill the pet with tasks that together exceed 60 min
    for i in range(6):
        sample_pet.add_task(Task(f"Long Task {i}", "walk", 15, "medium"))

    scheduler = Scheduler(sample_owner)
    scheduler.generate_plan()
    summary = scheduler.get_summary()

    assert summary["tasks_skipped"] > 0, "Some tasks should be skipped when over budget"


# ---------------------------------------------------------------------------
# Test 3 — Sorting Correctness
# ---------------------------------------------------------------------------

def test_sort_by_time_chronological_order(sample_owner, sample_pet):
    """sort_by_time() should return tasks in morning → afternoon → evening → anytime order."""
    # Add tasks intentionally out of order
    sample_pet.add_task(Task("Evening Task",   "enrichment", 10, "low",    "evening"))
    sample_pet.add_task(Task("Morning Task",   "walk",       10, "high",   "morning"))
    sample_pet.add_task(Task("Anytime Task",   "feed",        5, "medium", "anytime"))
    sample_pet.add_task(Task("Afternoon Task", "enrichment", 10, "medium", "afternoon"))

    scheduler = Scheduler(sample_owner)
    scheduler.generate_plan()
    sorted_entries = scheduler.sort_by_time()

    TIME_ORDER = ["morning", "afternoon", "evening", "anytime"]
    slots = [e["time_slot"] for e in sorted_entries]
    # Convert slot names to their index positions and verify the list is non-decreasing
    indices = [TIME_ORDER.index(s) for s in slots]
    assert indices == sorted(indices), f"Tasks not in chronological order: {slots}"


def test_sort_by_time_empty_schedule(sample_owner):
    """sort_by_time() on an empty schedule should return an empty list."""
    scheduler = Scheduler(sample_owner)
    scheduler.generate_plan()
    assert scheduler.sort_by_time() == []


# ---------------------------------------------------------------------------
# Test 4 — Recurrence Logic
# ---------------------------------------------------------------------------

def test_daily_recurrence_creates_next_day_task(sample_pet):
    """Completing a daily recurring task should queue a new task due the following day."""
    from datetime import date, timedelta

    today = date.today()
    daily_task = Task(
        "Daily Walk", "walk", 20, "high", "morning",
        recurrence="daily", due_date=today,
    )
    sample_pet.add_task(daily_task)

    owner = Owner(name="Jordan", available_minutes=120)
    owner.add_pet(sample_pet)
    scheduler = Scheduler(owner)
    scheduler.generate_plan()

    result = scheduler.mark_task_done("Daily Walk")
    assert result is True, "mark_task_done should return True for a scheduled task"

    tomorrow = today + timedelta(days=1)
    next_tasks = [t for t in sample_pet.tasks if t.name == "Daily Walk" and t.due_date == tomorrow]
    assert len(next_tasks) == 1, "A new Daily Walk task due tomorrow should be queued"
    assert next_tasks[0].completed is False, "The next occurrence should start as incomplete"


def test_no_recurrence_does_not_queue_next(sample_pet):
    """Completing a non-recurring task should NOT add any new tasks."""
    task = Task("One-off Groom", "grooming", 10, "low", "evening")
    sample_pet.add_task(task)

    owner = Owner(name="Jordan", available_minutes=120)
    owner.add_pet(sample_pet)
    scheduler = Scheduler(owner)
    scheduler.generate_plan()

    before_count = len(sample_pet.tasks)
    scheduler.mark_task_done("One-off Groom")
    assert len(sample_pet.tasks) == before_count, "Non-recurring task should not spawn a new task"


# ---------------------------------------------------------------------------
# Test 5 — Conflict Detection
# ---------------------------------------------------------------------------

def test_detect_same_pet_conflict(sample_owner, sample_pet):
    """Two tasks of the same category in the same slot for one pet should be flagged."""
    sample_pet.add_task(Task("Morning Walk 1", "walk", 10, "high",   "morning"))
    sample_pet.add_task(Task("Morning Walk 2", "walk", 10, "medium", "morning"))

    scheduler = Scheduler(sample_owner)
    scheduler.generate_plan()
    conflicts = scheduler.detect_conflicts()

    assert any("same pet" in w for w in conflicts), (
        f"Expected a same-pet conflict warning, got: {conflicts}"
    )


def test_detect_cross_pet_conflict():
    """Two different pets with the same category in the same slot should be flagged."""
    pet1 = Pet(name="Mochi", species="dog")
    pet2 = Pet(name="Luna",  species="cat")
    pet1.add_task(Task("Breakfast", "feed", 5, "high", "morning"))
    pet2.add_task(Task("Breakfast", "feed", 5, "high", "morning"))

    owner = Owner(name="Jordan", available_minutes=60)
    owner.add_pet(pet1)
    owner.add_pet(pet2)

    scheduler = Scheduler(owner)
    scheduler.generate_plan()
    conflicts = scheduler.detect_conflicts()

    assert any("cross-pet" in w for w in conflicts), (
        f"Expected a cross-pet conflict warning, got: {conflicts}"
    )
