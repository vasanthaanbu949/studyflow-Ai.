# StudyFlow AI — Smart Study Planner

A Python + Streamlit student-planning app for organizing schoolwork, generating a focus-session timetable, and tracking progress.

**Google sign-in is required:** the sign-in screen is the first screen. The study planner is not rendered until Google authentication succeeds. There is no guest/demo bypass. Once signed in, users can save tasks per account and optionally e-mail their study plan.

## Important: where to run commands
After extracting the ZIP, open **the extracted folder that directly contains `app.py` and `requirements.txt`** in VS Code. Do not run the commands from its parent folder.

## Run on Windows (easiest)
1. Install Python 3.10 or newer from https://www.python.org/downloads/ (select **Add Python to PATH**).
2. Extract this ZIP.
3. Double-click `run_windows.bat`, or open the extracted folder in VS Code and use the commands below.

```bat
python -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

If Windows says `python` is not found, try replacing `python` with `py` in the setup commands. Keep the terminal open while using the app. Open http://localhost:8501 if it does not open automatically. Press Ctrl+C to stop the app.

## Run on macOS / Linux
```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

## Features
- Overview dashboard: tasks, due-soon count, remaining hours, and completion rate.
- Add tasks with subject, deadline, estimated time, difficulty, and importance.
- Search and filter tasks; mark tasks complete or remove them.
- Transparent, rule-based priority scoring.
- Study timetable with daily capacity limits and focus blocks.
- Warnings when workload does not fit the selected plan.
- Charts and CSV downloads for tasks and timetable.
- Responsive layout and touch-friendly controls.
- **Google sign-in** (name + e-mail only; the app never reads the student's inbox).
- **Saved tasks per user** (SQLite on your computer, PostgreSQL in the cloud). Users can delete all their data from inside the app.
- **E-mail my plan:** sends the timetable to the signed-in student's Gmail inbox.

## Important accuracy note
Despite the name “AI”, this version is an **AI-inspired, rule-based prototype**, not a trained machine-learning model. Google sign-in is required to reach the planner. Signed-in users' tasks are saved in the app's database when storage is available.

## Turn on Google sign-in, saved tasks and e-mail (setup guide)

Everything below is configured through **secrets**, never in the code. Locally, copy `.streamlit/secrets.toml.example` to `.streamlit/secrets.toml` and fill it in. On Streamlit Community Cloud, open your app → **Settings → Secrets** and paste the same text. (Menu names in Google, Supabase and Streamlit change from time to time; follow the closest match.)

### Step 1 - Google sign-in
1. Go to https://console.cloud.google.com/ and create a project.
2. Open **APIs & Services → OAuth consent screen** (also called *Google Auth Platform*). Choose **External**, enter an app name and your e-mail.
3. Open **Credentials → Create credentials → OAuth client ID → Web application**. Under **Authorized redirect URIs** add both:
   - `http://localhost:8501/oauth2callback` (for testing on your computer)
   - `https://YOUR-APP-NAME.streamlit.app/oauth2callback` (your deployed app)
4. Copy the **Client ID** and **Client secret** into the `[auth.google]` section of your secrets. Set `redirect_uri` in `[auth]` to the address you are currently using (localhost or the deployed one) and `cookie_secret` to a long random string (`python -c "import secrets; print(secrets.token_urlsafe(32))"`).
5. While the consent screen is in **Testing** mode only the Gmail addresses you list as *Test users* can sign in. To let any student sign in, click **Publish app**. The app asks only for the basic `openid`, `email` and `profile` information, which does not need Google's extra review.

### Step 2 - Permanent storage
- **On your own computer:** do nothing. Tasks are saved in a local file `studyflow.db`.
- **On Streamlit Community Cloud:** the app's disk is erased when it restarts, so use a free hosted PostgreSQL database such as **Supabase** or **Neon**. Create a project, copy its connection string (a URL starting with `postgresql://`), and put it in the `[database]` section as `url`. If a connection error mentions IPv6 or "network is unreachable", use the provider's *pooler* connection string instead. The tables are created automatically on first start.

### Step 3 - Test it
Run the app and verify that the sign-in screen appears before any planner content. Click **Continue with Google**, complete Google sign-in, add a task, sign out, and sign in again. With permanent storage configured, the task should still be there; another Google account must not see it. Without the required secrets, the app shows setup instructions and remains locked.

### Step 4 - E-mail the plan (optional)
1. Pick (or create) a Gmail account to act as the **sender**, for example `studyflow.noreply.demo@gmail.com`.
2. Turn on **2-Step Verification** for it, then create an **App password** (Google Account → Security → App passwords).
3. Put the address and the 16-character app password in the `[email]` section of your secrets.

The signed-in student then sees **“Email this plan to my Gmail”** on the Plan tab. E-mails are only ever sent to the address the student signed in with, and at most one per minute per session.

### What data is stored, and is it safe?
- Stored: e-mail address, name, and the tasks the student types in. Nothing else from Google; **the app never reads anyone's Gmail inbox and never sees their password.**
- Every database query is filtered by the signed-in e-mail address, so users cannot see each other's tasks. Each user can delete all their data from **Privacy & my data**.
- Keep `secrets.toml` private. If the sender app password or database URL leaks, revoke it and create a new one.
- If the app is used by real students (especially under 18), tell them and their school what is stored and get any permission your school requires.

## Troubleshooting
- **`No module named streamlit`:** activate the virtual environment, then run `python -m pip install -r requirements.txt`.
- **`File does not exist: app.py`:** you are in the wrong directory. Change directory to the extracted folder containing `app.py`.
- **`streamlit is not recognized`:** run it as `python -m streamlit run app.py` rather than `streamlit run app.py`.
- **Package installation fails:** check internet access, then retry `python -m pip install -r requirements.txt`.
- **`redirect_uri_mismatch` from Google:** the redirect URI in your secrets must exactly match one added in Google Cloud (including `https://` and `/oauth2callback`).
- **“Access blocked” when signing in:** the consent screen is in Testing mode and your Gmail is not on the Test users list, or publish the app (Step 1.5).
- **Planner opens without signing in:** make sure you deployed the updated `app.py`; the updated version intentionally locks the app if Google secrets are missing.
- **Tasks disappear on Streamlit Cloud:** you are using the local SQLite file; add a `[database]` URL (Step 2).
- **E-mail fails:** check the sender's 2-Step Verification and App password, and that the sender address matches the account the app password belongs to.
- **Port 8501 is busy:** run `python -m streamlit run app.py --server.port 8502` and open http://localhost:8502.

## Open on a phone using the same Wi-Fi
Run `python -m streamlit run app.py --server.address 0.0.0.0`, connect the phone to the same Wi-Fi, and open `http://COMPUTER-IP:8501`. Allow Python through the computer's firewall on private networks if prompted.

## Deploy to Streamlit Community Cloud
Upload **`app.py`, `planner.py`, `storage.py`, `mailer.py`, and `requirements.txt`** to a GitHub repository (all five are needed). On https://share.streamlit.io/, select that repository and set `app.py` as the main file. Then add your secrets (next section). Never upload `secrets.toml`, passwords, API keys, or private data; the included `.gitignore` blocks `secrets.toml` and database files.

## Tests
From this folder run:
```bash
python -m unittest discover -s tests -v
```

Nineteen tests cover the planner (urgency scoring, daily capacity, small time budgets, unplanned workload, summaries, invalid plan lengths), storage (round-trip, persistence, user isolation, limits, SQL-injection text, data deletion) and e-mail building (content, HTML escaping, header injection).

## Project files
- `app.py` — Streamlit interface (including Google sign-in).
- `planner.py` — priority scoring and schedule allocation.
- `storage.py` — per-user saved tasks (SQLite or PostgreSQL).
- `mailer.py` — builds and sends the study-plan e-mail through Gmail.
- `.streamlit/secrets.toml.example` — template for sign-in, database and e-mail settings.
- `tests/test_planner.py` — automated tests.
- `requirements.txt` — dependencies.
- `run_windows.bat` — Windows setup and launch helper.
- `make_qr.py` / `phone_qr.png` — optional QR helper for local demos.
- `PRESENTATION_GUIDE.md` — speaking notes.
- `EXHIBITION_PACKAGE.md` — exhibition setup notes.
- `PROJECT_REVIEW.md` — project review.
