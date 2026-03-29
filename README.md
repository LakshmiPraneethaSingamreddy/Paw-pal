# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Smarter Scheduling

PawPal+ has been enhanced with 5 intelligent features to help pet owners plan more effectively:

1. **Task Sorting by Time** — Tasks are automatically sorted chronologically, making it easy to view the day's schedule at a glance.

2. **Pet & Flexibility Filtering** — Filter tasks by pet or flexibility status (flexible/non-flexible) to focus on specific care categories.

3. **Recurring Tasks** — Define tasks that repeat on DAILY, WEEKLY, or CUSTOM schedules (including multi-day patterns and intervals). The scheduler intelligently expands recurrence patterns before planning.

4. **Conflict Detection** — The app detects and warns about overlapping tasks in the schedule, helping identify potential scheduling issues without auto-resolving them.

5. **Task Completion Tracking** — Mark tasks as complete directly from the schedule view with interactive checkboxes. Completed tasks show with strikethrough styling and completion timestamps for easy tracking of daily progress.

These features work together to provide a more organized, flexible, and transparent scheduling experience.

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Testing PawPal+

command to run: python -m pytest

The test set include:
1. **Task CRUD and completion flow(⭐⭐⭐⭐⭐)** -- These tests verify that tasks are added correctly, completion state is persisted, and completion-related error paths raise expected exceptions. They protect core task lifecycle behavior from create through mark-complete operations.

2. **Core scheduling behavior and ordering(⭐⭐⭐⭐⭐)** -- These tests ensure tasks are actually scheduled within intended time bounds and returned in deterministic chronological order. They validate foundational planner guarantees around timing and stable ordering.

3. **Priority, backtracking, deferral, and flexibility behavior(⭐⭐⭐⭐⭐)** -- These tests cover contention scenarios where the scheduler must prefer high-priority rigid tasks, defer flexible tasks, and allow flexible overflow when needed. They confirm the planner’s conflict-resolution strategy behaves as designed under pressure.

4. **Recurrence rules(⭐⭐⭐⭐⭐)** -- These tests validate daily/weekly/custom recurrence paths, including interval-based rules, weekday-based custom rules, and fallback behavior for partially configured recurrence fields. They ensure tasks appear only on eligible dates and are skipped otherwise.

5. **Availability and constraint filtering(⭐⭐⭐⭐⭐)** -- These tests verify the scheduler respects owner availability, fallback windows, late-night preferences, and hard constraints that filter out invalid tasks. They ensure impossible or policy-violating tasks are excluded before final scheduling.

6. **Schedule regeneration and conflict handling(⭐⭐⭐⭐⭐)** -- These tests confirm regenerate fixes overlaps when allowed, refuses invalid inputs, and preserves locked item positions. They protect post-processing logic that cleans schedules without violating lock semantics.

7. **Explanations and observability(⭐⭐⭐⭐)** -- These tests check that planning outputs include meaningful explanation messages and reason codes, including empty-schedule summaries. They validate that the system remains interpretable and debuggable, not just functionally correct.But sometimes these can be too dependent on exact message phrases, which can be brittle to wording changes.


### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.
