# PawPal+ Project Reflection

## 1. System Design
The intial 3 core actions the user should be able to perform are
1) The user can add/ remove a pet
2) The user can edit(add/remove) the tasks
3) The user can check the schedule at any point of time during the day 

**a. Initial design**

- Briefly describe your initial UML design.
My intial UML has only 3 classes where the classes and relationships between them describe the basic and important functionality of the app.
- What classes did you include, and what responsibilities did you assign to each?
the classes i have included in my initial UML are: 1) Owner, 2) Pet and 3) Scheduler.
the responsibilities of these classes are:
1) Owner - can add/remove the pet, can edit(add/remove) tasks, can view schedule, provides availability window and preferences
2) Scheduler - create schedule, can edit schedule, generates explanation, ranks tasks based on priority and keep tracks of multiple pets
3) pet - has name, age, height and weight.

**b. Design changes**

- Did your design change during implementation?
Yes , during the implementation my designed has changed. I have added some more classes and the corresponding required attributes to make the system more manageable and also for clean system design.
- If yes, describe at least one change and why you made it.
 1) I have created seperate classes for owner preferences and Availability window so that the system logic will not become complicated.
 2) I have added Petcare app class as the main interface, so that it will be the entry point where the owner interacts with the app.
 3) I have added Scheduling constraint, Daily schedule and schedule item classes so that the edits to the schedule are manageable.
 4) I have created a seperate PlanExplanation class, so that the explanation of why that plan has choosen will be transparent.
 5) and lastly I also have included a careTask class, becuase a pet can have many tasks scheduled for that day and something needs to keep track of these.
---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
