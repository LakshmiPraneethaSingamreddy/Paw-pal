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

These features work together to provide a more organized, flexible, and transparent scheduling experience. See `app.py` docstring for implementation details.

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.
