import streamlit as st
from pawpal_system import Task, Pet, Owner, Scheduler

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

# ---------------------------------------------------------------------------
# Session state vault
# Pattern: if key is absent → create once; every rerun after → skip and reuse.
# owner.pets is the single source of truth for pets — no separate list needed.
# ---------------------------------------------------------------------------

if "owner" not in st.session_state:
    st.session_state.owner = Owner(name="", available_minutes=60)

if "schedule" not in st.session_state:
    st.session_state.schedule = None

if "explanation" not in st.session_state:
    st.session_state.explanation = ""

if "scheduler" not in st.session_state:
    st.session_state.scheduler = None

# Alias — mutating `owner` mutates st.session_state.owner (same object in memory)
owner: Owner = st.session_state.owner

# ---------------------------------------------------------------------------
# Section 1 — Owner profile
# ---------------------------------------------------------------------------

st.subheader("Owner Profile")

col_name, col_time, col_energy = st.columns(3)
with col_name:
    owner_name = st.text_input("Your name", value=owner.name or "Jordan")
with col_time:
    available_minutes = st.number_input(
        "Time available today (min)", min_value=10, max_value=480,
        value=owner.available_minutes,
    )
with col_energy:
    energy_level = st.selectbox(
        "Energy level", ["low", "medium", "high"],
        index=["low", "medium", "high"].index(owner.energy_level),
    )

if st.button("Save owner profile"):
    # Directly mutate the owner object that lives in session state
    owner.name = owner_name
    owner.available_minutes = available_minutes
    owner.energy_level = energy_level
    st.success(f"Profile saved for {owner.name}.")

st.divider()

# ---------------------------------------------------------------------------
# Section 2 — Add a pet
#
# When the form is submitted:
#   1. Pet(...) constructs the data object
#   2. pet.get_care_requirements() populates its default task list
#   3. owner.add_pet(pet) registers it — owner.pets is the only list we keep
#
# UI update: after the rerun, owner.pets has the new pet, so the list below
# renders it automatically.
# ---------------------------------------------------------------------------

st.subheader("Your Pets")

with st.form("add_pet_form", clear_on_submit=True):
    col_pet, col_species = st.columns(2)
    with col_pet:
        pet_name = st.text_input("Pet name", value="Mochi")
    with col_species:
        species = st.selectbox("Species", ["dog", "cat", "other"])
    submitted_pet = st.form_submit_button("Add pet")

if submitted_pet:
    existing_names = [p.name for p in owner.pets]          # owner.pets is the source of truth
    if pet_name in existing_names:
        st.warning(f"{pet_name} is already registered.")
    else:
        new_pet = Pet(name=pet_name, species=species)
        new_pet.tasks = new_pet.get_care_requirements()     # Pet.get_care_requirements()
        owner.add_pet(new_pet)                              # Owner.add_pet()
        st.success(f"Added {pet_name} ({species}) with {len(new_pet.tasks)} default tasks.")

# Render current pet list straight from owner.pets
if owner.pets:
    st.write("Registered pets:")
    for pet in owner.pets:
        st.markdown(f"- **{pet.name}** ({pet.species}) — {len(pet.tasks)} tasks")
else:
    st.info("No pets yet. Add one above.")

st.divider()

# ---------------------------------------------------------------------------
# Section 3 — Add a custom task to a pet
#
# When the form is submitted:
#   1. We look up the target Pet object from owner.pets by name
#   2. Task(...) constructs the task data object
#   3. pet.add_task(task) appends it to that pet's task list
#
# UI update: pet.tasks grows by one; the task count in Section 2 reflects
# this on the next rerun because it reads len(pet.tasks) live.
# ---------------------------------------------------------------------------

st.subheader("Add a Custom Task")

if owner.pets:
    with st.form("add_task_form", clear_on_submit=True):
        pet_options = [p.name for p in owner.pets]
        target_pet_name = st.selectbox("Assign task to pet", pet_options)
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            task_name = st.text_input("Task name", value="Evening walk")
        with col2:
            category = st.selectbox(
                "Category", ["walk", "feed", "med", "enrichment", "grooming"]
            )
        with col3:
            duration = st.number_input("Duration (min)", min_value=1, max_value=240, value=20)
        with col4:
            priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)
        time_slot = st.selectbox(
            "Preferred time", ["morning", "afternoon", "evening", "anytime"]
        )
        notes = st.text_input("Notes (optional)", value="")
        submitted_task = st.form_submit_button("Add task")

    if submitted_task:
        # Look up the Pet object by name from owner.pets
        target_pet = next(p for p in owner.pets if p.name == target_pet_name)
        new_task = Task(task_name, category, int(duration), priority, time_slot, notes=notes)
        target_pet.add_task(new_task)                       # Pet.add_task()
        st.success(f"Added '{task_name}' to {target_pet_name}. They now have {len(target_pet.tasks)} tasks.")
else:
    st.info("Add a pet first, then you can assign tasks to them.")

st.divider()

# ---------------------------------------------------------------------------
# Section 4 — Generate schedule
#
# Scheduler(owner) receives the whole Owner (and through it, all pets+tasks).
# scheduler.generate_plan() runs the priority/budget logic.
# scheduler.get_summary() returns a plain dict the UI can render as a table.
# scheduler.explain_plan() returns the human-readable narrative string.
# ---------------------------------------------------------------------------

st.subheader("Generate Today's Schedule")

if st.button("Generate schedule", type="primary"):
    if not owner.name:
        st.error("Please save an owner profile first.")
    elif not owner.pets:
        st.error("Please add at least one pet before generating a schedule.")
    else:
        scheduler = Scheduler(owner)
        scheduler.generate_plan()
        st.session_state.scheduler = scheduler
        st.session_state.schedule = scheduler.get_summary()
        st.session_state.explanation = scheduler.explain_plan()

if st.session_state.schedule:
    summary = st.session_state.schedule
    scheduler: Scheduler = st.session_state.scheduler

    # --- Budget banner ---
    st.success(
        f"Scheduled **{summary['tasks_scheduled']} tasks** "
        f"({summary['total_minutes_scheduled']} / {summary['total_minutes_available']} min used)"
    )

    # --- Conflict warnings (from Scheduler.detect_conflicts) ---
    conflicts = scheduler.detect_conflicts()
    if conflicts:
        for msg in conflicts:
            st.warning(msg)

    # --- Pet filter (uses Scheduler.filter_tasks) ---
    pet_names = [p.name for p in owner.pets]
    filter_options = ["All pets"] + pet_names
    selected_pet = st.selectbox("Filter by pet", filter_options, key="pet_filter")

    filter_arg = None if selected_pet == "All pets" else selected_pet
    filtered_entries = scheduler.filter_tasks(pet_name=filter_arg)

    # Sort the filtered entries chronologically (Scheduler.sort_by_time order)
    TIME_ORDER = Scheduler.TIME_ORDER
    sorted_entries = sorted(
        filtered_entries,
        key=lambda e: (
            TIME_ORDER.index(e["time_slot"])
            if e["time_slot"] in TIME_ORDER
            else len(TIME_ORDER)
        ),
    )

    # --- Scheduled tasks table (sorted by time slot) ---
    if sorted_entries:
        st.markdown("#### Scheduled Tasks")
        st.table(
            [
                {
                    "Time Slot": e["time_slot"].capitalize(),
                    "Pet": e["pet"].name,
                    "Task": e["task"].name,
                    "Category": e["task"].category,
                    "Duration (min)": e["task"].duration_minutes,
                    "Priority": e["task"].priority,
                    "Notes": e["task"].notes or "—",
                }
                for e in sorted_entries
            ]
        )
    else:
        st.info("No tasks match the current filter.")

    # --- Skipped tasks ---
    if summary["skipped"]:
        st.markdown("#### Skipped (not enough time)")
        st.table(
            [
                {
                    "Pet": row["pet"],
                    "Task": row["task"],
                    "Duration (min)": row["duration_minutes"],
                    "Priority": row["priority"],
                    "Reason": row["reason"],
                }
                for row in summary["skipped"]
            ]
        )

    with st.expander("Why did the scheduler choose this plan?"):
        st.text(st.session_state.explanation)
