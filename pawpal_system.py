from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime, time, timedelta
from enum import Enum
from typing import Any
from uuid import UUID, uuid4


class TaskCategory(Enum):
	FEEDING = "Feeding"
	WALKING = "Walking"
	MEDICATION = "Medication"
	GROOMING = "Grooming"
	PLAY = "Play"
	VET = "Vet"


class Frequency(Enum):
	DAILY = "Daily"
	WEEKLY = "Weekly"
	CUSTOM = "Custom"


class ConstraintType(Enum):
	TIME_AVAILABILITY = "TimeAvailability"
	PRIORITY = "Priority"
	PREFERENCE = "Preference"
	SPACING = "Spacing"
	DEADLINE = "Deadline"


class ScheduleStatus(Enum):
	DRAFT = "Draft"
	FINAL = "Final"
	UPDATED = "Updated"


@dataclass
class PlanExplanation:
	explanation_id: UUID = field(default_factory=uuid4)
	message: str = ""
	rule_applied: str = ""
	impact_score: float = 0.0


@dataclass
class CareTask:
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
	pet_id: UUID = field(default_factory=uuid4)
	name: str = ""
	species: str = ""
	age_years: int = 0
	height_cm: float = 0.0
	weight_kg: float = 0.0
	tasks: list[CareTask] = field(default_factory=list)


@dataclass
class OwnerPreference:
	preference_id: UUID = field(default_factory=uuid4)
	max_tasks_per_block: int = 0
	preferred_task_order: str = ""
	avoid_late_night: bool = False
	notification_lead_min: int = 0


@dataclass
class AvailabilityWindow:
	window_id: UUID = field(default_factory=uuid4)
	day_of_week: int = 0
	start_time: time | None = None
	end_time: time | None = None


@dataclass
class ScheduleItem:
	item_id: UUID = field(default_factory=uuid4)
	start_time: datetime | None = None
	end_time: datetime | None = None
	reason_code: str = ""
	locked: bool = False
	task: CareTask | None = None
	pet_id: UUID | None = None


@dataclass
class DailySchedule:
	schedule_id: UUID = field(default_factory=uuid4)
	date: date | None = None
	status: ScheduleStatus = ScheduleStatus.DRAFT
	total_planned_min: int = 0
	created_at: datetime = field(default_factory=datetime.utcnow)
	items: list[ScheduleItem] = field(default_factory=list)
	explanations: list[PlanExplanation] = field(default_factory=list)

	def regenerate(self) -> None:
		"""Rebuild this schedule from current tasks and constraints."""
		pass


@dataclass
class SchedulingConstraint:
	constraint_id: UUID = field(default_factory=uuid4)
	name: str = ""
	constraint_type: ConstraintType = ConstraintType.TIME_AVAILABILITY
	weight: int = 0
	is_hard_constraint: bool = False

	def validate(self, item: ScheduleItem) -> bool:
		"""Return True when the schedule item satisfies this constraint."""
		pass


@dataclass
class Owner:
	owner_id: UUID = field(default_factory=uuid4)
	name: str = ""
	timezone: str = "UTC"
	pets: list[Pet] = field(default_factory=list)
	preference: OwnerPreference | None = None
	availability_windows: list[AvailabilityWindow] = field(default_factory=list)
	schedules_by_date: dict[date, DailySchedule] = field(default_factory=dict)
	task_to_pet: dict[UUID, UUID] = field(default_factory=dict)

	def add_pet(self, pet: Pet) -> None:
		if any(existing_pet.pet_id == pet.pet_id for existing_pet in self.pets):
			raise ValueError("Pet with this ID already exists")
		self.pets.append(pet)
		for task in pet.tasks:
			self.task_to_pet[task.task_id] = pet.pet_id

	def remove_pet(self, pet_id: UUID) -> None:
		for idx, pet in enumerate(self.pets):
			if pet.pet_id == pet_id:
				for task in pet.tasks:
					self.task_to_pet.pop(task.task_id, None)
				del self.pets[idx]
				return
		raise ValueError("Pet not found")

	def add_task(self, pet_id: UUID, task: CareTask) -> None:
		pet = self._get_pet_by_id(pet_id)
		if pet is None:
			raise ValueError("Pet not found")
		if task.task_id in self.task_to_pet:
			raise ValueError("Task with this ID already exists")
		pet.tasks.append(task)
		self.task_to_pet[task.task_id] = pet_id

	def edit_task(self, task_id: UUID, **changes: Any) -> None:
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
		return self.schedules_by_date.get(schedule_date)

	def _get_pet_by_id(self, pet_id: UUID) -> Pet | None:
		for pet in self.pets:
			if pet.pet_id == pet_id:
				return pet
		return None


class SchedulerService:
	def __init__(self, constraints: list[SchedulingConstraint] | None = None) -> None:
		self.constraints = constraints or []
		self.explanations_by_schedule_id: dict[UUID, list[PlanExplanation]] = {}

	def generate_daily_schedule(self, owner: Owner, schedule_date: date) -> DailySchedule:
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
		return float(task.priority)

	def apply_constraints(self, tasks: list[CareTask], owner: Owner, schedule_date: date) -> list[CareTask]:
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
		return self.explanations_by_schedule_id.get(schedule_id, [])


class PetCareApp:
	def __init__(self) -> None:
		self.scheduler_service = SchedulerService()
		self.owners_by_id: dict[UUID, Owner] = {}
		self.schedules_by_owner_date: dict[tuple[UUID, date], DailySchedule] = {}

	def create_owner_profile(self) -> Owner:
		owner = Owner()
		self.owners_by_id[owner.owner_id] = owner
		return owner

	def save_owner_info(self, owner: Owner) -> None:
		self.owners_by_id[owner.owner_id] = owner

	def save_pet_info(self, owner_id: UUID, pet: Pet) -> None:
		owner = self.owners_by_id.get(owner_id)
		if owner is None:
			raise ValueError("Owner not found")
		owner.add_pet(pet)

	def run_daily_planning(self, owner_id: UUID, schedule_date: date) -> DailySchedule:
		owner = self.owners_by_id.get(owner_id)
		if owner is None:
			raise ValueError("Owner not found")

		schedule = self.scheduler_service.generate_daily_schedule(owner, schedule_date)
		self.schedules_by_owner_date[(owner_id, schedule_date)] = schedule
		owner.schedules_by_date[schedule_date] = schedule
		return schedule
