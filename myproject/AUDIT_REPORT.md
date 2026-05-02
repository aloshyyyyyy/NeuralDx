# NeuralDx Security & Code Audit Report

**Project audited:** `/Users/Aloshy/Codes/intership project/myproject/`  
**Audit type:** Pre-publication security + quality review for a medical AI web app  
**Scope reviewed:** Django backend, templates, static assets, migrations, model/training artifacts, local data artifacts

---

## 1. CRITICAL SECURITY VULNERABILITIES

### CV-01: Unsafe fallback `SECRET_KEY` allows predictable cryptographic signing
- **File/line:** `myproject/settings.py:29`
- **Risk:** If `.env` is missing, app uses a known fallback (`default-unsafe-secret-key`). Attackers can forge signed cookies/tokens.
- **Exploit path:** Deploy without `SECRET_KEY` env var -> attacker signs session/csrf-related values.

| Bad code | Corrected code |
|---|---|
|```python<br>SECRET_KEY = os.environ.get('SECRET_KEY', 'default-unsafe-secret-key')<br>```|```python<br>SECRET_KEY = os.environ['SECRET_KEY']  # fail fast if missing<br>```|

---

### CV-02: Missing auth guard on inference endpoint enables anonymous model abuse + server errors
- **File/line:** `myapp/views.py:105-160`, route in `myapp/urls.py:13`
- **Risk:** Unauthenticated users can POST files to expensive model inference; DoS risk and noisy error paths.
- **Exploit path:** Repeated anonymous POSTs to `/upload_and_predict/` consume CPU/GPU and storage IO.

| Bad code | Corrected code |
|---|---|
|```python<br>def upload_and_predict(request):<br>    if request.method == 'POST' and request.FILES.get('image'):<br>        ...<br>        prediction_record = Prediction.objects.create(user=request.user, ...)<br>```|```python<br>from django.views.decorators.http import require_POST<br><br>@login_required(login_url='/login/')<br>@require_POST<br>def upload_and_predict(request):<br>    file = request.FILES.get('image')<br>    if not file:<br>        return render(request, 'upload.html', {'error': 'Image is required.'}, status=400)<br>    ...<br>```|

---

### CV-03: Unsafe model loading (`safe_mode=False`) can enable malicious model deserialization behavior
- **File/line:** `myapp/views.py:92-96`
- **Risk:** Loading compromised model artifacts with unsafe mode increases risk of unsafe object deserialization behavior.
- **Exploit path:** Attacker replaces model file in deployment pipeline/repo artifact.

| Bad code | Corrected code |
|---|---|
|```python<br>model = keras.models.load_model(<br>    MODEL_PATH,<br>    compile=False,<br>    safe_mode=False<br>)<br>```|```python<br>model = keras.models.load_model(<br>    MODEL_PATH,<br>    compile=False,<br>    safe_mode=True<br>)<br>```|

---

### CV-04: No server-side file type/size validation on upload
- **File/line:** `myapp/views.py:106-118`; client-only hint at `templates/upload.html:55`
- **Risk:** Non-image payloads or extremely large files can trigger parser crashes, memory pressure, or storage exhaustion.
- **Exploit path:** Upload huge/decompression-bomb/non-image file to inference endpoint.

| Bad code | Corrected code |
|---|---|
|```python<br>file = request.FILES['image']<br>file_name = default_storage.save('tmp/' + file.name, file)<br>img = keras.utils.load_img(file_path, target_size=(IMG_SIZE, IMG_SIZE), color_mode='rgb')<br>```|```python<br>from PIL import Image, UnidentifiedImageError<br>from django.core.exceptions import ValidationError<br><br>MAX_UPLOAD_MB = 5<br>if file.size > MAX_UPLOAD_MB * 1024 * 1024:<br>    raise ValidationError('File exceeds 5MB limit.')<br><br>if file.content_type not in {'image/jpeg', 'image/png'}:<br>    raise ValidationError('Only JPEG/PNG files are allowed.')<br><br>try:<br>    with Image.open(file) as im:<br>        im.verify()<br>except UnidentifiedImageError:<br>    raise ValidationError('Uploaded file is not a valid image.')<br>file.seek(0)<br>```|

---

### CV-05: Raw exception messages are returned to end users (information disclosure)
- **File/line:** `myapp/views.py:67`, `myapp/views.py:155`
- **Risk:** Internal errors, model/db/storage details are exposed in UI.
- **Exploit path:** Trigger failures intentionally (bad file, DB lock) and collect internals from error responses.

| Bad code | Corrected code |
|---|---|
|```python<br>except Exception as e:<br>    return render(request, 'upload.html', {'error': str(e)})<br>```|```python<br>import logging<br>logger = logging.getLogger(__name__)<br><br>except Exception:<br>    logger.exception('Prediction failed')<br>    return render(request, 'upload.html', {'error': 'Prediction failed. Please try again.'}, status=500)<br>```|

---

### CV-06: Patient data artifacts committed in repo (`db.sqlite3` + medical images in `media/`)
- **Files:** `db.sqlite3`, `media/predictions/*`
- **Risk:** PII/medical image leakage, compliance breach before/after public GitHub release.
- **Exploit path:** Anyone cloning/publicly browsing repo downloads patient history and scans.
- **Fix:** Remove from version control, rotate data, add `.gitignore`:

```gitignore
db.sqlite3
media/
.env
__pycache__/
*.pyc
```

---

### Additional critical checks
- **`DEBUG = True` hardcoded?** **No** (`myproject/settings.py:32` reads env; default evaluates to False).  
- **SQL injection in code paths reviewed?** **No direct SQL construction found** (ORM used).  
- **`eval()`/`exec()` usage?** **None found**.  
- **Missing CSRF middleware/forms?** Middleware enabled and form templates include `{% csrf_token %}`.

---

## 2. AUTHENTICATION & AUTHORIZATION ISSUES

### Findings
1. **Unauthenticated access to core pages**
   - `myapp/views.py:99-103` (`home`, `upload_get`) not protected.
   - Allows logged-out users into app flow that should be account-bound.

2. **Inference endpoint lacks auth decorator**
   - `myapp/views.py:105` (`upload_and_predict`) accepts unauthenticated POST.

3. **Report download ownership check is good**
   - `myapp/views.py:196` scopes by `id` and `user=request.user`; protects IDOR.

4. **No logout view**
   - UI “Logout” points to `/login/` in templates (`home.html:21`, `upload.html:21`, `history.html:23`, `profile.html:21`, `result.html:21`) but session is not invalidated.

### Recommended auth patch
```python
from django.contrib.auth import logout
from django.views.decorators.http import require_http_methods, require_POST

@login_required(login_url='/login/')
def home(request): ...

@login_required(login_url='/login/')
def upload_get(request): ...

@login_required(login_url='/login/')
@require_POST
def upload_and_predict(request): ...

@require_http_methods(["POST"])
def logout_user(request):
    logout(request)
    return redirect('/login/')
```

---

## 3. FILE UPLOAD SECURITY

### Findings
- **No server-side MIME/content verification** (`myapp/views.py:106-118`) -> **HIGH**  
- **No server-side size limit** (`myapp/views.py`) despite UI text “Max 5MB” (`templates/upload.html:55`) -> **HIGH**  
- **Original filename reused in temp path** (`myapp/views.py:108`) -> **MEDIUM** (normalize with `os.path.basename` + generated UUID filename).  
- **Temp cleanup implemented** (`myapp/views.py:157-158`) -> **GOOD**.  
- **Media served in DEBUG URL config** (`myproject/urls.py:27-28`) -> acceptable for dev, not production pattern.

### Fix sketch
```python
import uuid, os
safe_name = f"{uuid.uuid4().hex}{os.path.splitext(file.name)[1].lower()}"
file_name = default_storage.save(f"tmp/{safe_name}", file)
```

---

## 4. ML MODEL SECURITY

### Findings
- **Unsafe load mode** (`safe_mode=False`, `myapp/views.py:95`) -> **CRITICAL**.
- **No pre-inference hard validation** on shape, MIME, file size -> **HIGH**.
- **Inference runs synchronously in request thread** (`myapp/views.py:128`) -> availability risk under load.
- **Model file exposure via URL:** not directly served (stored under `myapp/model_VGG.keras`) -> **No direct issue found**.

---

## 5. CODE QUALITY ISSUES

| File:line | Issue | Severity | Fix |
|---|---|---|---|
| `myapp/views.py:134-137` | Debug `print()` in production path | MEDIUM | Replace with structured logging or remove |
| `myapp/views.py:66-67`, `154-155` | Broad `except Exception` with user-facing internals | HIGH | Catch specific exceptions + generic safe message |
| `myapp/views.py:12`, `28` | `login_post`/`register_post` missing explicit method constraints | MEDIUM | Add `@require_POST` |
| `myapp/views.py:170-173` | Multiple related queries without helper/service split | LOW | Refactor profile aggregation into helper |
| `myapp/views.py:188` | `datetime` imported but unused | LOW | Remove dead import |
| `myapp/models.py:5` | Model name `user_table` not PEP8/Django conventional | LOW | Rename to `UserProfile` (migration required) |
| `myapp/tests.py` | No tests implemented | HIGH | Add auth/upload/prediction/report access tests |

---

## 6. DJANGO BEST PRACTICES VIOLATIONS

### Violations
- **Raw `request.POST` instead of Django Forms** in auth/registration/upload (`myapp/views.py`) -> weaker validation and maintainability.
- **Method guards missing** on state-changing endpoints (`login_post`, `register_post`, `upload_and_predict`).
- **No `.gitignore` present** (project root scan found none).
- **User model profile uses non-idiomatic name** (`user_table`).

### Positive checks
- `__str__` methods exist for both models (`myapp/models.py:14-15`, `24-25`).
- CSRF middleware enabled and tokens present on forms.
- Migrations exist for current models (`0001_initial.py`, `0002_prediction.py`).

---

## 7. TEMPLATE SECURITY

### Findings
- **No direct XSS sinks found**; templates rely on Django auto-escaping.
- Dynamic output uses `{{ ... }}` safely across reviewed templates.
- **Inline JS in `history.html:79-89` does not inject unescaped user input**.

### Minor concern
- Result-driven CSS class generation (`templates/result.html:27,40,50,59`) assumes trusted `result` values. If DB tampered, could break UI (not direct XSS due escaping + slugify).

---

## 8. PERFORMANCE ISSUES

### Findings
1. **Model is lazily cached globally** (`myapp/views.py:88-97`) -> good baseline.
2. **Prediction is synchronous** (`myapp/views.py:128`) -> request blocking, poor scalability.
3. **No upload pre-resize/compression before save** -> storage growth risk.
4. **No request throttling/rate limiting** on inference endpoint.
5. **No DB index on `Prediction.created_at` / `Prediction.user` explicitly declared** (FK index usually created; consider composite index on `(user, -created_at)` for history sorting).

---

## 9. ERROR HANDLING GAPS

| Scenario | Current behavior | Gap |
|---|---|---|
| Non-image upload | Exception from image loader, raw message returned (`views.py:155`) | Internal details leak |
| Missing model file | Exception during `load_model`, shown to user | Internal path/config leak |
| DB locked on create | Exception string shown | No retry/friendly handling |
| Disk full on temp save | Failure occurs before `try` block (`views.py:108-111`) | Unhandled 500 risk |
| Production traceback visibility | Controlled by env-driven DEBUG | Safe if env set correctly; unsafe if misconfigured |

---

## 10. DEPENDENCY AUDIT

### Package source of truth status
- **`requirements.txt` / lockfile:** **Missing** (none found in root).
- Result: exact reproducible dependency and CVE mapping is incomplete.

### Inferred dependencies from imports
- Django, python-dotenv, numpy, tensorflow, reportlab, pillow, matplotlib, seaborn, scikit-learn.

### Locally detectable versions (from `pip show` in current environment)
- python-dotenv `1.2.1`
- numpy `2.0.2`
- reportlab `4.5.0`
- pillow `11.3.0`
- (Django/tensorflow/matplotlib/seaborn/scikit-learn not resolved in current interpreter)

### Security readiness findings
1. **No pinned requirements file** -> **HIGH** supply-chain and reproducibility risk.
2. **No automated vulnerability scan artifact** (`pip-audit`/`safety`) committed -> **MEDIUM**.
3. `training.py` imports heavy data science stack in app repo; if not needed in production runtime, split to separate training environment to reduce attack surface.

---

## 11. GITHUB / PUBLIC REPO READINESS

### Findings
- **Do not publish:** `db.sqlite3`, `media/predictions/*` (sensitive medical/user data).
- **Hardcoded local absolute paths in training script**
  - `myapp/training.py:18-19` contains `/Users/Aloshy/...` paths -> portability leak.
- **No `.gitignore` present** -> high risk of accidental secret/data commits.
- **No README found** -> project not reproducible for external users.
- **Potential sensitive secret fallback in code** (`settings.py:29`) should be removed.
- **Debug artifacts present**
  - `views.py:134-137` debug prints
  - `.DS_Store`, `__pycache__`, `.pyc` files in tree

---

## 12. PRIORITY FIX LIST (MOST CRITICAL -> LEAST)

1. **Remove sensitive data from repo** — **CRITICAL** — **~1-2h** — Delete `db.sqlite3`/`media`, rotate data, add `.gitignore`.
2. **Fix secret management** — **CRITICAL** — **~15-30m** — Remove insecure `SECRET_KEY` fallback and enforce env-only key.
3. **Protect inference endpoint with auth + method guard** — **CRITICAL** — **~30-60m** — Add `@login_required` + `@require_POST`, deny anonymous inference.
4. **Enable strict server-side upload validation** — **HIGH** — **~1-2h** — MIME/content/size validation + safe filename generation.
5. **Set `safe_mode=True` for model loading** — **HIGH** — **~15m** — Eliminate unsafe model loading mode.
6. **Stop leaking raw exceptions to users** — **HIGH** — **~30-60m** — Log server-side, return generic user-safe errors.
7. **Implement real logout endpoint** — **MEDIUM** — **~20-40m** — Invalidate session instead of linking to login page.
8. **Add requirements lock + dependency scanning** — **MEDIUM** — **~30-60m** — Pin versions and run CVE scans.
9. **Replace raw POST handling with Django Forms** — **MEDIUM** — **~2-4h** — Strong validation + cleaner security posture.
10. **Refactor naming/tests/cleanup debug artifacts** — **LOW** — **~2-3h** — Rename `user_table`, remove debug prints, add tests.

---

## 13. OVERALL SCORE

- **Security:** **3/10**
- **Code Quality:** **5/10**
- **Django Best Practices:** **4/10**
- **Production Readiness:** **2/10**
- **Overall:** **3.5/10**

NeuralDx has a functional base but is **not safe for public release** in its current state. The major blockers are repository data exposure, insecure secret fallback, insufficient upload hardening, and weak auth boundaries around expensive ML operations. Address the top critical fixes before publishing or deploying.

