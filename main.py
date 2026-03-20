from datetime import date, time

from pawpal_system import (
	AvailabilityWindow,
	CareTask,
	OwnerPreference,
	Pet,
	PetCareApp,
	TaskCategory,
)


def build_demo_data(app: PetCareApp) -> tuple:
	owner = app.create_owner_profile()
	owner.name = "Alex"
	owner.preference = OwnerPreference(
		avoid_late_night=False,
		notification_lead_min=20,
	)

	today = date.today()
	owner.availability_windows.append(
		AvailabilityWindow(
			day_of_week=today.weekday(),
			start_time=time(hour=6, minute=0),
			end_time=time(hour=22, minute=0),
		)
	)

	buddy = Pet(name="Buddy", species="Dog", age_years=4, weight_kg=24.0)
	luna = Pet(name="Luna", species="Cat", age_years=2, weight_kg=5.0)

	app.save_pet_info(owner.owner_id, buddy)
	app.save_pet_info(owner.owner_id, luna)

	owner.add_task(
		buddy.pet_id,
		CareTask(
			title="Morning Walk",
			category=TaskCategory.WALKING,
			duration_min=30,
			priority=9,
			earliest_start=time(hour=7, minute=0),
			latest_end=time(hour=10, minute=0),
		),
	)
	owner.add_task(
		buddy.pet_id,
		CareTask(
			title="Breakfast",
			category=TaskCategory.FEEDING,
			duration_min=15,
			priority=10,
			earliest_start=time(hour=8, minute=0),
			latest_end=time(hour=9, minute=30),
		),
	)
	owner.add_task(
		buddy.pet_id,
		CareTask(
			title="Evening Walk",
			category=TaskCategory.WALKING,
			duration_min=25,
			priority=8,
			earliest_start=time(hour=18, minute=0),
			latest_end=time(hour=20, minute=0),
		),
	)

	owner.add_task(
		luna.pet_id,
		CareTask(
			title="Morning Feed",
			category=TaskCategory.FEEDING,
			duration_min=10,
			priority=9,
			earliest_start=time(hour=7, minute=30),
			latest_end=time(hour=9, minute=0),
		),
	)
	owner.add_task(
		luna.pet_id,
		CareTask(
			title="Play Session",
			category=TaskCategory.PLAY,
			duration_min=20,
			priority=7,
			earliest_start=time(hour=12, minute=0),
			latest_end=time(hour=15, minute=0),
		),
	)
	owner.add_task(
		luna.pet_id,
		CareTask(
			title="Evening Feed",
			category=TaskCategory.FEEDING,
			duration_min=10,
			priority=8,
			earliest_start=time(hour=18, minute=30),
			latest_end=time(hour=20, minute=30),
		),
	)

	return owner, today


def print_todays_schedule(app: PetCareApp, owner_id, today: date) -> None:
	schedule = app.schedules_by_owner_date.get((owner_id, today))
	if schedule is None:
		schedule = app.run_daily_planning(owner_id, today)
	owner = app.owners_by_id[owner_id]
	pet_name_by_id = {pet.pet_id: pet.name for pet in owner.pets}

	print("Today's Schedule")
	print("=" * 40)
	print(f"Date: {today.isoformat()}")
	print(f"Total Planned Minutes: {schedule.total_planned_min}")
	print("-")

	if not schedule.items:
		print("No tasks scheduled for today.")
		return

	for item in schedule.items:
		pet_name = pet_name_by_id.get(item.pet_id, "Unknown Pet")
		task_name = item.task.title if item.task else "Unknown Task"
		start_str = item.start_time.strftime("%H:%M") if item.start_time else "N/A"
		end_str = item.end_time.strftime("%H:%M") if item.end_time else "N/A"
		status = "COMPLETED" if item.completed else "PENDING"
		print(f"{start_str} - {end_str} | {pet_name}: {task_name} [{status}]")

	print("-")
	for explanation in schedule.explanations:
		print(f"Reason: {explanation.message}")


if __name__ == "__main__":
	pet_app = PetCareApp()
	owner_data, today_date = build_demo_data(pet_app)
	today_schedule = pet_app.run_daily_planning(owner_data.owner_id, today_date)

	# Demo: mark the first scheduled task as completed.
	if today_schedule.items:
		pet_app.mark_task_completion(
			owner_id=owner_data.owner_id,
			schedule_date=today_date,
			item_id=today_schedule.items[0].item_id,
			completed=True,
		)

	print_todays_schedule(pet_app, owner_data.owner_id, today_date)
