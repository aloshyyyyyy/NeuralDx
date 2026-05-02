# Project Status Report

## 1. What Is This Project
This is a medical image classification web application built with Django. It provides a user authentication system (registration and login) and allows authenticated users to upload images. The uploaded images are then processed and passed through a pre-trained deep learning model (VGG16 architecture via Keras) to predict the image's class, returning the predicted result and a confidence score to the user.

## 2. Tech Stack Detected
- **Web Framework:** Django (Version 4.2.30 in the current project, 5.2 in the sample)
- **Machine Learning / Data Science:** TensorFlow, Keras, NumPy
- **Database:** SQLite3 (in the current project) / MySQL (in the reference sample)
- **Frontend:** HTML, CSS (via Django Templates)
- **Model Architecture:** VGG16 (loaded from `.keras` files)

## 3. What Is Already Done (IndianShip Project)
Your current project (`IndianShip Project/`) is in a very advanced state. The following components are successfully implemented:
- **Project Configuration:** `settings.py` is configured properly with SQLite and static/media directories.
- **Database Models:** A custom `user_table` model extending the built-in `User` model, capturing `name`, `email`, `phone_number`, and `place`.
- **Authentication Views:** Fully functional `login_user`, `login_post`, `register_user`, and `register_post` views. Registration includes password confirmation, duplicate checks, and proper template error rendering.
- **ML Integration Views:** `upload_and_predict` is fully written. It correctly handles file uploads to a temporary directory, loads the VGG16 Keras model, processes the image to 224x224 pixels, makes a prediction, and renders the result.
- **Routing:** `urls.py` correctly maps all views (`login`, `register`, `home`, `upload_get`, `upload_and_predict`).
- **Templates:** Base HTML templates (`login.html`, `register.html`, `home.html`, `upload.html`, `result.html`) are present.
- **ML Assets:** `model_VGG.keras` and `class_indices.json` are successfully placed inside the `myapp` directory.

## 4. What Is In Sample But Missing From My Project
- **Database Configuration:** The Sample project uses MySQL (`mysqlclient`), whereas your project is currently using SQLite.
- **User Groups Authorization:** The Sample project explicitly adds new users to a Django Group named "user" (`Group.objects.get(name="user")`) during registration, and checks if the user is in this group before allowing them to log in. Your project does not use this group-based restriction.
- **Extra ML Training Scripts:** The Sample project contains `training.py` and `emotion.py` in the `myapp` folder, which appear to be scripts used to train or evaluate models.
- **Additional Model Weights:** The Sample project includes `final_covid_model.keras` and an older HDF5 model format `model_VGG.h5`.
- **Specific Naming:** The Sample has views named `login_get` and `user_home` instead of `login_user` and `home`. Its model uses `phone` instead of `phone_number` and `LOGIN` instead of `login`. 

## 5. Differences Between The Two Projects
- **Error Handling:** Your project is arguably **better coded** in its error handling. The Sample project returns raw `HttpResponse` strings with inline JavaScript (`<script>alert(...)`) to show errors. Your project properly passes `error_message` context variables to Django templates.
- **User Creation:** Your project uses Django's secure `User.objects.create_user()`. The Sample project creates the user manually and uses `make_password()`.
- **Model Fields:** Your `user_table` model has an extra field (`place`) which the sample lacks.
- **Overall Quality:** The `IndianShip Project` follows Django conventions much closer than the `Sample` project. 

## 6. ML Model Details
- **Model Used:** The active model in `views.py` for both projects is `model_VGG.keras`.
- **Location:** It is stored inside the app directory at `myapp/model_VGG.keras`.
- **Loading Mechanism:** It is lazy-loaded using a global `get_model()` function to avoid loading the heavy model on every single request. It utilizes `tensorflow.keras.models.load_model(..., compile=False)`.
- **Class Mapping:** The numeric predictions are mapped to human-readable class names using the dictionary loaded from `myapp/class_indices.json`.
- **Preprocessing:** Uploaded images are resized to 224x224, converted to arrays, expanded in dimensions, and preprocessed using `tensorflow.keras.applications.vgg16.preprocess_input` before being fed into `model.predict()`.

## 7. Current Progress Estimate
**Estimate: 95% Complete.** 
The core application flow—from registration to image upload to ML prediction—is entirely present and well-structured. The only missing elements are either minor configurations (like MySQL) or legacy training scripts from the sample that aren't strictly required for the web application to run. 

## 8. Recommended Next Steps
1. **Verify Database Needs:** Decide if you must use MySQL. If so, update your `DATABASES` setting in `settings.py` and install `mysqlclient`. If SQLite is acceptable, you can skip this.
2. **Review Group Authentication:** Determine if your project requirements specifically ask for role-based authentication (checking for the "user" group). If required, add the `Group` assignment logic to your `register_post` view.
3. **Template Polish:** Ensure your frontend templates (`home.html`, `upload.html`, `result.html`) look good and function properly with your new views.
4. **Test the Pipeline:** Run `python manage.py runserver`, register a user, upload a test image, and verify that the model correctly outputs a prediction without crashing.
