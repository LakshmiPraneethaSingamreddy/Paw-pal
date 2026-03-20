from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime, time, timedelta
from enum import Enum
from typing import Any
from uuid import UUID, uuid4


class TaskCategory(Enum):
	"""Categories of pet care tasks.
	
	Attributes:
		FEEDING: Task for feeding the pet.
		WALKING: Task for walking the pet.
		MEDICATION: Task for administering medication.
		GROOMING: Task for grooming the pet.
		PLAY: Task for playing with the pet.
		VET: Task for veterinary appointments.
	"""
	FEEDING = "Feeding"
	WALKING = "Walking"
	MEDICATION = "Medication"
	GROOMING = "Grooming"
	PLAY = "Play"
	VET = "Vet"


class Frequency(Enum):
	"""Frequency options for recurring pet care tasks.
	
	Attributes:
		DAILY: Task occurs daily.
		WEEKLY: Task occurs weekly.
		CUSTOM: Task occurs on a custom schedule.
	"""
	DAILY = "Daily"
	WEEKLY = "Weekly"
	CUSTOM = "Custom"


class ConstraintType(Enum):
	"""Types of scheduling constraints for pet care tasks.
	
	Attributes:
		TIME_AVAILABILITY: Constraint on time windows when tasks can occur.
		PRIORITY: Constraint on task priority levels.
		PREFERENCE: Constraint on task flexibility or duration preferences.
		SPACING: Constraint on spacing between tasks.
		DEADLINE: Constraint on when tasks must be completed by.
	"""
	TIME_AVAILABILITY = "TimeAvailability"
	PRIORITY = "Priority"
	PREFERENCE = "Preference"
	SPACING = "Spacing"
	DEADLINE = "Deadline"


class ScheduleStatus(Enum):
	"""Status states for a daily pet care schedule.
	
	Attributes:
		DRAFT: Schedule is in draft state, not yet finalized.
		FINAL: Schedule has been finalized and locked.
		UPDATED: Schedule was previously final but has been updated.
	"""
	DRAFT = "Draft"
	FINAL = "Final"
	UPDATED = "Updated"


@dataclass
class PlanExplanation:
	"""Explanation for a scheduling decision in the pet care plan.
	
	Provides reasoning and impact information for how tasks are scheduled.
	
	Attributes:
		explanation_id: Unique identifier for this explanation.
		message: Human-readable explanation of the scheduling decision.
		rule_applied: Name of the rule or constraint that was applied.
		impact_score: Score quantifying the impact of this decision (0.0 to 1.0).
	"""
	explanation_id: UUID = field(default_factory=uuid4)
	message: str = ""
	rule_applied: str = ""
	impact_score: float = 0.0


@dataclass
class CareTask:
	"""A pet care task that needs to be scheduled.
	
	Represents a specific activity that must be performed for a pet, with
	constraints on timing, duration, and flexibility.
	
	Attributes:
		task_id: Unique identifier for this task.
		title: Name/description of the task.
		category: Category of pet care (Feeding, Walking, etc.).
		duration_min: Expected duration of the task in minutes.
		priority: Priority level (higher values = higher priority).
		frequency: How often this task recurs (Daily, Weekly, Custom).
		earliest_start: Earliest time the task can start on a given day.
		latest_end: Latest time the task must be completed by.
		is_flexible: Whether the task can be moved/rescheduled (True) or is rigid.
		notes: Additional notes or instructions for this task.
	"""
	task_id: UUID = field(default_factory=uuid4)
	title: str = ""
	category: TaskCategory = TaskCategory.FEEDING
	duration_min: int = 0
	priority: int = 0
	frequency: Frequency = Frequency.DAILY
	earliest_start: time | None = None
	latest_end: time | None = None
	is_flexible: bool = True
	notes: str = ""


@dataclass
class Pet:
	"""A pet that requires care and scheduling.
	
	Stores information about a pet and tracks all care tasks associated with it.
	
	Attributes:
		pet_id: Unique identifier for this pet.
		name: The pet's name.
		species: Species of the pet (dog, cat, bird, etc.).
		age_years: Age of the pet in years.
		height_cm: Height of the pet in centimeters.
		weight_kg: Weight of the pet in kilograms.
		tasks: List of care tasks assigned to this pet.
	"""
	pet_id: UUID = field(default_factory=uuid4)
	name: str = ""
	species: str = ""
	age_years: int = 0
	height_cm: float = 0.0
	weight_kg: float = 0.0
	tasks: list[CareTask] = field(default_factory=list)


@dataclass
class OwnerPreference:
	"""Pet owner's preferences for task scheduling.
	
	Defines how an owner likes their pet care schedule organized and displayed.
	
	Attributes:
		preference_id: Unique identifier for this preference set.
		max_tasks_per_block: Maximum number of tasks to schedule in one time block.
		preferred_task_order: Preferred order for tasks (e.g., "feeding, play, medication").
		avoid_late_night: If True, don't schedule tasks after 10 PM.
		notification_lead_min: Minutes before a task to send a notification reminder.
	"""
	preference_id: UUID = field(default_factory=uuid4)
	max_tasks_per_block: int = 0
	preferred_task_order: str = ""
	avoid_late_night: bool = False
	notification_lead_min: int = 0


@dataclass
class AvailabilityWindow:
	"""A time window when the owner is available for pet care tasks.
	
	Defines recurring availability windows throughout the week.
	
	Attributes:
		window_id: Unique identifier for this availability window.
		day_of_week: Day of week (0=Monday, 6=Sunday).
		start_time: Time when availability starts on this day.
		end_time: Time when availability ends on this day.
	"""
	window_id: UUID = field(default_factory=uuid4)
	day_of_week: int = 0
	start_time: time | None = None
	end_time: time | None = None


@dataclass
class ScheduleItem:
	"""A single item in a daily schedule representing a scheduled task.
	
	Represents a specific time-boxed instance of a care task on a particular day.
	
	Attributes:
		item_id: Unique identifier for this schedule item.
		start_time: When this task is scheduled to start.
		end_time: When this task is scheduled to end.
		reason_code: Code indicating why this task was scheduled at this time.
		locked: If True, this item cannot be moved/rescheduled.
		task: Reference to the CareTask definition.
		pet_id: ID of the pet this task is for.
		completed: Whether this task has been completed.
		completed_at: Timestamp when this task was completed (if applicable).
	"""
	item_id: UUID = field(default_factory=uuid4)
	start_time: datetime | None = None
	end_time: datetime | None = None
	reason_code: str = ""
	locked: bool = False
	task: CareTask | None = None
	pet_id: UUID | None = None
	completed: bool = False
	completed_at: datetime | None = None

	def mark_completed(self, when: datetime | None = None) -> None:
		"""Mark this schedule item as completed.
		
		Args:
			when: Timestamp of completion. Defaults to current UTC time if not provided.
		"""
		self.completed = True
		self.completed_at = when or datetime.utcnow()

	def mark_incomplete(self) -> None:
		"""Mark this schedule item as not completed."""
		self.completed = False
		self.completed_at = None


@dataclass
class DailySchedule:
	"""A complete daily schedule for pet care tasks.
	
	Contains all scheduled tasks for a specific date and tracks their
	completion status and scheduling explanations.
	
	Attributes:
		schedule_id: Unique identifier for this schedule.
		date: The date this schedule is for.
		status: Current status of the schedule (Draft, Final, or Updated).
		total_planned_min: Total planned time in minutes for all tasks.
		created_at: Timestamp when this schedule was created.
		items: List of scheduled task items for this day.
		explanations: List of explanations for scheduling decisions.
	"""
	schedule_id: UUID = field(default_factory=uuid4)
	date: date | None = None
	status: ScheduleStatus = ScheduleStatus.DRAFT
	total_planned_min: int = 0
	created_at: datetime = field(default_factory=datetime.utcnow)
	items: list[ScheduleItem] = field(default_factory=list)
	explanations: list[PlanExplanation] = field(default_factory=list)

	def regenerate(self) -> None:
		"""Rebuild this schedule from current tasks and constraints.
		
		Validates all schedule items, removes conflicts and invalid entries,
		and adjusts non-locked items as needed. Also updates the schedule status
		if it was previously final.
		
		Raises:
			ValueError: If the schedule date is not set.
		"""
		if self.date is None:
			raise ValueError("Schedule date is required to regenerate")

		valid_items: list[ScheduleItem] = []
		invalid_count = 0
		for item in self.items:
			if item.task is None or item.start_time is None or item.end_time is None:
				invalid_count += 1
				continue
			if item.end_time <= item.start_time:
				invalid_count += 1
				continue
			valid_items.append(item)

		valid_items.sort(key=lambda schedule_item: schedule_item.start_time)

		adjusted_count = 0
		for idx in range(1, len(valid_items)):
			previous_item = valid_items[idx - 1]
			current_item = valid_items[idx]
			if current_item.start_time >= previous_item.end_time:
				continue

			if current_item.locked:
				continue

			duration = current_item.end_time - current_item.start_time
			current_item.start_time = previous_item.end_time
			current_item.end_time = current_item.start_time + duration
			adjusted_count += 1

		self.items = valid_items
		self.total_planned_min = sum(
			int((item.end_time - item.start_time).total_seconds() // 60)
			for item in self.items
			if item.start_time is not None and item.end_time is not None
		)

		if self.status == ScheduleStatus.FINAL:
			self.status = ScheduleStatus.UPDATED
		elif self.status == ScheduleStatus.DRAFT:
			self.status = ScheduleStatus.UPDATED

		summary = (
			f"Regenerated schedule: kept {len(self.items)} items, "
			f"removed {invalid_count} invalid items, adjusted {adjusted_count} overlaps"
		)
		self.explanations.append(
			PlanExplanation(
				message=summary,
				rule_applied="regenerate_schedule",
				impact_score=1.0 if adjusted_count or invalid_count else 0.3,
			)
		)

	def mark_item_completion(self, item_id: UUID, completed: bool = True, when: datetime | None = None) -> None:
		"""Mark a specific schedule item as completed or incomplete.
		
		Args:
			item_id: ID of the schedule item to update.
			completed: If True, mark as completed; if False, mark as incomplete.
			when: Timestamp of completion (used only if completed=True).
		
		Raises:
			ValueError: If the schedule item with the given ID is not found.
		"""
		for item in self.items:
			if item.item_id == item_id:
				if completed:
					item.mark_completed(when)
				else:
					item.mark_incomplete()
				return
		raise ValueError("Schedule item not found")


@dataclass
class SchedulingConstraint:
	"""A constraint that restricts how pet care tasks can be scheduled.
	
	Specifies rules and limits on task scheduling based on various factors
	such as time availability, priority levels, task flexibility, and deadlines.
	
	Attributes:
		constraint_id: Unique identifier for this constraint.
		name: Human-readable name of the constraint.
		constraint_type: Type of constraint (TimeAvailability, Priority, etc.).
		weight: Importance weight for soft constraints (higher = more important).
		is_hard_constraint: If True, must be satisfied; if False, is a preference.
		allowed_start: Earliest time a task can start (for TIME_AVAILABILITY).
		allowed_end: Latest time a task can end (for TIME_AVAILABILITY).
		min_priority: Minimum task priority required (for PRIORITY).
		max_priority: Maximum task priority allowed (for PRIORITY).
		max_duration_min: Maximum task duration allowed (for PREFERENCE/SPACING).
		require_flexible: Whether tasks must be flexible (for PREFERENCE).
		deadline_at: Latest time by which task must complete (for DEADLINE).
	"""
	constraint_id: UUID = field(default_factory=uuid4)
	name: str = ""
	constraint_type: ConstraintType = ConstraintType.TIME_AVAILABILITY
	weight: int = 0
	is_hard_constraint: bool = False
	allowed_start: time | None = None
	allowed_end: time | None = None
	min_priority: int | None = None
	max_priority: int | None = None
	max_duration_min: int | None = None
	require_flexible: bool | None = None
	deadline_at: datetime | None = None

	def validate(self, item: ScheduleItem) -> bool:
		"""Return True when the schedule item satisfies this constraint.
		
		Validates a specific schedule item against this constraint's rules,
		checking that the item's task and timing meet all constraint requirements.
		
		Args:
			item: The schedule item to validate.
		
		Returns:
			True if the item satisfies all constraint checks, False otherwise.
		"""
		if item.task is None:
			return False

		task = item.task

		if self.constraint_type == ConstraintType.TIME_AVAILABILITY:
			if item.start_time is None or item.end_time is None:
				return False
			if self.allowed_start is not None and item.start_time.time() < self.allowed_start:
				return False
			if self.allowed_end is not None and item.end_time.time() > self.allowed_end:
				return False
			return True

		if self.constraint_type == ConstraintType.PRIORITY:
			if self.min_priority is not None and task.priority < self.min_priority:
				return False
			if self.max_priority is not None and task.priority > self.max_priority:
				return False
			return True

		if self.constraint_type == ConstraintType.PREFERENCE:
			if self.require_flexible is not None and task.is_flexible != self.require_flexible:
				return False
			if self.max_duration_min is not None and task.duration_min > self.max_duration_min:
				return False
			return True

		if self.constraint_type == ConstraintType.SPACING:
			if self.max_duration_min is not None and task.duration_min > self.max_duration_min:
				return False
			return True

		if self.constraint_type == ConstraintType.DEADLINE:
			if item.end_time is None:
				return False
			if self.deadline_at is not None and item.end_time > self.deadline_at:
				return False
			if task.latest_end is not None and item.end_time.time() > task.latest_end:
				return False
			return True

		return True


@dataclass
class Owner:
	"""A pet owner and their associated pets and scheduling information.
	
	Manages all information about a pet owner including their pets,
	tasks, scheduling preferences, and generated schedules.
	
	Attributes:
		owner_id: Unique identifier for this owner.
		name: The owner's name.
		timezone: Timezone for scheduling (e.g., 'UTC', 'US/Eastern').
		pets: List of pets owned by this person.
		preference: The owner's scheduling preferences.
		availability_windows: Time windows when owner is available for pet care.
		schedules_by_date: Dictionary mapping dates to generated daily schedules.
		task_to_pet: Dictionary mapping task IDs to their associated pet IDs.
	"""
	owner_id: UUID = field(default_factory=uuid4)
	name: str = ""
	timezone: str = "UTC"
	pets: list[Pet] = field(default_factory=list)
	preference: OwnerPreference | None = None
	availability_windows: list[AvailabilityWindow] = field(default_factory=list)
	schedules_by_date: dict[date, DailySchedule] = field(default_factory=dict)
	task_to_pet: dict[UUID, UUID] = field(default_factory=dict)

	def add_pet(self, pet: Pet) -> None:
		"""Add a new pet to this owner's collection.
		
		Also registers all of the pet's tasks in the task_to_pet mapping.
		
		Args:
			pet: The pet to add.
		
		Raises:
			ValueError: If a pet with the same ID already exists.
		"""
		if any(existing_pet.pet_id == pet.pet_id for existing_pet in self.pets):
			raise ValueError("Pet with this ID already exists")
		self.pets.append(pet)
		for task in pet.tasks:
			self.task_to_pet[task.task_id] = pet.pet_id

	def remove_pet(self, pet_id: UUID) -> None:
		"""Remove a pet and all its tasks from this owner's collection.
		
		Also removes all task-to-pet mappings for this pet's tasks.
		
		Args:
			pet_id: ID of the pet to remove.
		
		Raises:
			ValueError: If no pet with the given ID exists.
		"""
		for idx, pet in enumerate(self.pets):
			if pet.pet_id == pet_id:
				for task in pet.tasks:
					self.task_to_pet.pop(task.task_id, None)
				del self.pets[idx]
				return
		raise ValueError("Pet not found")

	def add_task(self, pet_id: UUID, task: CareTask) -> None:
		"""Add a care task to a specific pet.
		
		Args:
			pet_id: ID of the pet to add the task to.
			task: The care task to add.
		
		Raises:
			ValueError: If the pet is not found or task ID already exists.
		"""
		pet = self._get_pet_by_id(pet_id)
		if pet is None:
			raise ValueError("Pet not found")
		if task.task_id in self.task_to_pet:
			raise ValueError("Task with this ID already exists")
		pet.tasks.append(task)
		self.task_to_pet[task.task_id] = pet_id

	def edit_task(self, task_id: UUID, **changes: Any) -> None:
		"""Edit one or more fields of an existing care task.
		
		Args:
			task_id: ID of the task to edit.
			**changes: Keyword arguments for fields to update (field_name=new_value).
		
		Raises:
			ValueError: If task is not found or task_id field is being edited.
			AttributeError: If an unknown field name is provided.
		"""
		pet_id = self.task_to_pet.get(task_id)
		if pet_id is None:
			raise ValueError("Task not found")

		pet = self._get_pet_by_id(pet_id)
		if pet is None:
			raise ValueError("Inconsistent task index: pet not found")

		for task in pet.tasks:
			if task.task_id == task_id:
				for field_name, field_value in changes.items():
					if field_name == "task_id":
						raise ValueError("task_id cannot be edited")
					if not hasattr(task, field_name):
						raise AttributeError(f"Unknown task field: {field_name}")
					setattr(task, field_name, field_value)
				return

		raise ValueError("Task not found")

	def remove_task(self, task_id: UUID) -> None:
		"""Remove a care task from one of the owner's pets.
		
		Args:
			task_id: ID of the task to remove.
		
		Raises:
			ValueError: If task is not found or pet index is inconsistent.
		"""
		pet_id = self.task_to_pet.get(task_id)
		if pet_id is None:
			raise ValueError("Task not found")

		pet = self._get_pet_by_id(pet_id)
		if pet is None:
			raise ValueError("Inconsistent task index: pet not found")

		for idx, task in enumerate(pet.tasks):
			if task.task_id == task_id:
				del pet.tasks[idx]
				self.task_to_pet.pop(task_id, None)
				return

		raise ValueError("Task not found")

	def view_schedule(self, schedule_date: date) -> DailySchedule | None:
		"""Retrieve the generated schedule for a specific date.
		
		Args:
			schedule_date: The date for which to retrieve the schedule.
		
		Returns:
			The DailySchedule for the given date, or None if not yet generated.
		"""
		return self.schedules_by_date.get(schedule_date)

	def _get_pet_by_id(self, pet_id: UUID) -> Pet | None:
		"""Internal helper to retrieve a pet by its ID.
		
		Args:
			pet_id: ID of the pet to retrieve.
		
		Returns:
			The Pet object if found, None otherwise.
		"""
		for pet in self.pets:
			if pet.pet_id == pet_id:
				return pet
		return None


class SchedulerService:
	"""Service for generating and managing pet care schedules.
	
	Handles the core scheduling logic including constraint application,
	task ordering, and schedule generation.
	
	Attributes:
		constraints: List of scheduling constraints to apply.
		explanations_by_schedule_id: Maps schedule IDs to their explanations.
	"""
	def __init__(self, constraints: list[SchedulingConstraint] | None = None) -> None:
		"""Initialize the scheduler service.
		
		Args:
			constraints: Optional list of scheduling constraints to enforce.
				Defaults to an empty list.
		"""
		self.constraints = constraints or []
		self.explanations_by_schedule_id: dict[UUID, list[PlanExplanation]] = {}

	def generate_daily_schedule(self, owner: Owner, schedule_date: date) -> DailySchedule:
		"""Generate a daily schedule for all of an owner's pets' tasks.
		
		Collects all tasks from the owner's pets, applies constraints and
		preferences, and creates a schedule with tasks ordered by priority.
		
		Args:
			owner: The owner whose schedule to generate.
			schedule_date: The date to generate the schedule for.
		
		Returns:
			A DailySchedule with all scheduled tasks for the given date.
		"""
		all_tasks: list[tuple[UUID, CareTask]] = []
		for pet in owner.pets:
			for task in pet.tasks:
				all_tasks.append((pet.pet_id, task))

		filtered_tasks = self.apply_constraints(
			[t for _, t in all_tasks],
			owner,
			schedule_date,
		)

		task_order = {task.task_id: idx for idx, task in enumerate(filtered_tasks)}
		ordered_pairs = sorted(
			[(pet_id, task) for pet_id, task in all_tasks if task.task_id in task_order],
			key=lambda pair: task_order[pair[1].task_id],
		)

		schedule = DailySchedule(
			date=schedule_date,
			status=ScheduleStatus.DRAFT,
		)

		current_dt = datetime.combine(schedule_date, time(hour=8, minute=0))
		for pet_id, task in ordered_pairs:
			if task.earliest_start is not None:
				earliest_dt = datetime.combine(schedule_date, task.earliest_start)
				if current_dt < earliest_dt:
					current_dt = earliest_dt

			end_dt = current_dt + timedelta(minutes=max(task.duration_min, 0))
			schedule.items.append(
				ScheduleItem(
					start_time=current_dt,
					end_time=end_dt,
					reason_code="priority_and_constraints",
					task=task,
					pet_id=pet_id,
				)
			)
			schedule.total_planned_min += max(task.duration_min, 0)
			current_dt = end_dt

		explanations = [
			PlanExplanation(
				message="Tasks ordered by priority and filtered by constraints",
				rule_applied="priority_and_constraints",
				impact_score=1.0,
			)
		]
		schedule.explanations = explanations
		self.explanations_by_schedule_id[schedule.schedule_id] = explanations
		return schedule

	def score_task(self, task: CareTask) -> float:
		"""Calculate a priority score for a task to determine scheduling order.
		
		Args:
			task: The task to score.
		
		Returns:
			A float score (higher scores indicate higher priority).
		"""
		return float(task.priority)

	def apply_constraints(self, tasks: list[CareTask], owner: Owner, schedule_date: date) -> list[CareTask]:
		"""Filter and sort tasks based on owner availability and constraints.
		
		Removes tasks that don't fit the owner's availability windows or
		constraints, then sorts remaining tasks by priority score.
		
		Args:
			tasks: List of tasks to filter.
			owner: The owner whose preferences and availability to apply.
			schedule_date: The date being scheduled for.
		
		Returns:
			A list of filtered and sorted tasks ready for scheduling.
		"""
		day_windows = [
			window for window in owner.availability_windows if window.day_of_week == schedule_date.weekday()
		]

		if not day_windows:
			return []

		filtered: list[CareTask] = []
		for task in tasks:
			if owner.preference and owner.preference.avoid_late_night:
				if task.latest_end is not None and task.latest_end >= time(hour=22, minute=0):
					continue
			filtered.append(task)

		# Constraints are optional hooks for future expansion.
		for constraint in self.constraints:
			if constraint.is_hard_constraint:
				filtered = [
					task
					for task in filtered
					if constraint.validate(
						ScheduleItem(
							start_time=datetime.combine(schedule_date, task.earliest_start or time(hour=8, minute=0)),
							end_time=datetime.combine(schedule_date, task.latest_end or time(hour=20, minute=0)),
							task=task,
						)
					)
				]

		return sorted(filtered, key=self.score_task, reverse=True)

	def explain_plan(self, schedule_id: UUID) -> list[PlanExplanation]:
		"""Retrieve the explanations for a schedule's planning decisions.
		
		Args:
			schedule_id: ID of the schedule to explain.
		
		Returns:
			List of PlanExplanation objects for the schedule,
			or empty list if not found.
		"""
		return self.explanations_by_schedule_id.get(schedule_id, [])


class PetCareApp:
	"""Main application for managing pet care and scheduling.
	
	Coordinates owner profiles, pet management, task scheduling,
	and schedule tracking.
	
	Attributes:
		scheduler_service: Service used to generate daily schedules.
		owners_by_id: Dictionary mapping owner IDs to owner profiles.
		schedules_by_owner_date: Dictionary mapping (owner_id, date) tuples
			to generated daily schedules.
	"""
	def __init__(self) -> None:
		"""Initialize the pet care application with empty data structures."""
		self.scheduler_service = SchedulerService()
		self.owners_by_id: dict[UUID, Owner] = {}
		self.schedules_by_owner_date: dict[tuple[UUID, date], DailySchedule] = {}

	def create_owner_profile(self) -> Owner:
		"""Create a new owner profile and register it with the application.
		
		Returns:
			A new Owner object with auto-generated ID.
		"""
		owner = Owner()
		self.owners_by_id[owner.owner_id] = owner
		return owner

	def save_owner_info(self, owner: Owner) -> None:
		"""Save or update owner information in the application.
		
		Args:
			owner: The owner object to save.
		"""
		self.owners_by_id[owner.owner_id] = owner

	def save_pet_info(self, owner_id: UUID, pet: Pet) -> None:
		"""Add a new pet to an owner's profile.
		
		Args:
			owner_id: ID of the owner.
			pet: The pet to add.
		
		Raises:
			ValueError: If the owner is not found.
		"""
		owner = self.owners_by_id.get(owner_id)
		if owner is None:
			raise ValueError("Owner not found")
		owner.add_pet(pet)

	def run_daily_planning(self, owner_id: UUID, schedule_date: date) -> DailySchedule:
		"""Generate and save a daily schedule for an owner.
		
		Args:
			owner_id: ID of the owner to generate schedule for.
			schedule_date: The date to schedule.
		
		Returns:
			The generated DailySchedule.
		
		Raises:
			ValueError: If the owner is not found.
		"""
		owner = self.owners_by_id.get(owner_id)
		if owner is None:
			raise ValueError("Owner not found")

		schedule = self.scheduler_service.generate_daily_schedule(owner, schedule_date)
		self.schedules_by_owner_date[(owner_id, schedule_date)] = schedule
		owner.schedules_by_date[schedule_date] = schedule
		return schedule

	def mark_task_completion(
		self,
		owner_id: UUID,
		schedule_date: date,
		item_id: UUID,
		completed: bool = True,
		when: datetime | None = None,
	) -> None:
		"""Mark a scheduled task item as completed or incomplete.
		
		Args:
			owner_id: ID of the owner.
			schedule_date: Date of the schedule containing the item.
			item_id: ID of the schedule item to update.
			completed: If True, mark as completed; if False, mark as incomplete.
			when: Timestamp of completion (used only if completed=True).
		
		Raises:
			ValueError: If the schedule or item is not found.
		"""
		schedule = self.schedules_by_owner_date.get((owner_id, schedule_date))
		if schedule is None:
			raise ValueError("Schedule not found")
		schedule.mark_item_completion(item_id=item_id, completed=completed, when=when)
