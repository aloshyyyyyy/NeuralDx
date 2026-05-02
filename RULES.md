# RULES.md — What To Do and What To Skip

## Priority Rules

1. **`IndianShip Project/` is the master codebase.** Never restructure or rename its core folders or files unless absolutely required for functionality.
2. **Do NOT touch or overwrite** the existing login and register pages/logic in `IndianShip Project/`. They are already working — build around them.
3. **`Sample/` is reference only.** Never run or modify it. Read it, understand it, then implement equivalent logic into `IndianShip Project/`.

---

## What To SKIP from `Sample/`

Ignore all of the following — do not copy them:

- `.idea/` folder (PyCharm config)
- Any `venv/` or virtual environment folders
- `*.pyc` files and `__pycache__/` folders
- Any hardcoded absolute file paths (e.g., `C:\Users\Dan\...`) — replace with relative paths
- Any PyCharm run configurations
- `db.sqlite3` from Sample — we keep our own database
- Any credentials, secret keys, or API keys from Sample — use the ones already in `IndianShip Project/`

---

## What To COPY and IMPLEMENT from `Sample/`

Extract and adapt the following into `IndianShip Project/`:

- **ML model loading logic** — how and where the Keras model is loaded
- **Image upload handling** — the form, view, and file saving logic
- **Image preprocessing** — resizing, normalization, or any transformations before passing to the model
- **Prediction logic** — how the model output is interpreted (class labels, confidence scores, etc.)
- **Results display** — the template and view that shows prediction results to the user
- **Any Django models** (database tables) related to image uploads, predictions, or results — migrate them cleanly
- **URL patterns** for all new features
- **Any static files** (CSS, JS, images) that are part of the UI — adapted to fit the existing template style
- **ML model file** (`.h5`, `.keras`, or similar) — copy it to the appropriate location in `IndianShip Project/`

---

## Conflict Resolution

- If `Sample/` has a different way of doing login/auth — **ignore it**, keep mine
- If `Sample/` uses different variable names or function names — **adapt to my naming style** where possible
- If `Sample/` has a `settings.py` with additional configs (like `MEDIA_ROOT`, `MEDIA_URL`, `STATICFILES_DIRS`) — **merge only the missing parts** into my `settings.py`, don't replace the whole file
- If there's a feature in `Sample/` that seems unrelated to the core ML prediction flow — **ask before implementing**

---

## Code Quality Rules

- All new code must follow the existing code style in `IndianShip Project/`
- No unused imports, no dead code
- Every new view must be connected to a URL
- Every new model must have a migration generated
- The app must run with `python manage.py runserver` without errors after all changes
