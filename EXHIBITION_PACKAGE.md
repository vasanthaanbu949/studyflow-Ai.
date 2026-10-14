# StudyFlow AI — School Exhibition Notes

## Project title
**StudyFlow AI: A Smart Study Planner for Students**

## Abstract
Students often need to manage homework, revision, projects, and exam preparation at the same time. StudyFlow AI is a student-friendly planner that saves each signed-in student's tasks (Google sign-in is required before accessing the planner), calculates a transparent priority score, creates a focus-session timetable, and tracks task completion. It demonstrates how rule-based intelligence can support planning without requiring paid APIs or collecting data in an external AI service.

## Problem statement
Students may forget deadlines, underestimate the time required for assignments, or spend time on less urgent tasks while important work approaches.

## Proposed solution
The user adds each task with a subject, deadline, estimated effort, difficulty, and importance. The app scores open tasks and places focus sessions into a selected planning window while respecting the daily study-time setting as far as capacity allows.

## Main modules
1. **Overview:** task totals, urgent tasks, remaining estimated hours, and completion rate.
2. **Tasks and priorities:** create, search, filter, mark complete, remove, and export tasks.
3. **Smart schedule:** generate a timetable, inspect study-time charts, and export the schedule.
4. **Progress and guide:** view completion charts, learn how scoring works, and read FAQs.

## Priority formula
The prototype combines four factors:
- Deadline urgency
- Difficulty
- Importance
- Estimated effort (with a small capped adjustment)

The score is intentionally explainable. It is **AI-inspired and rule-based**, not a trained machine-learning model.

## Technology used
- Python
- Streamlit for the interface
- Pandas for tabular data and CSV exports
- Python `unittest` for automated tests

## Estimated cost
| Item | Cost |
|---|---:|
| Python | ₹0 |
| Streamlit | ₹0 |
| Pandas | ₹0 |
| AI API | ₹0 — not required |
| Total additional software cost | ₹0 if a compatible computer is available |

An internet connection may be required during first-time package installation.

## Suggested 90-second demonstration
1. Introduce the problem of managing multiple school assignments.
2. Show the overview cards and sample tasks.
3. Add a new task and explain its settings.
4. Mark one task complete and show progress update.
5. Generate a timetable and point out the subject and daily workload charts.
6. Explain that the priority score uses rules and show the CSV export.

## Questions a judge may ask
**Is it real AI?** It is an AI-inspired, rule-based prototype, not a trained machine-learning model. The project is designed to demonstrate explainable automated prioritization.

**What inputs does it use?** Subject, task name, deadline, estimated time, difficulty, and importance.

**What does it produce?** A priority-sorted task view, a focus-session timetable, progress summaries, charts, and CSV downloads.

**Does it cost money?** The software components are free to use. A computer is needed, and internet may be needed for the initial setup.

**Where is task data stored?** If the student signs in with Google, in the app's database under their e-mail address (the app reads only name and e-mail, never the inbox). The planner cannot be accessed before Google sign-in. Students can always download a CSV copy. The prototype does not send the task list to an external AI service.

## Limitations and future improvements
- Automatic study reminders by e-mail and calendar integration.
- Add calendar reminders and exam timetable import.
- Allow task editing and recurring revision sessions.
- Add a trained recommendation model only if a suitable dataset and privacy plan are available.

## Poster text
**StudyFlow AI — Plan smarter, study calmly.**
A student-friendly study planner that prioritizes assignments, builds focus sessions, and tracks progress using a transparent rule-based algorithm.
