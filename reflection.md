# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

- Briefly describe your initial UML design.
Four classes for pet care that is needed to stay consistent with duties of the owner's use of the system.

- What classes did you include, and what responsibilities did you assign to each?
Pet, Task, Owner , Daily Plan

**b. Design changes**

- Did your design change during implementation? 
No.

- If yes, describe at least one change and why you made it. 
N/A
---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?

Budget based on spending choices

- How did you decide which constraints mattered most?

Mattered based on owner.

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.

Greedy scheduler skips tasks that would fit later.

- Why is that tradeoff reasonable for this scenario?

Schedules more tasks without changing the priority ordering.

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?

Mainly for brainstorming and debugging, and honestly reviewing some code I entered.

- What kinds of prompts or questions were most helpful?

Offering filters on the scheduling for the pet owners

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
AI wanted me to go by priority order rather than time order , but I would rather go by the time due to initial app run start. I would use this to view the flow of operation first.

- How did you evaluate or verify what the AI suggested?
I checked the lines it wanted to fix and replace.

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?

Tested daily tasks and made sure that it was marked completed and status' updated.
- Why were these tests important?

These are important because the app will tend to run on a cycle with different users.
**b. Confidence**

- How confident are you that your scheduler works correctly?

Very confident with the multiple tests ran.

- What edge cases would you test next if you had more time?

To see if the same or different pet were getting registered under the same task.

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

The streamline running , final product.

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

I could improve the tasks to be more unique.

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?

I learned that even AI can understand the needs of our furry friends! Haha, not only that but, it is actually super beneficial to use AI to superb your projects in areas you may not realize.