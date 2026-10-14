# StudyFlow AI — Presentation Guide (7-member team)

## Slide 1 — Title and introduction (Member 1)
“Good morning. Our project is StudyFlow AI, a smart study planner designed to help students organize assignments, prioritize deadlines, and track their learning progress.”

## Slide 2 — Problem statement (Member 1)
“Students often manage multiple subjects and deadlines at once. Without a plan, they may forget tasks, underestimate the time required, or leave difficult work until the last minute.”

## Slide 3 — Objectives and solution (Member 2)
“Our objective is to make study planning clearer and more manageable. StudyFlow lets a student enter a task, estimate the effort, set a deadline, and generate a focus-session timetable.”

## Slide 4 — Technology stack (Member 3)
“The user interface is built with Python and Streamlit. Pandas prepares tables and chart data. Our planner module calculates priority scores and allocates focus sessions. CSV export helps students keep copies of their work.”

## Slide 5 — Main features (Member 4)
“The dashboard summarizes tasks and progress. The Tasks tab supports adding, searching, filtering, completing, and removing tasks. The Plan tab creates sessions and charts. The Progress tab explains completion and the scoring method.”

## Slide 6 — How the planner works (Member 5)
“The planner assigns points for urgency, difficulty, importance, and estimated effort. Tasks with higher scores are considered earlier. The scheduler respects the selected daily time budget and focus-block length. If the total workload does not fit, it warns the user.”

## Slide 7 — Demonstration (Member 6)
“First we restore sample tasks, then add a new task. We mark one task completed, generate a schedule, inspect the subject and daily workload charts, and download the timetable as a CSV file.”

## Slide 8 — Testing and improvements (Member 6)
“We added automated tests for urgency ordering, daily capacity, smaller study budgets, overload reporting, schedule summaries, and invalid plan lengths. The layout is designed to adapt to smaller screens.”

## Slide 9 — Limitations and future scope (Member 7)
“This is a rule-based prototype, not a trained AI model. Students can sign in with their Google account so their tasks are saved in a database that only they can see, and they can e-mail their plan to their own Gmail. Without signing in, the demo keeps nothing. Future versions could add automatic reminders, calendar integration, and optional AI-generated revision suggestions.”

## Slide 10 — Conclusion and questions (Member 7)
“StudyFlow AI demonstrates how a simple, transparent planning algorithm can help students organize their workload. Our goal is not to make students study more hours, but to help them use their available time more thoughtfully. Thank you. We welcome your questions.”
