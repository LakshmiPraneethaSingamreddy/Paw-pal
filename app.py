import streamlit as st
from datetime import date, time

from pawpal_system import (
    AvailabilityWindow,
    CareTask,
    Frequency,
    OwnerPreference,
    Pet,
    PetCareApp,
    TaskCategory,
)

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

st.markdown(
    """
Welcome to the PawPal+ starter app.

This file is intentionally thin. It gives you a working Streamlit app so you can start quickly,
but **it does not implement the project logic**. Your job is to design the system and build it.

Use this app as your interactive demo once your backend classes/functions exist.
"""
)

with st.expander("Scenario", expanded=True):
    st.markdown(
        """
**PawPal+** is a pet care planning assistant. It helps a pet owner plan care tasks
for their pet(s) based on constraints like time, priority, and preferences.

You will design and implement the scheduling logic and connect it to this Streamlit UI.
"""
    )

with st.expander("What you need to build", expanded=True):
    st.markdown(
        """
At minimum, your system should:
- Represent pet care tasks (what needs to happen, how long it takes, priority)
- Represent the pet and the owner (basic info and preferences)
- Build a plan/schedule for a day that chooses and orders tasks based on constraints
- Explain the plan (why each task was chosen and when it happens)
"""
    )

st.divider()

st.subheader("Owner and Pet Setup")
owner_name = st.text_input("Owner name", value="Jordan")
timezone = st.text_input("Timezone", value="UTC")

if "petcare_app" not in st.session_state:
    st.session_state.petcare_app = PetCareApp()

if "owner_id" not in st.session_state:
    owner = st.session_state.petcare_app.create_owner_profile()
    owner.preference = OwnerPreference(
        max_tasks_per_block=4,
        preferred_task_order="high_to_low_priority",
        avoid_late_night=False,
        notification_lead_min=15,
    )
    owner.availability_windows = []
    st.session_state.petcare_app.save_owner_info(owner)
    st.session_state.owner_id = owner.owner_id

if "pet_id" not in st.session_state:
    st.session_state.pet_id = None

owner = st.session_state.petcare_app.owners_by_id[st.session_state.owner_id]
owner.name = owner_name
owner.timezone = timezone
st.session_state.petcare_app.save_owner_info(owner)

existing_pets = owner.pets
pet_options = {f"{pet.name or 'Unnamed'} ({pet.species or 'unknown'})": pet.pet_id for pet in existing_pets}
selected_pet_label = st.selectbox(
    "Existing pets",
    options=["Create new pet"] + list(pet_options.keys()),
)
selected_pet_id = pet_options.get(selected_pet_label)

selected_pet = next((pet for pet in existing_pets if pet.pet_id == selected_pet_id), None)

pet_name_default = selected_pet.name if selected_pet else "Mochi"
species_default = selected_pet.species if selected_pet and selected_pet.species in ["dog", "cat", "other"] else "dog"
age_default = selected_pet.age_years if selected_pet else 2
height_default = float(selected_pet.height_cm) if selected_pet else 35.0
weight_default = float(selected_pet.weight_kg) if selected_pet else 6.5

pet_name = st.text_input("Pet name", value=pet_name_default)
species = st.selectbox("Species", ["dog", "cat", "other"], index=["dog", "cat", "other"].index(species_default))
pet_age = st.number_input("Age (years)", min_value=0, max_value=50, value=int(age_default))
pet_height = st.number_input("Height (cm)", min_value=0.0, max_value=300.0, value=height_default)
pet_weight = st.number_input("Weight (kg)", min_value=0.0, max_value=250.0, value=weight_default)

pref_col1, pref_col2 = st.columns(2)
with pref_col1:
    max_tasks_per_block = st.number_input("Max tasks per block", min_value=1, max_value=12, value=4)
    preferred_task_order = st.text_input("Preferred task order", value="high_to_low_priority")
with pref_col2:
    late_night_available = st.checkbox("Late-night tasks allowed (after 10 PM)", value=True)
    notification_lead_min = st.number_input("Notification lead (minutes)", min_value=0, max_value=180, value=15)

st.markdown("### Availability Window")
available_days = st.multiselect(
    "Available days",
    options=["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
    default=["Mon", "Tue", "Wed", "Thu", "Fri"],
)
avail_col1, avail_col2 = st.columns(2)
with avail_col1:
    availability_start = st.time_input("Available from", value=time(hour=8, minute=0))
with avail_col2:
    availability_end = st.time_input("Available until", value=time(hour=20, minute=0))

day_to_index = {"Mon": 0, "Tue": 1, "Wed": 2, "Thu": 3, "Fri": 4, "Sat": 5, "Sun": 6}

save_pet_col, delete_pet_col = st.columns(2)
with save_pet_col:
    save_pet_clicked = st.button("Add/Update pet")
with delete_pet_col:
    delete_pet_clicked = st.button("Delete selected pet")

if save_pet_clicked:
    owner.preference = OwnerPreference(
        max_tasks_per_block=int(max_tasks_per_block),
        preferred_task_order=preferred_task_order,
        avoid_late_night=not late_night_available,
        notification_lead_min=int(notification_lead_min),
    )
    if availability_end <= availability_start:
        st.error("Availability end time must be after start time.")
    else:
        owner.availability_windows = [
            AvailabilityWindow(
                day_of_week=day_to_index[day_label],
                start_time=availability_start,
                end_time=availability_end,
            )
            for day_label in available_days
        ]

        if selected_pet is None:
            pet = Pet(
                name=pet_name,
                species=species,
                age_years=int(pet_age),
                height_cm=float(pet_height),
                weight_kg=float(pet_weight),
            )
            st.session_state.petcare_app.save_pet_info(st.session_state.owner_id, pet)
            st.session_state.pet_id = pet.pet_id
        else:
            selected_pet.name = pet_name
            selected_pet.species = species
            selected_pet.age_years = int(pet_age)
            selected_pet.height_cm = float(pet_height)
            selected_pet.weight_kg = float(pet_weight)
            st.session_state.pet_id = selected_pet.pet_id

        st.session_state.petcare_app.save_owner_info(owner)
        st.success("Owner preferences, availability, and pet profile saved.")

if delete_pet_clicked:
    if selected_pet is None:
        st.error("Choose an existing pet to delete.")
    else:
        owner.remove_pet(selected_pet.pet_id)
        if st.session_state.pet_id == selected_pet.pet_id:
            st.session_state.pet_id = None
        st.session_state.petcare_app.save_owner_info(owner)
        st.success("Pet deleted.")

st.markdown("### Tasks")
st.caption("Add a few tasks. In your final version, these should feed into your scheduler.")

col1, col2, col3 = st.columns(3)
with col1:
    task_title = st.text_input("Task title", value="Morning walk")
with col2:
    duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
with col3:
    priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)

task_col1, task_col2, task_col3 = st.columns(3)
with task_col1:
    task_category = st.selectbox("Category", options=[category.name for category in TaskCategory], index=1)
with task_col2:
    task_frequency = st.selectbox("Frequency", options=[freq.name for freq in Frequency], index=0)
with task_col3:
    is_flexible = st.checkbox("Flexible task", value=True)

time_col1, time_col2 = st.columns(2)
with time_col1:
    earliest_start = st.time_input("Earliest start", value=time(hour=8, minute=0))
with time_col2:
    latest_end = st.time_input("Latest end", value=time(hour=20, minute=0))

task_notes = st.text_area("Task notes", value="")

priority_to_score = {"low": 1, "medium": 2, "high": 3}
selected_task_category = TaskCategory[task_category]
selected_task_frequency = Frequency[task_frequency]

if st.button("Add task"):
    target_pet_id = selected_pet_id or st.session_state.pet_id
    if target_pet_id is None:
        st.error("Add a pet first, then add tasks.")
    elif latest_end <= earliest_start:
        st.error("Task latest end must be after earliest start.")
    else:
        task = CareTask(
            title=task_title,
            category=selected_task_category,
            duration_min=int(duration),
            priority=priority_to_score[priority],
            frequency=selected_task_frequency,
            earliest_start=earliest_start,
            latest_end=latest_end,
            is_flexible=is_flexible,
            notes=task_notes,
        )
        owner.add_task(target_pet_id, task)
        st.session_state.pet_id = target_pet_id
        st.session_state.petcare_app.save_owner_info(owner)
        st.success("Task added.")

active_pet_id = selected_pet_id or st.session_state.pet_id
pet = next((current_pet for current_pet in owner.pets if current_pet.pet_id == active_pet_id), None)
if pet and pet.tasks:
    st.write("Current tasks:")
    st.table(
        [
            {
                "title": task.title,
                "category": task.category.value,
                "duration_minutes": task.duration_min,
                "priority": task.priority,
                "frequency": task.frequency.value,
                "earliest_start": task.earliest_start.strftime("%H:%M") if task.earliest_start else "",
                "latest_end": task.latest_end.strftime("%H:%M") if task.latest_end else "",
                "flexible": task.is_flexible,
            }
            for task in pet.tasks
        ]
    )
else:
    st.info("No tasks yet. Add one above.")

st.divider()

st.subheader("Build Schedule")
st.caption("This button should call your scheduling logic once you implement it.")

schedule_date = st.date_input("Schedule date", value=date.today())

if st.button("Generate schedule"):
    if not owner.pets:
        st.error("Add a pet before generating a schedule.")
    elif not owner.availability_windows:
        st.error("Set at least one availability window before generating a schedule.")
    else:
        schedule = st.session_state.petcare_app.run_daily_planning(
            owner_id=st.session_state.owner_id,
            schedule_date=schedule_date,
        )

        if schedule.items:
            st.success(f"Schedule generated for {schedule_date.isoformat()}.")
            st.table(
                [
                    {
                        "task": item.task.title if item.task else "",
                        "start": item.start_time.strftime("%H:%M") if item.start_time else "",
                        "end": item.end_time.strftime("%H:%M") if item.end_time else "",
                        "reason": item.reason_code,
                    }
                    for item in schedule.items
                ]
            )
            if schedule.explanations:
                st.markdown("### Plan explanation")
                for explanation in schedule.explanations:
                    st.write(f"- {explanation.message}")
        else:
            st.warning("No tasks could be scheduled. Check pet tasks and owner availability.")
