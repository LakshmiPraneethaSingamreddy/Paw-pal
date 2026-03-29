from datetime import date, time, timedelta

from pawpal_system import AvailabilityWindow, CareTask, Frequency, Pet, PetCareApp, TaskCategory


def _build_owner_with_pet(app: PetCareApp):
	owner = app.create_owner_profile()
	today = date.today()
	owner.availability_windows.append(
		AvailabilityWindow(
			day_of_week=today.weekday(),
			start_time=time(hour=6, minute=0),
			end_time=time(hour=22, minute=0),
		)
	)

	pet = Pet(name="Buddy", species="Dog", age_years=4, weight_kg=24.0)
	app.save_pet_info(owner.owner_id, pet)
	return owner, pet, today


def test_mark_task_completion_updates_schedule_item_status():
	app = PetCareApp()
	owner, pet, today = _build_owner_with_pet(app)

	owner.add_task(
		pet.pet_id,
		CareTask(
			title="Morning Walk",
			category=TaskCategory.WALKING,
			duration_min=30,
			priority=9,
			earliest_start=time(hour=7, minute=0),
			latest_end=time(hour=10, minute=0),
		),
	)

	schedule = app.run_daily_planning(owner.owner_id, today)
	assert schedule.items

	item_id = schedule.items[0].item_id
	assert schedule.items[0].completed is False
	assert schedule.items[0].completed_at is None

	app.mark_task_completion(owner.owner_id, today, item_id, completed=True)

	updated_schedule = app.schedules_by_owner_date[(owner.owner_id, today)]
	updated_item = next(item for item in updated_schedule.items if item.item_id == item_id)
	assert updated_item.completed is True
	assert updated_item.completed_at is not None


def test_add_task_increases_pet_task_count():
	app = PetCareApp()
	owner, pet, _ = _build_owner_with_pet(app)

	initial_count = len(pet.tasks)

	owner.add_task(
		pet.pet_id,
		CareTask(
			title="Breakfast",
			category=TaskCategory.FEEDING,
			duration_min=15,
			priority=10,
			earliest_start=time(hour=8, minute=0),
			latest_end=time(hour=9, minute=30),
		),
	)

	assert len(pet.tasks) == initial_count + 1


def test_scheduler_respects_time_windows_for_morning_tasks():
	app = PetCareApp()
	owner, pet, today = _build_owner_with_pet(app)

	owner.add_task(
		pet.pet_id,
		CareTask(
			title="Morning walk",
			category=TaskCategory.WALKING,
			duration_min=20,
			priority=3,
			frequency=Frequency.DAILY,
			earliest_start=time(hour=8, minute=0),
			latest_end=time(hour=10, minute=0),
		),
	)
	owner.add_task(
		pet.pet_id,
		CareTask(
			title="Feed breakfast",
			category=TaskCategory.FEEDING,
			duration_min=20,
			priority=3,
			frequency=Frequency.DAILY,
			earliest_start=time(hour=8, minute=30),
			latest_end=time(hour=9, minute=30),
		),
	)
	owner.add_task(
		pet.pet_id,
		CareTask(
			title="Playdate",
			category=TaskCategory.PLAY,
			duration_min=60,
			priority=2,
			frequency=Frequency.CUSTOM,
			earliest_start=time(hour=8, minute=0),
			latest_end=time(hour=9, minute=30),
		),
	)
	owner.add_task(
		pet.pet_id,
		CareTask(
			title="Vet appointment",
			category=TaskCategory.VET,
			duration_min=120,
			priority=3,
			frequency=Frequency.CUSTOM,
			earliest_start=time(hour=12, minute=0),
			latest_end=time(hour=14, minute=0),
		),
	)

	schedule = app.run_daily_planning(owner.owner_id, today)
	assert schedule.items

	for item in schedule.items:
		assert item.task is not None
		assert item.end_time is not None
		# Non-flexible tasks must respect deadline; flexible tasks can overflow
		if item.task.latest_end is not None and not item.task.is_flexible:
			assert item.end_time.time() <= item.task.latest_end

	morning_tasks = {"Morning walk", "Feed breakfast", "Playdate"}
	for item in schedule.items:
		if item.task and item.task.title in morning_tasks:
			assert item.end_time is not None
			assert item.end_time.time() <= time(hour=10, minute=0)


def test_scheduler_provides_specific_decision_explanations():
	app = PetCareApp()
	owner, pet, today = _build_owner_with_pet(app)

	owner.add_task(
		pet.pet_id,
		CareTask(
			title="Breakfast",
			category=TaskCategory.FEEDING,
			duration_min=20,
			priority=3,
			earliest_start=time(hour=8, minute=0),
			latest_end=time(hour=9, minute=0),
		),
	)
	owner.add_task(
		pet.pet_id,
		CareTask(
			title="Long Grooming",
			category=TaskCategory.GROOMING,
			duration_min=180,
						is_flexible=False,
			priority=2,
			earliest_start=time(hour=8, minute=0),
			latest_end=time(hour=9, minute=30),
		),
	)

	schedule = app.run_daily_planning(owner.owner_id, today)
	assert schedule.explanations

	messages = [explanation.message for explanation in schedule.explanations]
	assert any("Placed 'Breakfast'" in message for message in messages)
	assert any("Skipped 'Long Grooming'" in message for message in messages)

	breakfast_item = next(item for item in schedule.items if item.task and item.task.title == "Breakfast")
	assert breakfast_item.reason_code != "window_aware_priority"
	assert breakfast_item.reason_code != ""


def test_scheduler_prioritizes_high_priority_over_low_with_backtracking():
	app = PetCareApp()
	owner, pet, today = _build_owner_with_pet(app)

	owner.add_task(
		pet.pet_id,
		CareTask(
			title="Play with mochi",
			category=TaskCategory.PLAY,
			duration_min=60,
			priority=1,
			is_flexible=True,
			earliest_start=time(hour=8, minute=0),
			latest_end=time(hour=10, minute=0),
		),
	)
	owner.add_task(
		pet.pet_id,
		CareTask(
			title="buy mochi ice cream",
			category=TaskCategory.FEEDING,
			duration_min=20,
			priority=1,
			is_flexible=True,
			earliest_start=time(hour=8, minute=0),
			latest_end=time(hour=10, minute=0),
		),
	)
	owner.add_task(
		pet.pet_id,
		CareTask(
			title="take mochi to vet",
			category=TaskCategory.VET,
			duration_min=40,
			priority=3,
			is_flexible=False,
			earliest_start=time(hour=8, minute=0),
			latest_end=time(hour=10, minute=30),
		),
	)

	schedule = app.run_daily_planning(owner.owner_id, today)
	assert schedule.items

	scheduled_titles = {item.task.title for item in schedule.items if item.task}
	assert "take mochi to vet" in scheduled_titles, "High-priority vet task should be scheduled"

	messages = [explanation.message.lower() for explanation in schedule.explanations]
	assert any("vet" in msg or "defer" in msg for msg in messages), \
		"Explanations should mention vet task or deferring"


def test_scheduler_defers_flexible_tasks_over_removing_them():
	app = PetCareApp()
	owner, pet, today = _build_owner_with_pet(app)

	owner.add_task(
		pet.pet_id,
		CareTask(
			title="Flexible playtime",
			category=TaskCategory.PLAY,
			duration_min=60,
			priority=1,
			is_flexible=True,
			earliest_start=time(hour=8, minute=0),
			latest_end=time(hour=18, minute=0),
		),
	)
	owner.add_task(
		pet.pet_id,
		CareTask(
			title="Crucial vet appointment",
			category=TaskCategory.VET,
			duration_min=40,
			priority=3,
			is_flexible=False,
			earliest_start=time(hour=8, minute=0),
			latest_end=time(hour=10, minute=0),
		),
	)

	schedule = app.run_daily_planning(owner.owner_id, today)
	assert len(schedule.items) == 2, "Both tasks should be scheduled"

	scheduled_titles = [item.task.title if item.task else "" for item in schedule.items]
	assert "Flexible playtime" in scheduled_titles
	assert "Crucial vet appointment" in scheduled_titles

	vet_item = next(item for item in schedule.items if item.task and item.task.title == "Crucial vet appointment")
	play_item = next(item for item in schedule.items if item.task and item.task.title == "Flexible playtime")

	assert vet_item.start_time < play_item.start_time, "Non-flexible vet should be scheduled before flexible playtime"

	messages = [explanation.message.lower() for explanation in schedule.explanations]
	assert any("defer" in msg for msg in messages), "Should mention deferring flexible tasks"


def test_scheduler_non_flexible_tasks_prioritized_in_ordering():
	app = PetCareApp()
	owner, pet, today = _build_owner_with_pet(app)

	owner.add_task(
		pet.pet_id,
		CareTask(
			title="Flexible low-priority task",
			category=TaskCategory.PLAY,
			duration_min=30,
			priority=1,
			is_flexible=True,
			earliest_start=time(hour=8, minute=0),
			latest_end=time(hour=20, minute=0),
		),
	)
	owner.add_task(
		pet.pet_id,
		CareTask(
			title="Non-flexible medium-priority task",
			category=TaskCategory.FEEDING,
			duration_min=20,
			priority=2,
			is_flexible=False,
			earliest_start=time(hour=8, minute=0),
			latest_end=time(hour=10, minute=0),
		),
	)

	schedule = app.run_daily_planning(owner.owner_id, today)
	assert len(schedule.items) == 2, f"Expected 2 items, got {len(schedule.items)}"

	feeding_item = next((item for item in schedule.items if item.task and item.task.title == "Non-flexible medium-priority task"), None)
	play_item = next((item for item in schedule.items if item.task and item.task.title == "Flexible low-priority task"), None)

	assert feeding_item is not None, "Non-flexible feeding task should be scheduled"
	assert play_item is not None, "Flexible play task should be scheduled"
	assert feeding_item.start_time < play_item.start_time, \
		"Non-flexible task should be scheduled before flexible task regardless of priority"


def test_weekly_task_schedules_only_on_matching_weekday():
	app = PetCareApp()
	owner, pet, today = _build_owner_with_pet(app)

	owner.add_task(
		pet.pet_id,
		CareTask(
			title="Weekly grooming",
			category=TaskCategory.GROOMING,
			duration_min=30,
			priority=2,
			frequency=Frequency.WEEKLY,
			weekly_day_of_week=today.weekday(),
			earliest_start=time(hour=8, minute=0),
			latest_end=time(hour=12, minute=0),
		),
	)

	today_schedule = app.run_daily_planning(owner.owner_id, today)
	assert any(item.task and item.task.title == "Weekly grooming" for item in today_schedule.items)

	next_day = today + timedelta(days=1)
	next_day_schedule = app.run_daily_planning(owner.owner_id, next_day)
	assert not any(item.task and item.task.title == "Weekly grooming" for item in next_day_schedule.items)


def test_custom_interval_task_schedules_on_interval_days_only():
	app = PetCareApp()
	owner, pet, today = _build_owner_with_pet(app)
	owner.availability_windows.append(
		AvailabilityWindow(
			day_of_week=(today + timedelta(days=1)).weekday(),
			start_time=time(hour=6, minute=0),
			end_time=time(hour=22, minute=0),
		)
	)
	owner.availability_windows.append(
		AvailabilityWindow(
			day_of_week=(today + timedelta(days=2)).weekday(),
			start_time=time(hour=6, minute=0),
			end_time=time(hour=22, minute=0),
		)
	)

	owner.add_task(
		pet.pet_id,
		CareTask(
			title="Custom meds",
			category=TaskCategory.MEDICATION,
			duration_min=15,
			priority=3,
			frequency=Frequency.CUSTOM,
			custom_interval_days=2,
			custom_anchor_date=today,
			earliest_start=time(hour=9, minute=0),
			latest_end=time(hour=11, minute=0),
		),
	)

	today_schedule = app.run_daily_planning(owner.owner_id, today)
	assert any(item.task and item.task.title == "Custom meds" for item in today_schedule.items)

	day_plus_one_schedule = app.run_daily_planning(owner.owner_id, today + timedelta(days=1))
	assert not any(item.task and item.task.title == "Custom meds" for item in day_plus_one_schedule.items)

	day_plus_two_schedule = app.run_daily_planning(owner.owner_id, today + timedelta(days=2))
	assert any(item.task and item.task.title == "Custom meds" for item in day_plus_two_schedule.items)


def test_scheduler_uses_fallback_availability_for_unconfigured_weekday():
	app = PetCareApp()
	owner, pet, today = _build_owner_with_pet(app)

	# Only today's weekday is configured by helper. Schedule for next day should still work.
	next_day = today + timedelta(days=1)

	owner.add_task(
		pet.pet_id,
		CareTask(
			title="Daily fallback walk",
			category=TaskCategory.WALKING,
			duration_min=20,
			priority=2,
			frequency=Frequency.DAILY,
			earliest_start=time(hour=8, minute=0),
			latest_end=time(hour=10, minute=0),
		),
	)

	schedule = app.run_daily_planning(owner.owner_id, next_day)
	assert any(item.task and item.task.title == "Daily fallback walk" for item in schedule.items)
	assert any(
		explanation.rule_applied == "availability_fallback_window"
		for explanation in schedule.explanations
	)
