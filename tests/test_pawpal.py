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
