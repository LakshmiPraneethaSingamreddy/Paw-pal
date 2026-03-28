"""Test to demonstrate flexible tasks being scheduled past their deadline."""
from datetime import date, time
from pawpal_system import (
	CareTask, Owner, OwnerPreference, Pet, TaskCategory, 
	Frequency, AvailabilityWindow, PetCareApp
)

def test_flexible_tasks_overflow_past_deadline():
	"""Demonstrates your exact task setup with flexible tasks scheduled after deadline."""
	app = PetCareApp()
	
	# Create owner with full-day availability
	owner = Owner(name="Test Owner", timezone="America/Chicago")
	owner.preference = OwnerPreference(avoid_late_night=False)
	app.owners_by_id[owner.owner_id] = owner
	
	# Create pet
	pet = Pet(
		name="Mochi",
		species="Dog",
		age_years=2,
		height_cm=30,
		weight_kg=5
	)
	owner.add_pet(pet)
	
	# Use today's date with matching availability window
	today = date.today()
	owner.availability_windows.append(
		AvailabilityWindow(
			day_of_week=today.weekday(),
			start_time=time(8, 0),
			end_time=time(18, 0)
		)
	)
	
	# Add your exact tasks
	owner.add_task(pet.pet_id, CareTask(
		title="Morning walk",
		category=TaskCategory.WALKING,
		duration_min=20,
		priority=3,
		earliest_start=time(8, 0),
		latest_end=time(10, 0),
		is_flexible=False
	))
	
	owner.add_task(pet.pet_id, CareTask(
		title="Feed",
		category=TaskCategory.FEEDING,
		duration_min=20,
		priority=3,
		earliest_start=time(8, 0),
		latest_end=time(9, 30),
		is_flexible=False
	))
	
	owner.add_task(pet.pet_id, CareTask(
		title="play",
		category=TaskCategory.PLAY,
		duration_min=60,
		priority=1,
		earliest_start=time(8, 0),
		latest_end=time(10, 0),
		is_flexible=True  # FLEXIBLE - can overflow past 10:00
	))
	
	owner.add_task(pet.pet_id, CareTask(
		title="vet appointment",
		category=TaskCategory.VET,
		duration_min=60,
		priority=3,
		earliest_start=time(8, 0),
		latest_end=time(10, 30),
		is_flexible=True  # FLEXIBLE - can overflow
	))
	
	owner.add_task(pet.pet_id, CareTask(
		title="buy ice cream",
		category=TaskCategory.FEEDING,
		duration_min=30,
		priority=1,
		earliest_start=time(8, 0),
		latest_end=time(10, 0),
		is_flexible=True  # FLEXIBLE - can overflow past 10:00
	))
	
	# Generate schedule for today
	schedule = app.run_daily_planning(owner.owner_id, today)
	
	print("\n" + "="*80)
	print("SCHEDULE WITH FLEXIBLE TASK OVERFLOW (Your Example)")
	print("="*80)
	
	print("\nScheduled Tasks:")
	print("-" * 80)
	for i, item in enumerate(schedule.items, 1):
		if item.task and item.start_time:
			deadline_text = item.task.latest_end.strftime("%H:%M") if item.task.latest_end else "N/A"
			flexible_text = "✓ FLEXIBLE" if item.task.is_flexible else "  RIGID"
			start_time = item.start_time.strftime("%H:%M") if item.start_time else "N/A"
			end_time = item.end_time.strftime("%H:%M") if item.end_time else "N/A"
			
			overflow_marker = " ⚠️ OVERFLOWED PAST DEADLINE" if (item.task.latest_end and item.end_time and 
																  item.end_time.time() > item.task.latest_end and 
																  item.task.is_flexible) else ""
			
			print(f"{i}. {item.task.title:20} | {start_time}-{end_time} | "
				  f"Priority:{item.task.priority} | Deadline:{deadline_text} | {flexible_text}{overflow_marker}")
			print(f"   Reason: {item.reason_code}")
	
	print("\n\nSkipped Tasks:")
	print("-" * 80)
	skipped_count = 0
	for item in schedule.items:
		if item.start_time is None and item.task:
			skipped_count += 1
			print(f"• {item.task.title} - {item.reason_code}")
	if skipped_count == 0:
		print("(None - all tasks were scheduled!)")
	
	print("\n\nPlan Explanation:")
	print("-" * 80)
	for explanation in schedule.explanations:
		print(f"• {explanation.message}")
	
	print("\n" + "="*80)
	print("KEY INSIGHT:")
	print("="*80)
	print("✓ Flexible tasks (like 'play' and 'buy ice cream') CAN be scheduled AFTER their deadline")
	print("✓ Non-flexible tasks (like 'Feed' and 'Morning walk') MUST stay within their deadline")
	print("✓ This allows the scheduler to fit more tasks by being flexible with timing!")
	print("="*80 + "\n")

if __name__ == "__main__":
	test_flexible_tasks_overflow_past_deadline()
