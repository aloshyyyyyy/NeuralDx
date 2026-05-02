from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST, require_http_methods
from .models import user_table, Prediction
from PIL import Image, UnidentifiedImageError
import uuid
import logging
logger = logging.getLogger(__name__)


def login_user(request):
    return render(request, 'login.html')


@require_POST
def login_post(request):
    username = request.POST.get('username')
    password = request.POST.get('password')

    user = authenticate(request, username=username, password=password)
    if user is not None:
        login(request, user)
        return redirect('/home/')

    return redirect('/login/')


def register_user(request):
    return render(request, 'register.html')


@require_POST
def register_post(request):
    name = request.POST.get('name')
    username = request.POST.get('username')
    email = request.POST.get('email')
    phone_number = request.POST.get('phone_number')
    place = request.POST.get('place')
    password = request.POST.get('password')
    password_confirm = request.POST.get('password_confirm')

    # Check if passwords match
    if password != password_confirm:
        return render(request, 'register.html', {'error_message': 'Passwords do not match!'})

    # Check if username already exists
    if User.objects.filter(username=username).exists():
        return render(request, 'register.html', {'error_message': 'Username already taken!'})

    # Check if email already exists
    if User.objects.filter(email=email).exists():
        return render(request, 'register.html', {'error_message': 'Email already registered!'})

    # Create new user
    try:
        user = User.objects.create_user(username=username, email=email, password=password)
        user.save()

        # Create user_table entry with additional info
        user_info = user_table(
            name=name,
            email=email,
            phone_number=phone_number,
            place=place,
            login=user
        )
        user_info.save()

        login(request, user)
        return redirect('/home/')
    except Exception:
        logger.exception('An error occurred during prediction')
        return render(request, 'register.html', {'error_message': 'Error creating account. Please try again.'})

import numpy as np
import os
import json
from django.core.files.storage import default_storage
from django.conf import settings
import tensorflow as tf

keras = tf.keras

MODEL_PATH = os.path.join(settings.BASE_DIR, 'myapp', 'model_VGG.keras')
CLASS_INDEX_PATH = os.path.join(settings.BASE_DIR, 'myapp', 'class_indices.json')

# ✅ Load class indices
with open(CLASS_INDEX_PATH) as f:
    class_indices = json.load(f)

class_names = {v: k for k, v in class_indices.items()}

# ✅ Lazy load model
model = None
def get_model():
    global model
    if model is None:
        model = keras.models.load_model(
            MODEL_PATH,
            compile=False,
            safe_mode=True
        )
    return model

@login_required(login_url='/login/')
def home(request):
    return render(request, 'home.html')

@login_required(login_url='/login/')
def upload_get(request):
    return render(request, 'upload.html')

@login_required(login_url='/login/')
@require_POST
def upload_and_predict(request):
    file = request.FILES.get('image')
    if not file:
        return render(request, 'upload.html', {'error': 'No image file provided.'})

    # Size check — max 5MB
    if file.size > 5 * 1024 * 1024:
        return render(request, 'upload.html', {'error': 'File size exceeds 5MB limit.'})

    # MIME type check
    allowed_types = {'image/jpeg', 'image/png'}
    if file.content_type not in allowed_types:
        return render(request, 'upload.html', {'error': 'Only JPEG and PNG files are allowed.'})

    # Real image content verification
    try:
        with Image.open(file) as im:
            im.verify()
    except (UnidentifiedImageError, Exception):
        return render(request, 'upload.html', {'error': 'Uploaded file is not a valid image.'})
    file.seek(0)

    # Safe filename using UUID
    safe_name = f"{uuid.uuid4().hex}{os.path.splitext(file.name)[1].lower()}"
    file_name = default_storage.save('tmp/' + safe_name, file)
    file_path = default_storage.path(file_name)

    try:
        IMG_SIZE = 224

        img = keras.utils.load_img(
            file_path,
            target_size=(IMG_SIZE, IMG_SIZE),
            color_mode='rgb'
        )

        img_array = keras.utils.img_to_array(img)

        from tensorflow.keras.applications.vgg16 import preprocess_input
        img_array = preprocess_input(img_array)

        img_array = np.expand_dims(img_array, axis=0)

        model = get_model()
        predictions = model.predict(img_array)

        predicted_index = int(np.argmax(predictions))
        predicted_class = class_names[predicted_index]
        confidence = round(100 * np.max(predictions), 2)

        # 🔍 DEBUG
        logger.debug("Raw predictions: %s", predictions)
        logger.debug("Predicted index: %s", predicted_index)
        logger.debug("Predicted class: %s", predicted_class)

        file.seek(0)
        prediction_record = Prediction.objects.create(
            user=request.user,
            image=file,
            result=predicted_class,
            confidence=confidence
        )

        return render(request, 'result.html', {
            'result': predicted_class,
            'confidence': confidence,
            'image_url': prediction_record.image.url,
            'prediction_id': prediction_record.id
        })

    except Exception:
        logger.exception('An error occurred during prediction')
        return render(request, 'upload.html', {'error': 'Something went wrong. Please try again.'})

    finally:
        default_storage.delete(file_name)

    return render(request, 'upload.html')

@login_required(login_url='/login/')
def history(request):
    predictions = Prediction.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'history.html', {'predictions': predictions})

@login_required(login_url='/login/')
def profile(request):
    user_info = user_table.objects.filter(login=request.user).first()
    predictions = Prediction.objects.filter(user=request.user).order_by('-created_at')
    total_predictions = predictions.count()
    last_prediction = predictions.first()
    
    context = {
        'user_info': user_info,
        'total_predictions': total_predictions,
        'last_prediction_date': last_prediction.created_at if last_prediction else None
    }
    return render(request, 'profile.html', context)

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from django.http import HttpResponse
import os
from datetime import datetime

@login_required(login_url='/login/')
def download_report(request, prediction_id):
    
    # Fetch the prediction record
    from .models import Prediction
    prediction = Prediction.objects.get(id=prediction_id, user=request.user)
    
    # Create PDF response
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="NeuralDx_Report_{prediction.id}.pdf"'
    
    # Draw PDF
    p = canvas.Canvas(response, pagesize=A4)
    width, height = A4
    
    # Colors
    if prediction.result == "Covid":
        accent = colors.HexColor('#ef4444')
    elif prediction.result == "Normal":
        accent = colors.HexColor('#10b981')
    else:
        accent = colors.HexColor('#f97316')
    
    # Header bar
    p.setFillColor(colors.HexColor('#0f172a'))
    p.rect(0, height - 60*mm, width, 60*mm, fill=1, stroke=0)
    
    # App name
    p.setFillColor(colors.white)
    p.setFont("Helvetica-Bold", 24)
    p.drawString(20*mm, height - 25*mm, "NeuralDx")
    p.setFont("Helvetica", 11)
    p.setFillColor(colors.HexColor('#94a3b8'))
    p.drawString(20*mm, height - 35*mm, "AI-Powered Medical Diagnostic Report")
    
    # Report date top right
    p.setFont("Helvetica", 9)
    date_str = prediction.created_at.strftime("%B %d, %Y  %I:%M %p")
    p.drawRightString(width - 20*mm, height - 25*mm, date_str)
    
    # Accent bar
    p.setFillColor(accent)
    p.rect(0, height - 63*mm, width, 3*mm, fill=1, stroke=0)
    
    # Scan image
    if prediction.image:
        img_path = prediction.image.path
        if os.path.exists(img_path):
            img_y = height - 145*mm
            p.drawImage(img_path, 20*mm, img_y, width=80*mm, height=70*mm, preserveAspectRatio=True)
    
    # Result section
    p.setFillColor(colors.HexColor('#0f172a'))
    p.setFont("Helvetica-Bold", 11)
    p.drawString(115*mm, height - 80*mm, "DIAGNOSTIC RESULT")
    
    p.setFillColor(accent)
    p.setFont("Helvetica-Bold", 28)
    p.drawString(115*mm, height - 95*mm, prediction.result)
    
    p.setFillColor(colors.HexColor('#475569'))
    p.setFont("Helvetica", 11)
    p.drawString(115*mm, height - 108*mm, f"AI Confidence: {prediction.confidence:.2f}%")
    
    # Confidence bar
    bar_x = 115*mm
    bar_y = height - 118*mm
    bar_w = 75*mm
    bar_h = 4*mm
    p.setFillColor(colors.HexColor('#e2e8f0'))
    p.roundRect(bar_x, bar_y, bar_w, bar_h, 2*mm, fill=1, stroke=0)
    fill_w = bar_w * (prediction.confidence / 100)
    p.setFillColor(accent)
    p.roundRect(bar_x, bar_y, fill_w, bar_h, 2*mm, fill=1, stroke=0)
    
    # Patient info section
    p.setFillColor(colors.HexColor('#f8faff'))
    p.rect(20*mm, height - 185*mm, width - 40*mm, 30*mm, fill=1, stroke=0)
    p.setFillColor(colors.HexColor('#94a3b8'))
    p.setFont("Helvetica", 9)
    p.drawString(25*mm, height - 163*mm, "PATIENT")
    p.drawString(100*mm, height - 163*mm, "ANALYSIS DATE")
    p.drawString(175*mm, height - 163*mm, "REPORT ID")
    p.setFillColor(colors.HexColor('#0f172a'))
    p.setFont("Helvetica-Bold", 10)
    p.drawString(25*mm, height - 172*mm, request.user.username)
    p.drawString(100*mm, height - 172*mm, prediction.created_at.strftime("%d %b %Y"))
    p.drawString(175*mm, height - 172*mm, f"#{prediction.id:04d}")
    
    # Disclaimer
    p.setFillColor(colors.HexColor('#94a3b8'))
    p.setFont("Helvetica-Oblique", 8)
    p.drawCentredString(width/2, 20*mm, "This is an AI-generated result for educational purposes only. Please consult a qualified medical professional.")
    
    # Footer line
    p.setStrokeColor(colors.HexColor('#e2e8f0'))
    p.line(20*mm, 28*mm, width - 20*mm, 28*mm)
    
    p.showPage()
    p.save()
    return response

from django.contrib.auth import logout as auth_logout

@require_http_methods(["GET", "POST"])
def logout_user(request):
    auth_logout(request)
    return redirect('/login/')