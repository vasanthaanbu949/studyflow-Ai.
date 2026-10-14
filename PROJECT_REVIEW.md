# StudyFlow AI — Review and Change Log

## Overall review
The existing project has a strong foundation for a student exhibition: clear Home/Tasks/Plan/Progress sections, mobile-aware styling, CSV export, a visible scoring explanation, and a launch script.

## Changes made
1. Improved the scheduling algorithm so daily planned minutes never exceed the chosen daily budget, including when a focus session is longer than the daily budget.
2. Preserved the focus-session maximum while allowing a shorter final block when only a small amount of time remains.
3. Added `unplanned_minutes()` to calculate work that does not fit in the selected planning window.
4. Added an in-app warning when the workload exceeds available capacity and a success message when the workload fits.
5. Added six automated unit tests for score ordering, daily limits, short daily budgets, workload overflow, summary totals, and invalid plan length.
6. Rewrote setup and deployment documentation and added seven-member presentation speaking notes.
7. Created a 10-slide PowerPoint presentation.

## Remaining limitations
- Signed-in users' tasks are saved to a database (SQLite locally, PostgreSQL in the cloud). Google sign-in is required before any planner content is shown.
- The priority logic is rule-based, not a trained machine-learning model or a paid AI integration.
- The live hosted app has not been changed by these local file edits. To update it, replace the source files in the repository used by Streamlit Community Cloud and redeploy.
- Visual verification against the live hosted app was not possible because the shared URL redirected to an authentication page in the browsing environment.

## Validation
- `app.py` and `planner.py` pass Python syntax compilation.
- All 6 planner unit tests pass with `python -m unittest discover -s tests -v`.
