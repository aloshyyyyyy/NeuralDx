# NeuralDx Summary

## What it does

NeuralDx is a Django web application for AI-assisted chest/lung scan classification.  
Authenticated users can register, log in, upload an image, receive a model prediction (`Covid`, `Normal`, or `Viral Pneumonia`) with confidence, review their analysis history, view profile stats, and download a PDF diagnostic report.

Evidence:
- Purpose and user-facing outcomes are documented in the project README (`/home/runner/work/NeuralDx/NeuralDx/README.md:3-21`).
- Authenticated dashboard/upload/result workflow is reflected in templates (`/home/runner/work/NeuralDx/NeuralDx/myproject/templates/home.html:29-40`, `/home/runner/work/NeuralDx/NeuralDx/myproject/templates/upload.html:30-58`, `/home/runner/work/NeuralDx/NeuralDx/myproject/templates/result.html:50-70`).
- Prediction classes are explicitly mapped in class indices (`/home/runner/work/NeuralDx/NeuralDx/myproject/myapp/class_indices.json:1`).
- Prediction history and profile stats are implemented in views/templates (`/home/runner/work/NeuralDx/NeuralDx/myproject/myapp/views.py:197-213`, `/home/runner/work/NeuralDx/NeuralDx/myproject/templates/history.html:46-75`, `/home/runner/work/NeuralDx/NeuralDx/myproject/templates/profile.html:58-66`).
- PDF report download is implemented (`/home/runner/work/NeuralDx/NeuralDx/myproject/myapp/urls.py:17`, `/home/runner/work/NeuralDx/NeuralDx/myproject/myapp/views.py:223-323`).

## How it works (step-by-step)

1. **Django starts from `manage.py`** and sets `DJANGO_SETTINGS_MODULE` to `myproject.settings`, then runs management commands/server (`/home/runner/work/NeuralDx/NeuralDx/myproject/manage.py:7-22`).
2. **Settings load environment variables** from root `.env`, configure security/debug flags, SQLite DB, static/media paths, and installed apps (`/home/runner/work/NeuralDx/NeuralDx/myproject/myproject/settings.py:19-50`, `86-91`, `128-132`; `/home/runner/work/NeuralDx/NeuralDx/.env.example:1-3`).
3. **Root URL routing** includes `myapp.urls`, and in debug mode serves static/media (`/home/runner/work/NeuralDx/NeuralDx/myproject/myproject/urls.py:22-28`).
4. **App URL routing** maps login/register/home/upload/predict/history/profile/report endpoints (`/home/runner/work/NeuralDx/NeuralDx/myproject/myapp/urls.py:4-18`).
5. **Authentication flow**:
   - Login page renders, POST authenticates user via Django auth, redirects to `/home/` on success (`/home/runner/work/NeuralDx/NeuralDx/myproject/myapp/views.py:13-27`).
   - Registration validates password confirmation and uniqueness, creates `User`, creates `user_table` profile entry, logs in user (`/home/runner/work/NeuralDx/NeuralDx/myproject/myapp/views.py:34-75`).
   - Logout clears session and redirects to login (`/home/runner/work/NeuralDx/NeuralDx/myproject/myapp/views.py:327-330`).
6. **Protected user pages** (`home`, `upload_get`, `history`, `profile`, `download_report`) require login via `@login_required` (`/home/runner/work/NeuralDx/NeuralDx/myproject/myapp/views.py:107`, `111`, `196`, `201`, `223`).
7. **Upload and validation** in `upload_and_predict`:
   - Requires uploaded file.
   - Enforces 5MB max.
   - Restricts MIME to JPEG/PNG.
   - Verifies real image content with PIL.
   - Saves temporarily with UUID filename in storage.
   (`/home/runner/work/NeuralDx/NeuralDx/myproject/myapp/views.py:118-143`).
8. **Inference preprocessing**:
   - Loads image at 224x224 RGB.
   - Converts to array.
   - Applies VGG16 `preprocess_input`.
   - Adds batch dimension.
   (`/home/runner/work/NeuralDx/NeuralDx/myproject/myapp/views.py:145-159`).
9. **Model loading and prediction**:
   - Model path points to `myapp/model_VGG.keras`.
   - Class index JSON is loaded and reversed to index→class map.
   - Model is lazy-loaded once through `get_model()` with `safe_mode=True`.
   - Prediction uses `argmax` + max probability for confidence.
   (`/home/runner/work/NeuralDx/NeuralDx/myproject/myapp/views.py:86-105`, `160-166`).
10. **Persistence and result rendering**:
    - Creates `Prediction` record with user, uploaded image, predicted class, and confidence.
    - Renders `result.html` with result details and report download id.
    - Deletes temporary upload file in `finally`.
    (`/home/runner/work/NeuralDx/NeuralDx/myproject/myapp/views.py:173-193`; `/home/runner/work/NeuralDx/NeuralDx/myproject/myapp/models.py:17-23`; `/home/runner/work/NeuralDx/NeuralDx/myproject/templates/result.html:54-70`).
11. **History/profile/report flow**:
    - History fetches per-user predictions ordered newest first (`/home/runner/work/NeuralDx/NeuralDx/myproject/myapp/views.py:197-199`).
    - Profile calculates total predictions and last prediction date (`/home/runner/work/NeuralDx/NeuralDx/myproject/myapp/views.py:202-213`).
    - Report endpoint generates a styled PDF with result, confidence bar, image, username/date/id (`/home/runner/work/NeuralDx/NeuralDx/myproject/myapp/views.py:223-323`).
12. **Frontend behavior**:
    - JS adds upload preview + enables submit once file selected (`/home/runner/work/NeuralDx/NeuralDx/myproject/static/js/main.js:3-29`).
    - JS animates result confidence bar (`/home/runner/work/NeuralDx/NeuralDx/myproject/static/js/main.js:31-38`).
    - JS filters history cards by class (`/home/runner/work/NeuralDx/NeuralDx/myproject/static/js/main.js:41-59`; `/home/runner/work/NeuralDx/NeuralDx/myproject/templates/history.html:39-44`, `49`).

## Tech stack

### Core framework and runtime
- **Python 3.9 recommended** (`/home/runner/work/NeuralDx/NeuralDx/SETUP_NOTES.md:28`).
- **Django 4.2+** (dependency and project scaffold) (`/home/runner/work/NeuralDx/NeuralDx/requirements.txt:1`; `/home/runner/work/NeuralDx/NeuralDx/myproject/myproject/settings.py:1-4`).
- **ASGI/WSGI entrypoints** for deployment (`/home/runner/work/NeuralDx/NeuralDx/myproject/myproject/asgi.py:10-16`; `/home/runner/work/NeuralDx/NeuralDx/myproject/myproject/wsgi.py:10-16`).

### ML / data science stack
- **TensorFlow + Keras** used for inference and training (`/home/runner/work/NeuralDx/NeuralDx/myproject/myapp/views.py:82-85`, `100-104`; `/home/runner/work/NeuralDx/NeuralDx/myproject/myapp/training.py:8-14`).
- **VGG16 transfer learning architecture** (`/home/runner/work/NeuralDx/NeuralDx/myproject/myapp/training.py:85-100`; `/home/runner/work/NeuralDx/NeuralDx/README.md:38-41`).
- **NumPy**, **scikit-learn**, **matplotlib**, **seaborn** used in training/evaluation (`/home/runner/work/NeuralDx/NeuralDx/myproject/myapp/training.py:3-6`, `15`, `146-157`; `/home/runner/work/NeuralDx/NeuralDx/requirements.txt:4`, `6`, `7`, `9`).

### Persistence and files
- **SQLite3** database (`/home/runner/work/NeuralDx/NeuralDx/myproject/myproject/settings.py:86-91`).
- **Django media storage** for uploaded prediction images (`/home/runner/work/NeuralDx/NeuralDx/myproject/myproject/settings.py:130-132`; `/home/runner/work/NeuralDx/NeuralDx/myproject/myapp/models.py:19`).

### Frontend
- **Django templates** + **custom CSS/JS** (`/home/runner/work/NeuralDx/NeuralDx/myproject/templates/login.html:1-11`; `/home/runner/work/NeuralDx/NeuralDx/myproject/static/css/style.css:1-31`; `/home/runner/work/NeuralDx/NeuralDx/myproject/static/js/main.js:1-59`).
- **Bootstrap Icons CDN** and **Google Fonts** used client-side (`/home/runner/work/NeuralDx/NeuralDx/myproject/templates/login.html:8-10` and same pattern in other templates).

### Supporting libraries/services
- **Pillow** for image validation and handling (`/home/runner/work/NeuralDx/NeuralDx/myproject/myapp/views.py:7`, `133-136`; `/home/runner/work/NeuralDx/NeuralDx/requirements.txt:5`).
- **python-dotenv** for env loading (`/home/runner/work/NeuralDx/NeuralDx/myproject/myproject/settings.py:20-24`; `/home/runner/work/NeuralDx/NeuralDx/requirements.txt:8`).
- **ReportLab** for PDF generation (`/home/runner/work/NeuralDx/NeuralDx/myproject/myapp/views.py:215-218`).

### Package manifests present/missing
- Python dependencies are managed via `requirements.txt` (`/home/runner/work/NeuralDx/NeuralDx/requirements.txt:1-9`).
- No `pyproject.toml` present in repository.
- No `package.json` present in repository (no npm-managed JS dependency manifest).

## Key features

1. **User auth system** (register/login/logout) with registration safeguards (`/home/runner/work/NeuralDx/NeuralDx/myproject/myapp/views.py:18-27`, `44-55`, `327-330`).
2. **Extended user profile data** stored in custom model (`name`, `email`, `phone_number`, `place`) linked to Django user (`/home/runner/work/NeuralDx/NeuralDx/myproject/myapp/models.py:5-11`).
3. **Secure upload path for predictions** with size/type/content validation and temporary file handling (`/home/runner/work/NeuralDx/NeuralDx/myproject/myapp/views.py:118-143`).
4. **Lazy-loaded ML inference** using trained Keras model + class index mapping (`/home/runner/work/NeuralDx/NeuralDx/myproject/myapp/views.py:86-105`, `160-166`; `/home/runner/work/NeuralDx/NeuralDx/myproject/myapp/class_indices.json:1`).
5. **Prediction persistence per user** with timestamp and confidence (`/home/runner/work/NeuralDx/NeuralDx/myproject/myapp/models.py:17-23`; `/home/runner/work/NeuralDx/NeuralDx/myproject/myapp/views.py:173-179`).
6. **History page with class filters** (All/Covid/Normal/Viral Pneumonia) (`/home/runner/work/NeuralDx/NeuralDx/myproject/templates/history.html:39-44`, `49`; `/home/runner/work/NeuralDx/NeuralDx/myproject/static/js/main.js:41-59`).
7. **Profile analytics** showing total analyses and last analysis date (`/home/runner/work/NeuralDx/NeuralDx/myproject/myapp/views.py:205-212`; `/home/runner/work/NeuralDx/NeuralDx/myproject/templates/profile.html:60-66`).
8. **Downloadable PDF diagnostic report** generated server-side from prediction record (`/home/runner/work/NeuralDx/NeuralDx/myproject/myapp/views.py:223-323`; `/home/runner/work/NeuralDx/NeuralDx/myproject/templates/result.html:64-66`).
9. **Training pipeline script** for producing model and class mapping from dataset folders (`/home/runner/work/NeuralDx/NeuralDx/myproject/myapp/training.py:20-22`, `68-70`, `85-122`, `160-161`).
