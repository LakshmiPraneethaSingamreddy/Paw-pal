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
For the scheduler I have taken the availabiltiy, priority and preferences of the owner into consideration.

- How did you decide which constraints mattered most?
I have decided to give more weightage to the availability and priority, because the tasks should be completed when the owner is available and the high priority tasks should be completed first with in their scheduled time(like vet appointments, feeding as they can't be postponed). And then if the tasks are flexible, and cannot be fit in their scheduled slot, I assigned them to the next available time frame, because I want nothing to be skipped unless until I can't fit that task anywhere for that day. 

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
The main tradeoff that my schedule makes is that if a task is **"low priority"** and is **"flexible"**, then it will first schedule the tasks that are high priority, then schedule the remaining tasks later, and if they can't fit in their requested time slot, since they are flexible they are pushed to the next available time slot.

- Why is that tradeoff reasonable for this scenario?
I think this tradeoff is reasonable in this scenario. For example, consider three tasks within the 8:00 a.m. to 10:00 a.m. window: breakfast feeding (20 minutes, high priority, non-flexible), a vet appointment (90 minutes, high priority, non-flexible), and a morning walk (30 minutes, medium priority, flexible). Since feeding and the vet appointment are both high priority and non-flexible, they must be scheduled first. After placing those two tasks, only 10 minutes remain in the original window, which is not enough time for the full walk. Because the morning walk is flexible, the scheduler shifts it to the next available slot, from 9:50 a.m. to 10:20 a.m., instead of dropping it. This behavior prioritizes critical care while still completing less urgent flexible tasks whenever possible.

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
I used the AI tools for code writing, debugging, refactoring and test case generation during this project.

- What kinds of prompts or questions were most helpful?
I observed that the clear prompting of what we actually want helps in acheiving better functionality of the app. And asking the questions about why something is failing or how can we optimize the functionality further, or just asking the agent to generate plan on what next steps should be are really helpful as they give clear picture of what is happening with the code.

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
When I was asking questions on my UMl diagram and functionality of the app, it kept suggesting to add more features and classes. I mean that will be actually cool, if I add more functionality but it over complicates my app and I felt that in the long run it might get hard to actually complete the app since there any many things to work on my own. So, I did not accept that suggestions and I asked it to give me suggestions on exactly what I need and do not go outside of the scope of my problem.

- How did you evaluate or verify what the AI suggested?
I first ask on the Ai to explain fully what it suggests and then verify if it aligns with my goal and if it does I will ask it to generate a plan on how we are going to implement that. If I am satisfied with the plan, then I will proceed with the implementation and then I will ask it to generate some tests and I will also manually test the newly added functionality by myself.

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
I have tested the functionalities that I want my app to perform. I have tested whether the user can enter/edit/delete their details, user can add/edit/remove their pets, if user can add multiple pets, the core scheduling and ordering of tasks, how recurrent tasks are generated, whether the availability and preferences are taken into consideration or not, schedule rengeration and conflict handling and how the schedule plan explanations are done.

- Why were these tests important?
These tests are important because they verify that the app is actually delivering the functionality it is designed to provide. They also help catch gaps, edge cases, and unfinished logic, so I can identify and fix loose ends in the code before release.
**b. Confidence**

- How confident are you that your scheduler works correctly?
I am highly confident that my scheduler works correctly because it is supported by a strong implementation strategy and rigorous testing. The combination of careful design decisions and comprehensive test coverage gives me confidence that the core functionality behaves reliably across expected scenarios.

- What edge cases would you test next if you had more time?
If I had more time, I would implement a database layer so user data can be stored persistently instead of only in session state. After that, I would add targeted tests for data persistence, including save/retrieve flows, update consistency, and correct loading behavior across app restarts. This would make the system more reliable for real-world usage and help ensure data integrity over time.

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?
I feel the project went very well overall, and I am most satisfied with the UI design and the functionality it delivers.

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?
I would improve the app by adding database integration so it becomes a true end-to-end system, with persistent user data storage instead of session-only state.

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
I learned that UML diagrams play a critical role in app development because they provide a clear roadmap of what needs to be built. They help keep the implementation focused, reduce scope drift, and prevent unnecessary complexity by guiding decisions throughout the project.
