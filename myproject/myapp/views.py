from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from .models import user_table, Prediction


def login_user(request):
    return render(request, 'login.html')


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
    except Exception as e:
        return render(request, 'register.html', {'error_message': f'Error creating account: {str(e)}'})

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
            safe_mode=False
        )
    return model

def home(request):
    return render(request, 'home.html')

def upload_get(request):
    return render(request, 'upload.html')

def upload_and_predict(request):
    if request.method == 'POST' and request.FILES.get('image'):
        file = request.FILES['image']
        file_name = default_storage.save('tmp/' + file.name, file)
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
            print("Raw predictions:", predictions)
            print("Predicted index:", predicted_index)
            print("Predicted class:", predicted_class)

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
                'image_url': prediction_record.image.url
            })

        except Exception as e:
            return render(request, 'upload.html', {'error': str(e)})

        finally:
            default_storage.delete(file_name)

    return render(request, 'upload.html')

def history(request):
    if not request.user.is_authenticated:
        return redirect('/login/')
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