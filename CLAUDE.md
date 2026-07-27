# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project overview

Spendly is a Flask-based expense tracker built as a step-by-step learning exercise. Many routes and modules are intentionally left as placeholders (e.g. `return "Logout — coming in Step 3"`) with comments marking which build "Step" implements them. When asked to implement a feature, check for an existing placeholder route/comment first and build on it rather than restructuring around it.

## Commands

Run all commands from the `expense-tracker/` directory (where `app.py` lives), with the venv active:

```bash
source ../venv/bin/activate   # venv lives one directory up, at expense-tracker/venv
python app.py                 # runs the dev server on http://localhost:5002 (debug=True)
pytest                        # run tests
pytest path/to/test_file.py::test_name   # run a single test
pip install -r requirements.txt
```

There is no build step, linter, or frontend bundler configured — this is plain Flask + Jinja + vanilla JS/CSS.

## Architecture

- `app.py` — single Flask app, all routes defined directly on `app` (no blueprints). Currently a mix of working routes (`/`, `/register`, `/login`, `/terms`, `/privacy`) and placeholder stubs for auth and CRUD (`/logout`, `/profile`, `/expenses/add`, `/expenses/<id>/edit`, `/expenses/<id>/delete`).
- `database/db.py` — intended to hold `get_db()` (SQLite connection with `row_factory` and foreign keys enabled), `init_db()` (idempotent `CREATE TABLE IF NOT EXISTS` schema), and `seed_db()` (sample dev data). Not yet implemented — this is an early build step.
- `templates/` — Jinja templates extending `templates/base.html` (navbar/footer shell, loads `static/css/style.css` and `static/js/main.js` via `url_for`). Page-specific templates: `landing.html`, `login.html`, `register.html`, `terms.html`, `privacy.html`.
- `static/css/` — `style.css` is the shared base stylesheet; `landing.css` is landing-page-specific.
- `static/js/` — `main.js` is the shared base script (loaded on every page); `landing.js` is landing-page-specific (e.g. the "how it works" video modal).
- SQLite is the persistence layer (`expense_tracker.db`, gitignored) — no ORM.

## Notes

- The app runs on port 5002, not Flask's default 5000.
- `expense_tracker.db`, `venv/`, and `__pycache__/` are gitignored — don't commit them.

# Working Instructions (Usman's preferences)

- Before asking me to approve any bash command or code change, always explain in plain English first(just like explaining a concept with analogy ): what this specific command or change actually does, and what will be different after it runs. Don't just show the raw command/diff and ask yes/no.
- After making any code change, always explain what you changed and why, in plain English, before moving on — even if I don't ask.
- I run git add, git commit, and git push myself, manually. Don't run these automatically on my behalf.