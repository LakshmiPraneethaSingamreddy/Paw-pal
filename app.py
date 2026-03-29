"""PawPal+ Streamlit UI for owner/pet setup, task management, and daily scheduling.

This app now supports filtered and time-sorted task views, inline task edit/remove actions,
and recurrence-aware task creation (daily, weekly, and custom patterns).
It also persists generated schedules in session state, lets owners mark tasks complete,
and shows read-only conflict warnings when scheduled items overlap.
"""

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

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="wide")

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
pet_by_id = {pet.pet_id: pet for pet in existing_pets}
if "pet_form_mode" not in st.session_state:
    st.session_state.pet_form_mode = "add"
if "selected_pet_option_id" not in st.session_state:
    st.session_state.selected_pet_option_id = st.session_state.pet_id

pet_choice_ids = [None] + [pet.pet_id for pet in existing_pets]
if st.session_state.selected_pet_option_id not in pet_choice_ids:
    st.session_state.selected_pet_option_id = st.session_state.pet_id if st.session_state.pet_id in pet_choice_ids else None

def _pet_option_label(pet_id):
    """Return a readable dropdown label for pet selection options."""
    if pet_id is None:
        return "Select a pet"
    pet = pet_by_id.get(pet_id)
    if pet is None:
        return "Unknown pet"
    return f"{pet.name or 'Unnamed'} ({pet.species or 'unknown'})"

selected_pet_id = st.selectbox(
    "Pets",
    options=pet_choice_ids,
    format_func=_pet_option_label,
    key="selected_pet_option_id",
)

if selected_pet_id != st.session_state.pet_id:
    st.session_state.pet_id = selected_pet_id

selected_pet = pet_by_id.get(selected_pet_id)

pet_action_col1, pet_action_col2 = st.columns(2)
with pet_action_col1:
    if st.button("Add new pet"):
        st.session_state.pet_form_mode = "add"
with pet_action_col2:
    if st.button("Edit selected pet"):
        if selected_pet is None:
            st.error("Select a pet from the dropdown before editing.")
        else:
            st.session_state.pet_form_mode = "edit"

if st.session_state.pet_form_mode == "add":
    st.markdown("### Add Pet")
    add_col1, add_col2 = st.columns(2)
    with add_col1:
        add_pet_name = st.text_input("Pet name", value="Mochi")
        add_species = st.selectbox("Species", ["dog", "cat", "other"], index=0)
        add_pet_age = st.number_input("Age (years)", min_value=0, max_value=50, value=2)
    with add_col2:
        add_pet_height = st.number_input("Height (cm)", min_value=0.0, max_value=300.0, value=35.0)
        add_pet_weight = st.number_input("Weight (kg)", min_value=0.0, max_value=250.0, value=6.5)

    if st.button("Save new pet"):
        new_pet = Pet(
            name=add_pet_name,
            species=add_species,
            age_years=int(add_pet_age),
            height_cm=float(add_pet_height),
            weight_kg=float(add_pet_weight),
        )
        st.session_state.petcare_app.save_pet_info(st.session_state.owner_id, new_pet)
        st.session_state.pet_id = new_pet.pet_id
        st.session_state.selected_pet_for_filter = new_pet.pet_id
        st.session_state.pet_form_mode = "edit"
        st.session_state.petcare_app.save_owner_info(owner)
        st.success("New pet added.")
        st.rerun()
else:
    st.markdown("### Edit Pet")
    if selected_pet is None:
        st.info("Select a pet in the dropdown, then click 'Edit selected pet'.")
    else:
        key_suffix = str(selected_pet.pet_id)
        selected_species = selected_pet.species if selected_pet.species in ["dog", "cat", "other"] else "other"
        edit_col1, edit_col2 = st.columns(2)
        with edit_col1:
            edit_pet_name = st.text_input("Pet name", value=selected_pet.name, key=f"edit_pet_name_{key_suffix}")
            edit_species = st.selectbox(
                "Species",
                ["dog", "cat", "other"],
                index=["dog", "cat", "other"].index(selected_species),
                key=f"edit_species_{key_suffix}",
            )
            edit_pet_age = st.number_input(
                "Age (years)",
                min_value=0,
                max_value=50,
                value=int(selected_pet.age_years),
                key=f"edit_pet_age_{key_suffix}",
            )
        with edit_col2:
            edit_pet_height = st.number_input(
                "Height (cm)",
                min_value=0.0,
                max_value=300.0,
                value=float(selected_pet.height_cm),
                key=f"edit_pet_height_{key_suffix}",
            )
            edit_pet_weight = st.number_input(
                "Weight (kg)",
                min_value=0.0,
                max_value=250.0,
                value=float(selected_pet.weight_kg),
                key=f"edit_pet_weight_{key_suffix}",
            )

        edit_save_col, edit_delete_col = st.columns(2)
        with edit_save_col:
            update_pet_clicked = st.button("Save pet changes")
        with edit_delete_col:
            delete_pet_clicked = st.button("Delete pet")

        if update_pet_clicked:
            selected_pet.name = edit_pet_name
            selected_pet.species = edit_species
            selected_pet.age_years = int(edit_pet_age)
            selected_pet.height_cm = float(edit_pet_height)
            selected_pet.weight_kg = float(edit_pet_weight)
            st.session_state.pet_id = selected_pet.pet_id
            st.session_state.petcare_app.save_owner_info(owner)
            st.success("Pet profile updated.")
            st.rerun()

        if delete_pet_clicked:
            owner.remove_pet(selected_pet.pet_id)
            if st.session_state.pet_id == selected_pet.pet_id:
                st.session_state.pet_id = None
            st.session_state.selected_pet_option_id = None
            st.session_state.petcare_app.save_owner_info(owner)
            st.success("Pet deleted.")
            st.rerun()

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

if st.button("Save owner settings"):
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
        st.session_state.petcare_app.save_owner_info(owner)
        st.success("Owner preferences and availability saved.")

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

weekday_labels = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
weekly_day_of_week: int | None = None
custom_days_of_week: list[int] = []
custom_interval_days: int | None = None
custom_anchor_date = None

if task_frequency == Frequency.WEEKLY.name:
    weekly_day_label = st.selectbox(
        "Weekly day",
        options=weekday_labels,
        index=date.today().weekday(),
    )
    weekly_day_of_week = weekday_labels.index(weekly_day_label)
elif task_frequency == Frequency.CUSTOM.name:
    custom_mode = st.selectbox(
        "Custom recurrence mode",
        options=["Selected weekdays", "Every N days"],
    )
    if custom_mode == "Selected weekdays":
        selected_custom_days = st.multiselect(
            "Custom weekdays",
            options=weekday_labels,
            default=[weekday_labels[date.today().weekday()]],
        )
        custom_days_of_week = [weekday_labels.index(day) for day in selected_custom_days]
    else:
        custom_interval_days = st.number_input(
            "Repeat every N days",
            min_value=1,
            max_value=90,
            value=2,
        )
        custom_anchor_date = st.date_input("Custom recurrence anchor date", value=date.today())

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
            weekly_day_of_week=weekly_day_of_week,
            custom_days_of_week=custom_days_of_week,
            custom_interval_days=int(custom_interval_days) if custom_interval_days is not None else None,
            custom_anchor_date=custom_anchor_date,
            earliest_start=earliest_start,
            latest_end=latest_end,
            is_flexible=is_flexible,
            notes=task_notes,
        )
        owner.add_task(target_pet_id, task)
        st.session_state.pet_id = target_pet_id
        st.session_state.petcare_app.save_owner_info(owner)
        st.success("Task added.")

st.markdown("### View and Filter Tasks")

# Gather all tasks from all pets with pet name metadata
all_tasks_with_pets = []
for pet in owner.pets:
    for task in pet.tasks:
        all_tasks_with_pets.append((pet, task))

if all_tasks_with_pets:
    # Filter controls
    filter_col1, filter_col2 = st.columns(2)
    with filter_col1:
        pet_filter_options = ["All Pets"] + [pet.name or f"Pet {idx}" for idx, pet in enumerate(owner.pets)]
        
        # Initialize filter in session state if not present
        if "task_view_pet_filter" not in st.session_state:
            st.session_state.task_view_pet_filter = "All Pets"
        
        selected_pet_filter = st.selectbox(
            "Filter by pet",
            options=pet_filter_options,
            key="task_view_pet_filter"
        )
    
    with filter_col2:
        # Initialize flexibility filter in session state if not present
        if "task_view_flexibility_filter" not in st.session_state:
            st.session_state.task_view_flexibility_filter = "All Tasks"
        
        flexibility_filter = st.selectbox(
            "Filter by flexibility",
            options=["All Tasks", "Flexible Only", "Non-flexible Only"],
            key="task_view_flexibility_filter"
        )
    
    # Apply filters (display-only, non-mutating)
    filtered_tasks_with_pets = all_tasks_with_pets.copy()
    
    # Pet filter
    if selected_pet_filter != "All Pets":
        selected_pet_idx = pet_filter_options.index(selected_pet_filter) - 1
        filtered_pet_id = owner.pets[selected_pet_idx].pet_id
        filtered_tasks_with_pets = [
            (p, t) for p, t in filtered_tasks_with_pets
            if p.pet_id == filtered_pet_id
        ]
    
    # Flexibility filter
    if flexibility_filter == "Flexible Only":
        filtered_tasks_with_pets = [(p, t) for p, t in filtered_tasks_with_pets if t.is_flexible]
    elif flexibility_filter == "Non-flexible Only":
        filtered_tasks_with_pets = [(p, t) for p, t in filtered_tasks_with_pets if not t.is_flexible]
    
    # Sort filtered tasks
    def _task_display_sort_key(task: CareTask) -> tuple[int, time, int, str]:
        """Sort tasks by start-time presence, start time, priority (desc), then title."""
        start = task.earliest_start if task.earliest_start is not None else time(hour=23, minute=59)
        has_no_start = 1 if task.earliest_start is None else 0
        return (has_no_start, start, -task.priority, task.title.lower())
    
    sorted_filtered = sorted(filtered_tasks_with_pets, key=lambda pair: _task_display_sort_key(pair[1]))
    
    st.write(f"Current tasks: ({len(sorted_filtered)} showing)")
    if "editing_task_id" not in st.session_state:
        st.session_state.editing_task_id = None

    priority_to_label = {1: "low", 2: "medium", 3: "high"}
    label_to_priority = {"low": 1, "medium": 2, "high": 3}

    header_cols = st.columns([1.2, 1.8, 1.0, 0.8, 0.9, 0.9, 1.6, 0.9, 0.8, 0.9, 1.1, 1.3])
    header_labels = [
        "Pet",
        "Title",
        "Category",
        "Mins",
        "Priority",
        "Freq",
        "Recurrence",
        "Start",
        "End",
        "Flexible",
        "Edit",
        "Remove",
    ]
    for col, label in zip(header_cols, header_labels):
        with col:
            st.caption(f"**{label}**")

    for pet, task in sorted_filtered:
        recurrence_text = (
            f"weekly:{weekday_labels[task.weekly_day_of_week]}"
            if task.frequency == Frequency.WEEKLY and task.weekly_day_of_week is not None
            else (
                f"{','.join(weekday_labels[day] for day in task.custom_days_of_week)}"
                if task.frequency == Frequency.CUSTOM and task.custom_days_of_week
                else (
                    f"every {task.custom_interval_days} day(s)"
                    if task.frequency == Frequency.CUSTOM and task.custom_interval_days is not None
                    else ""
                )
            )
        )

        row_cols = st.columns([1.2, 1.8, 1.0, 0.8, 0.9, 0.9, 1.6, 0.9, 0.8, 0.9, 1.1, 1.3])
        with row_cols[0]:
            st.write(pet.name or "Unknown")
        with row_cols[1]:
            st.write(task.title)
        with row_cols[2]:
            st.write(task.category.value)
        with row_cols[3]:
            st.write(str(task.duration_min))
        with row_cols[4]:
            st.write(str(task.priority))
        with row_cols[5]:
            st.write(task.frequency.value)
        with row_cols[6]:
            st.write(recurrence_text or "-")
        with row_cols[7]:
            st.write(task.earliest_start.strftime("%H:%M") if task.earliest_start else "-")
        with row_cols[8]:
            st.write(task.latest_end.strftime("%H:%M") if task.latest_end else "-")
        with row_cols[9]:
            st.write("Yes" if task.is_flexible else "No")
        with row_cols[10]:
            if st.button("Edit", key=f"task_row_edit_{task.task_id}"):
                st.session_state.editing_task_id = str(task.task_id)
                st.rerun()
        with row_cols[11]:
            if st.button("Remove", key=f"task_row_remove_{task.task_id}"):
                owner.remove_task(task.task_id)
                st.session_state.petcare_app.save_owner_info(owner)
                if st.session_state.editing_task_id == str(task.task_id):
                    st.session_state.editing_task_id = None
                st.success(f"Removed task '{task.title}'.")
                st.rerun()

        if st.session_state.editing_task_id == str(task.task_id):
            st.markdown(f"Edit task: **{task.title}**")

            edit_col1, edit_col2, edit_col3 = st.columns(3)
            with edit_col1:
                edit_task_title = st.text_input("Task title", value=task.title, key=f"edit_task_title_{task.task_id}")
            with edit_col2:
                edit_duration = st.number_input(
                    "Duration (minutes)",
                    min_value=1,
                    max_value=240,
                    value=int(task.duration_min),
                    key=f"edit_duration_{task.task_id}",
                )
            with edit_col3:
                edit_priority = st.selectbox(
                    "Priority",
                    ["low", "medium", "high"],
                    index=["low", "medium", "high"].index(priority_to_label.get(task.priority, "medium")),
                    key=f"edit_priority_{task.task_id}",
                )

            edit_meta_col1, edit_meta_col2, edit_meta_col3 = st.columns(3)
            with edit_meta_col1:
                edit_task_category = st.selectbox(
                    "Category",
                    options=[category.name for category in TaskCategory],
                    index=[category.name for category in TaskCategory].index(task.category.name),
                    key=f"edit_category_{task.task_id}",
                )
            with edit_meta_col2:
                edit_task_frequency = st.selectbox(
                    "Frequency",
                    options=[freq.name for freq in Frequency],
                    index=[freq.name for freq in Frequency].index(task.frequency.name),
                    key=f"edit_frequency_{task.task_id}",
                )
            with edit_meta_col3:
                edit_is_flexible = st.checkbox(
                    "Flexible task",
                    value=task.is_flexible,
                    key=f"edit_is_flexible_{task.task_id}",
                )

            edit_weekly_day_of_week: int | None = None
            edit_custom_days_of_week: list[int] = []
            edit_custom_interval_days: int | None = None
            edit_custom_anchor_date = None

            if edit_task_frequency == Frequency.WEEKLY.name:
                edit_weekly_day_label = st.selectbox(
                    "Weekly day",
                    options=weekday_labels,
                    index=task.weekly_day_of_week if task.weekly_day_of_week is not None else date.today().weekday(),
                    key=f"edit_weekly_day_of_week_{task.task_id}",
                )
                edit_weekly_day_of_week = weekday_labels.index(edit_weekly_day_label)
            elif edit_task_frequency == Frequency.CUSTOM.name:
                default_custom_mode = "Every N days" if task.custom_interval_days is not None else "Selected weekdays"
                edit_custom_mode = st.selectbox(
                    "Custom recurrence mode",
                    options=["Selected weekdays", "Every N days"],
                    index=["Selected weekdays", "Every N days"].index(default_custom_mode),
                    key=f"edit_custom_mode_{task.task_id}",
                )
                if edit_custom_mode == "Selected weekdays":
                    default_custom_days = (
                        [weekday_labels[day] for day in task.custom_days_of_week]
                        if task.custom_days_of_week
                        else [weekday_labels[date.today().weekday()]]
                    )
                    selected_custom_days = st.multiselect(
                        "Custom weekdays",
                        options=weekday_labels,
                        default=default_custom_days,
                        key=f"edit_custom_days_of_week_{task.task_id}",
                    )
                    edit_custom_days_of_week = [weekday_labels.index(day) for day in selected_custom_days]
                else:
                    edit_custom_interval_days = st.number_input(
                        "Repeat every N days",
                        min_value=1,
                        max_value=90,
                        value=int(task.custom_interval_days or 2),
                        key=f"edit_custom_interval_days_{task.task_id}",
                    )
                    edit_custom_anchor_date = st.date_input(
                        "Custom recurrence anchor date",
                        value=task.custom_anchor_date or date.today(),
                        key=f"edit_custom_anchor_date_{task.task_id}",
                    )

            edit_time_col1, edit_time_col2 = st.columns(2)
            with edit_time_col1:
                edit_earliest_start = st.time_input(
                    "Earliest start",
                    value=task.earliest_start or time(hour=8, minute=0),
                    key=f"edit_earliest_start_{task.task_id}",
                )
            with edit_time_col2:
                edit_latest_end = st.time_input(
                    "Latest end",
                    value=task.latest_end or time(hour=20, minute=0),
                    key=f"edit_latest_end_{task.task_id}",
                )

            edit_task_notes = st.text_area("Task notes", value=task.notes, key=f"edit_task_notes_{task.task_id}")

            action_col1, action_col2 = st.columns(2)
            with action_col1:
                save_edit_clicked = st.button("Save changes", key=f"save_task_edit_{task.task_id}")
            with action_col2:
                cancel_edit_clicked = st.button("Cancel", key=f"cancel_task_edit_{task.task_id}")

            if cancel_edit_clicked:
                st.session_state.editing_task_id = None
                st.rerun()

            if save_edit_clicked:
                if edit_latest_end <= edit_earliest_start:
                    st.error("Task latest end must be after earliest start.")
                elif edit_task_frequency == Frequency.CUSTOM.name and edit_custom_interval_days is None and not edit_custom_days_of_week:
                    st.error("Select at least one custom weekday or use interval mode.")
                else:
                    owner.edit_task(
                        task.task_id,
                        title=edit_task_title,
                        category=TaskCategory[edit_task_category],
                        duration_min=int(edit_duration),
                        priority=label_to_priority[edit_priority],
                        frequency=Frequency[edit_task_frequency],
                        weekly_day_of_week=edit_weekly_day_of_week,
                        custom_days_of_week=edit_custom_days_of_week,
                        custom_interval_days=int(edit_custom_interval_days) if edit_custom_interval_days is not None else None,
                        custom_anchor_date=edit_custom_anchor_date,
                        earliest_start=edit_earliest_start,
                        latest_end=edit_latest_end,
                        is_flexible=edit_is_flexible,
                        notes=edit_task_notes,
                    )
                    st.session_state.petcare_app.save_owner_info(owner)
                    st.session_state.editing_task_id = None
                    st.success(f"Updated task '{edit_task_title}'.")
                    st.rerun()

        st.divider()
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
            # Store schedule in session state for persistence
            st.session_state.last_schedule = schedule
            st.session_state.last_schedule_date = schedule_date
            st.success(f"Schedule generated for {schedule_date.isoformat()}.")
        else:
            st.warning("No tasks could be scheduled. Check pet tasks and owner availability.")

# Display persisted schedule (either from fresh generation or from session state across reruns)
if hasattr(st.session_state, 'last_schedule') and st.session_state.last_schedule is not None:
    if st.session_state.last_schedule_date == schedule_date:
        schedule = st.session_state.last_schedule
        
        st.markdown("### Daily Schedule - Mark tasks as complete")
        
        pet_name_by_id = {pet.pet_id: pet.name or "Unnamed" for pet in owner.pets}
        
        # Display each task with interactive completion checkbox
        for item in sorted(schedule.items, key=lambda x: x.start_time or time(hour=23, minute=59)):
            col1, col2, col3, col4, col5, col6 = st.columns([0.5, 2, 1.5, 1.5, 2, 1])
            
            with col1:
                # Completion checkbox
                completed_state_key = f"complete_{item.item_id}"
                is_completed = st.checkbox(
                    "",
                    value=item.completed,
                    key=completed_state_key,
                    label_visibility="collapsed"
                )
                
                # Update backend if completion status changed
                if is_completed != item.completed:
                    st.session_state.petcare_app.mark_task_completion(
                        owner_id=st.session_state.owner_id,
                        schedule_date=schedule_date,
                        item_id=item.item_id,
                        completed=is_completed
                    )
                    item.completed = is_completed
            
            with col2:
                # Task title with strikethrough styling if completed
                task_title = item.task.title if item.task else "Unknown task"
                if item.completed:
                    st.markdown(f"~~{task_title}~~")
                else:
                    st.write(task_title)
            
            with col3:
                st.write(f"**{pet_name_by_id.get(item.pet_id, 'Unknown Pet')}**")
            
            with col4:
                time_str = ""
                if item.start_time and item.end_time:
                    time_str = f"{item.start_time.strftime('%H:%M')} - {item.end_time.strftime('%H:%M')}"
                st.write(time_str)
            
            with col5:
                st.write(item.reason_code)
            
            with col6:
                if item.completed and item.completed_at:
                    st.caption(f"✓ {item.completed_at.strftime('%H:%M')}")
                else:
                    st.caption("")

        # Read-only conflict detection: highlight overlaps without modifying the schedule.
        sorted_items = sorted(
            [item for item in schedule.items if item.start_time is not None and item.end_time is not None],
            key=lambda schedule_item: schedule_item.start_time,
        )
        conflicts: list[tuple] = []
        for previous_item, current_item in zip(sorted_items, sorted_items[1:]):
            if previous_item.end_time > current_item.start_time:
                conflicts.append((previous_item, current_item))

        if conflicts:
            st.warning(
                f"Detected {len(conflicts)} schedule conflict(s). The app is only warning here; it does not auto-resolve."
            )
            st.markdown("### Conflict details")
            for previous_item, current_item in conflicts:
                previous_task = previous_item.task.title if previous_item.task else "Unknown task"
                current_task = current_item.task.title if current_item.task else "Unknown task"
                previous_pet = pet_name_by_id.get(previous_item.pet_id, "Unknown Pet")
                current_pet = pet_name_by_id.get(current_item.pet_id, "Unknown Pet")
                st.write(
                    "- "
                    f"{previous_pet}: {previous_task} "
                    f"({previous_item.start_time.strftime('%H:%M')} - {previous_item.end_time.strftime('%H:%M')}) overlaps with "
                    f"{current_pet}: {current_task} "
                    f"({current_item.start_time.strftime('%H:%M')} - {current_item.end_time.strftime('%H:%M')})"
                )

        if schedule.explanations:
            st.markdown("### Plan explanation")
            for explanation in schedule.explanations:
                st.write(f"- {explanation.message}")
