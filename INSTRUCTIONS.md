# INSTRUCTIONS.md — Project Context

## What This Project Is

This is a **medical image classification web application** built with Django.

The core functionality:
- User uploads a scan image (e.g., eye/lens scan)
- A trained ML model (Keras/TensorFlow) processes the image
- The app returns a diagnosis — whether the scan indicates COVID, another disease, or is healthy
- Results are stored and displayed to the user

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python, Django |
| Database | SQLite (local) |
| ML / AI | Keras (TensorFlow backend) |
| Frontend | Django templates (HTML/CSS) |
| Environment | VS Code / Windsurf |

## The Two Codebases

### MY PROJECT — `IndianShip Project/` ✅ (PRIORITY)
- This is the **base**. All work happens here.
- Already has: Django project setup, SQLite database config, login page, register page, basic URL routing
- Missing: image upload feature, ML model integration, prediction logic, results display, and all other app features
- Built in **VS Code / Windsurf**

### REFERENCE CODE — `Sample/` 📖 (Source of Logic)
- This is a **100% complete, working version** of the same project
- Built in PyCharm — contains PyCharm-specific files to be ignored
- Use this as the **blueprint** to extract all missing logic from

## The Goal

Analyze both codebases. Understand the structure of `IndianShip Project/`. Extract all missing features and logic from `Sample/` and implement them cleanly inside `IndianShip Project/` — adapted to fit my existing structure, naming conventions, and setup.

The end result must be a **complete, bug-free, locally runnable Django application** that matches the full functionality of `Sample/`.
