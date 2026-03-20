from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime, time
from enum import Enum
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

	def add_pet(self, pet: Pet) -> None:
		pass

	def remove_pet(self, pet_id: UUID) -> None:
		pass

	def add_task(self, pet_id: UUID, task: CareTask) -> None:
		pass

	def edit_task(self, task_id: UUID) -> None:
		pass

	def remove_task(self, task_id: UUID) -> None:
		pass

	def view_schedule(self, schedule_date: date) -> DailySchedule | None:
		pass


class SchedulerService:
	def generate_daily_schedule(self, owner_id: UUID, schedule_date: date) -> DailySchedule:
		pass

	def score_task(self, task: CareTask) -> float:
		pass

	def apply_constraints(self, tasks: list[CareTask]) -> list[CareTask]:
		pass

	def explain_plan(self, schedule_id: UUID) -> list[PlanExplanation]:
		pass


class PetCareApp:
	def __init__(self) -> None:
		self.scheduler_service = SchedulerService()

	def create_owner_profile(self) -> Owner:
		pass

	def save_owner_info(self, owner: Owner) -> None:
		pass

	def save_pet_info(self, owner_id: UUID, pet: Pet) -> None:
		pass

	def run_daily_planning(self, owner_id: UUID, schedule_date: date) -> DailySchedule:
		pass
