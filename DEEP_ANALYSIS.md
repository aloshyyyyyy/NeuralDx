# Deep Project Structure & ML Analysis

## 1. Full Folder Structure — IndianShip Project
```
IndianShip Project (at /Users/Aloshy/Codes/intership project)
├── .DS_Store
├── .vscode/
│   └── settings.json
├── INSTRUCTIONS.md
├── RULES.md
├── STATUS.md
├── media/
├── static/
├── venv/
└── myproject/
    ├── db.sqlite3
    ├── manage.py
    ├── media/
    │   └── tmp/
    ├── myapp/
    │   ├── __init__.py
    │   ├── admin.py
    │   ├── apps.py
    │   ├── class_indices.json
    │   ├── migrations/
    │   │   ├── 0001_initial.py
    │   │   └── __init__.py
    │   ├── model_VGG.keras
    │   ├── models.py
    │   ├── tests.py
    │   ├── urls.py
    │   └── views.py
    ├── myproject/
    │   ├── __init__.py
    │   ├── asgi.py
    │   ├── settings.py
    │   ├── urls.py
    │   └── wsgi.py
    ├── static/
    └── templates/
        ├── home.html
        ├── login.html
        ├── register.html
        ├── result.html
        └── upload.html
```

---

## 2. Full Folder Structure — Sample
```
Sample Project (at /Users/Aloshy/Codes/sampleee)
├── .DS_Store
└── sampleee/
    ├── .DS_Store
    ├── manage.py
    ├── media/
    │   └── tmp/
    ├── myapp/
    │   ├── __init__.py
    │   ├── admin.py
    │   ├── apps.py
    │   ├── class_indices.json
    │   ├── emotion.py
    │   ├── final_covid_model.keras
    │   ├── migrations/
    │   │   ├── 0001_initial.py
    │   │   └── __init__.py
    │   ├── model_VGG.h5
    │   ├── model_VGG.keras
    │   ├── models.py
    │   ├── tests.py
    │   ├── training.py
    │   ├── urls.py
    │   └── views.py
    ├── sampleee/
    │   ├── __init__.py
    │   ├── asgi.py
    │   ├── settings.py
    │   ├── urls.py
    │   └── wsgi.py
    └── templates/
        ├── login.html
        ├── reg.html
        ├── result.html
        ├── upload.html
        └── user_home.html
```

---

## 3. ML Files Deep Dive — Sample

- **`training.py`**
  - **What it does:** A Python script that uses TensorFlow/Keras to train a Convolutional Neural Network (CNN) based on the VGG16 architecture. It loads images, applies data augmentation, balances class weights, trains the model, plots accuracy/loss charts, and outputs a confusion matrix.
  - **Dataset Path Expected:** `C:\Users\AKSHAY\Downloads\archive (2)\Covid19-dataset\train` and `...\test`
  - **Model Trained:** `tf.keras.applications.VGG16` (used as a base) with custom Dense layers added on top.
  - **Outputs:** Saves the trained weights to `model_VGG.keras` and the class mapping to `class_indices.json`.
  - **Reusability:** It can be reused, but the hardcoded Windows paths must be changed to local Mac paths.

- **`emotion.py`**
  - **What it does:** Uses OpenCV to activate the laptop webcam, detects human faces, and uses the `deepface` library to predict the person's emotion in real-time, drawing boxes and text over the video feed.
  - **Dataset Path Expected:** None (uses live webcam feed).
  - **Model Trained/Used:** Uses Haar Cascades (OpenCV) for face detection and DeepFace's built-in models for emotion.
  - **Outputs:** Displays a live video window.
  - **Reusability:** Unrelated to the Covid-19 app. Likely a leftover file from another project. **Do not reuse.**

- **`final_covid_model.keras` (134 MB)**
  - **What it is:** Another trained ML model. Likely a different architecture or earlier attempt that wasn't finalized in the web app views.

- **`model_VGG.h5` (62 MB)**
  - **What it is:** The exact same model as `model_VGG.keras`, just saved in the older legacy `.h5` (HDF5) format.

- **`model_VGG.keras` (62 MB)**
  - **What it is:** The primary, active trained model used by the Django web application to make predictions.

- **`class_indices.json`**
  - **What it is:** A simple dictionary mapping numbers (outputs from the model) back to human-readable strings (e.g., `0 -> Covid`).

---

## 4. ML Files Deep Dive — IndianShip Project

- **Model file present:** `model_VGG.keras` (located in `myproject/myapp/`).
- **class_indices.json:** Contains exactly: `{"Covid": 0, "Normal": 1, "Viral Pneumonia": 2}`.
- **How model is loaded:** In `views.py`, it uses a global `get_model()` function that calls `tensorflow.keras.models.load_model(..., compile=False)`. This is a "lazy load" pattern—it only loads the large model into memory the very first time an image is uploaded, rather than every time the server restarts.
- **Status of Model:** It is a fully trained, working model (copied from Sample). It is not a placeholder.

---

## 5. Dataset — What Is Expected
Based on `training.py`, you need to download a dataset with this exact folder structure:

```
Covid19-dataset/
├── train/
│   ├── Covid/
│   │   ├── image1.jpeg
│   │   └── ...
│   ├── Normal/
│   │   ├── image1.jpeg
│   │   └── ...
│   └── Viral Pneumonia/
│       ├── image1.jpeg
│       └── ...
└── test/
    ├── Covid/
    ├── Normal/
    └── Viral Pneumonia/
```

---

## 6. What To Delete
In `IndianShip Project/`:
- **Nothing.** Your current project folder is exceptionally clean. You haven't carried over any of the junk/unused files from the Sample project. You only have the exact files required to run the Django server and make ML predictions.

---

## 7. What To Copy From Sample
To give your project the ability to train its own model (instead of just relying on the pre-trained one), you should copy one file:
- Copy `/Users/Aloshy/Codes/sampleee/sampleee/myapp/training.py`
- Paste it to `/Users/Aloshy/Codes/intership project/myproject/myapp/training.py`

*(Do NOT copy `emotion.py`, `model_VGG.h5`, or `final_covid_model.keras`)*

---

## 8. What To Modify
File: `myproject/myapp/training.py` (after copying)
- **Why:** It contains hardcoded Windows file paths and saves outputs to the current working directory (which can cause issues depending on where you run the script from). 

---

## 9. Training Script Status
- **Does Sample contain a working `training.py`?** Yes. The script is complete and functional.
- **Changes Needed for Mac/IndianShip Project:**
  - **Lines 18-19:** 
    ```python
    # CHANGE THIS:
    train_path = r"C:\Users\AKSHAY\Downloads\archive (2)\Covid19-dataset\train"
    test_path = r"C:\Users\AKSHAY\Downloads\archive (2)\Covid19-dataset\test"
    
    # TO YOUR MAC PATH, e.g.:
    train_path = "/Users/Aloshy/Downloads/Covid19-dataset/train"
    test_path = "/Users/Aloshy/Downloads/Covid19-dataset/test"
    ```
  - **Line 67:**
    ```python
    # CHANGE THIS:
    with open("class_indices.json", "w") as f:
    
    # TO THIS (ensures it saves inside the myapp directory):
    with open(os.path.join(os.path.dirname(__file__), "class_indices.json"), "w") as f:
    ```
  - **Line 159:**
    ```python
    # CHANGE THIS:
    model.save("model_VGG.keras")
    
    # TO THIS (ensures it overwrites the active model file):
    model.save(os.path.join(os.path.dirname(__file__), "model_VGG.keras"))
    ```

---

## 10. Step-By-Step Action Plan
1. **Download Dataset:** Download the dataset to your Mac and extract it so it matches the folder structure outlined in Section 5.
2. **Copy Script:** Copy `training.py` from the Sample project's `myapp` folder into your `IndianShip Project`'s `myapp` folder.
3. **Update Script Paths:** Open your new `training.py` and modify lines 18-19 to point to where you saved the dataset on your Mac.
4. **Update Output Paths:** Modify lines 67 and 159 in `training.py` to use `os.path.join(os.path.dirname(__file__), "filename")` so it outputs the model directly into the `myapp` folder where Django expects it.
5. **Train the Model:** Open your terminal, activate your virtual environment, and run `python myproject/myapp/training.py`. Let it run through the epochs. It will automatically overwrite `model_VGG.keras` and `class_indices.json`.
6. **Test the App:** Run `python myproject/manage.py runserver`, upload a test image via the browser, and ensure your freshly trained model successfully returns a prediction.
