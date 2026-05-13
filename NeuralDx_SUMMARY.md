# NeuralDx Summary

## What it does
NeuralDx is a Django web app for authenticated users to upload chest scan images and receive an AI classification result. It predicts one of three classes (`Covid`, `Normal`, `Viral Pneumonia`) with a confidence score using a saved TensorFlow/Keras model. The app also stores each user’s prediction history and lets users download a styled PDF report for a specific result.

## How it works
1. **Routing and auth entrypoints**: Root URLs include `myapp.urls`, which exposes login/register/logout, dashboard, upload, prediction, history, profile, and report download routes.
2. **User registration/login**:
   - `register_post` validates password confirmation and uniqueness of username/email, creates a Django `User`, then creates a linked `user_table` profile record.
   - `login_post` authenticates with Django auth and starts a session.
3. **Protected app pages**: `home`, `upload_get`, `history`, `profile`, and `download_report` require authentication via `@login_required`.
4. **Model/class mapping load**:
   - `views.py` reads `myapp/class_indices.json` at import time and inverts it for numeric-index-to-class lookup.
   - `get_model()` lazily loads `myapp/model_VGG.keras` once using `keras.models.load_model(..., compile=False, safe_mode=True)`.
5. **Upload validation and preprocessing (`upload_and_predict`)**:
   - Requires POST and uploaded file presence.
   - Enforces max size (5 MB), MIME type allowlist (`image/jpeg`, `image/png`), and real image verification with Pillow (`Image.verify()`).
   - Stores a temporary UUID-based filename under `media/tmp/`.
   - Loads/resizes image to `224x224`, converts to array, applies `tensorflow.keras.applications.vgg16.preprocess_input`, and expands batch dimension.
6. **Prediction and persistence**:
   - Runs `model.predict(...)`, selects argmax class index, maps to class name, computes confidence percentage.
   - Saves a `Prediction` row (`user`, uploaded `ImageField`, result, confidence, timestamp).
   - Renders `result.html` with result, confidence, image URL, and prediction ID.
   - Deletes temporary upload in `finally`.
7. **History/profile/reporting**:
   - `history` lists user predictions ordered newest-first.
   - `profile` shows linked profile fields and aggregate stats (`total_predictions`, `last_prediction_date`).
   - `download_report` generates a PDF with ReportLab (result styling, confidence bar, scan image, metadata, disclaimer) and returns it as an attachment.
8. **Training pipeline (`training.py`)**:
   - Uses `ImageDataGenerator` + VGG16 transfer learning, class-weight balancing, early stopping, and 50-epoch training.
   - Writes `class_indices.json` and saves trained model to `myapp/model_VGG.keras`.

## Tech stack
- **Backend framework**: Django (`requirements.txt`: `Django>=4.2`)
- **Language/runtime**: Python
- **Database**: SQLite (`settings.py` uses `django.db.backends.sqlite3`)
- **ML/AI libraries**:
  - TensorFlow / Keras (`tensorflow-macos`, `tensorflow-metal` in requirements; `tensorflow` imports in app/training code)
  - NumPy
  - scikit-learn (`compute_class_weight`, `classification_report`, `confusion_matrix`)
- **Image/data processing**:
  - Pillow (`PIL.Image`, `UnidentifiedImageError`)
  - Matplotlib
  - Seaborn
- **PDF generation**:
  - ReportLab (`reportlab.lib.*`, `reportlab.pdfgen.canvas`)
- **Config/env**:
  - `python-dotenv` (`load_dotenv` in Django settings)
  - `.env` / `.env.example` for `SECRET_KEY`, `DEBUG`, `ALLOWED_HOSTS`
- **Frontend**:
  - Django templates (HTML)
  - Custom CSS (`myproject/static/css/style.css`)
  - Vanilla JavaScript (`myproject/static/js/main.js`)
  - External UI assets via CDN: Google Fonts (Inter), Bootstrap Icons (jsDelivr)
- **Storage/media handling**:
  - Django `default_storage`, `MEDIA_ROOT`, `MEDIA_URL`, `ImageField` uploads

## Key features
- Secure session-based authentication flow (register/login/logout) with server-side validation for duplicate username/email and password confirmation.
- Auth-protected AI diagnosis workflow with strict upload checks (size, MIME, and binary image verification).
- Lazy model loading to avoid repeated model initialization on each request.
- End-to-end prediction persistence (`Prediction` model) with per-user history and timestamps.
- Interactive frontend behaviors: upload preview + enable submit button, animated confidence bar, and client-side history filtering by diagnosis class.
- Profile dashboard with user metadata (`user_table`) and usage stats.
- Downloadable, branded PDF diagnostic report per prediction.
- Included training script for rebuilding the VGG16-based classifier and regenerating class-index/model artifacts.
