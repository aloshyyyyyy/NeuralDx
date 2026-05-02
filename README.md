# NeuralDx — AI Medical Image Diagnostic Tool

A web-based medical image classification application built with Django and deep learning. Upload a chest X-ray scan and receive an instant AI-powered diagnosis.

![Python](https://img.shields.io/badge/Python-3.9-blue)
![Django](https://img.shields.io/badge/Django-4.2-green)
![TensorFlow](https://img.shields.io/badge/TensorFlow-2.16-orange)
![Accuracy](https://img.shields.io/badge/Accuracy-91%25-brightgreen)

---

## What It Does

- User registers and logs in securely
- Uploads a chest X-ray or lung scan image
- A trained VGG16 deep learning model analyzes the scan
- Returns a diagnosis: **Covid**, **Normal**, or **Viral Pneumonia**
- Shows AI confidence percentage
- Saves prediction history per user
- User profile with total analysis stats

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python, Django 4.2 |
| Machine Learning | TensorFlow, Keras, VGG16 |
| Database | SQLite3 |
| Frontend | HTML, CSS (custom), Django Templates |
| Model Training | Transfer Learning on Covid19 Dataset |

---

## Model Performance

- **Architecture:** VGG16 (pretrained on ImageNet, fine-tuned)
- **Training:** 50 epochs, 201 training images
- **Test Accuracy:** 91% on 66 test images
- **Classes:** Covid, Normal, Viral Pneumonia

| Class | Precision | Recall | F1-Score |
|---|---|---|---|
| Covid | 1.00 | 0.96 | 0.98 |
| Normal | 0.94 | 0.75 | 0.83 |
| Viral Pneumonia | 0.80 | 1.00 | 0.89 |

---

## Project Structure

```
myproject/
├── myapp/
│   ├── templates/          # HTML templates
│   ├── static/             # CSS and JS files
│   ├── views.py            # App logic and ML prediction
│   ├── models.py           # Database models
│   ├── urls.py             # URL routing
│   └── training.py         # Model training script
├── myproject/
│   ├── settings.py
│   └── urls.py
└── manage.py
```

---

## Setup & Installation

### 1. Clone the repository
```bash
git clone https://github.com/yourusername/neuraldx.git
cd neuraldx
```

### 2. Create virtual environment
```bash
python -m venv venv
source venv/bin/activate  # Mac/Linux
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Run migrations
```bash
cd myproject
python manage.py migrate
```

### 5. Train the model (required — model file not included)
- Download the Covid19 dataset and place it at the path specified in `training.py`
- Update `train_path` and `test_path` in `myapp/training.py`
- Run:
```bash
python myapp/training.py
```

### 6. Start the server
```bash
python manage.py runserver
```

Open `http://127.0.0.1:8000` in your browser.

---

## Important Notes

- The trained model file (`.keras`) is not included in this repo due to file size limits
- You must train the model yourself using `training.py` before running the app
- The dataset is not included — obtain the Covid19 chest X-ray dataset separately

---

## Screenshots

> *(Add screenshots of login, dashboard, upload, and result pages here)*

---

## Disclaimer

This tool is for educational purposes only. It is not a substitute for professional medical diagnosis. Always consult a qualified doctor.

---

## Developer

Built by **Aloshy** as part of an internship project.
