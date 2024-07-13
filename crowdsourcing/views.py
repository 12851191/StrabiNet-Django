import os
from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.http import JsonResponse, HttpResponse
from django.core.mail import send_mail
import firebase_admin
from .models import UploadedImage
from firebase_admin import auth, credentials, exceptions
from django.views.decorators.csrf import csrf_exempt
import json
import shutil
import tempfile
import zipfile
from django.conf import settings
import sqlite3
from .models import UploadedImage
from .firebase_config import *
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required

def send_verification_email(email, link):
    subject = 'Verify your email address'
    message = f'Please click the following link to verify your email address: {link}'
    from_email = 'arnavsharma.0914@gmail.com'
    recipient_list = [email]
    send_mail(subject, message, from_email, recipient_list)

def signup_view(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']

        try:
            validate_email(email)
        except ValidationError:
            return render(request, 'signup.html', {'error': 'Invalid email format'})

        if len(password) < 6:
            return render(request, 'signup.html', {'error': 'Password must be at least 6 characters long'})

        if password != confirm_password:
            return render(request, 'signup.html', {'error': 'Passwords do not match'})

        try:
            user_record = auth.create_user(email=email, password=password)
            link = auth.generate_email_verification_link(email)
            send_verification_email(email, link)
            messages.success(request, 'Account created successfully. Please verify your email.')
            return redirect('login')
        except firebase_admin.exceptions.FirebaseError:
            return render(request, 'signup.html', {'error': 'Failed to create account'})

    return render(request, 'signup.html')

def login_view(request):
    if request.method == 'POST':
        body = json.loads(request.body)
        id_token = body.get('idToken')

        try:
            decoded_token = auth.verify_id_token(id_token)
            user = auth.get_user(decoded_token['uid'])
            if not user.email_verified:
                return JsonResponse({'status': 'error', 'message': 'Email not verified.'})
            request.session['user_id'] = decoded_token['uid']
            return JsonResponse({'status': 'success'})
        except exceptions.FirebaseError:
            return JsonResponse({'status': 'error', 'message': 'Invalid email or password.'})

    return render(request, 'login.html')

def login_required(func):
    def wrapper(request, *args, **kwargs):
        if 'user_id' not in request.session:
            return redirect('login')
        return func(request, *args, **kwargs)
    return wrapper

@login_required
def hello_view(request):
    return render(request, 'hello.html')

def index_view(request):
    return redirect('login')

def contribute_view(request):
    return render(request, 'contribute.html')

@csrf_exempt
def upload_image(request):
    if request.method == 'POST':
        user_id = request.session.get('user_id')
        face_image = request.FILES.get('face')
        left_eye_image = request.FILES.get('left_eye')
        right_eye_image = request.FILES.get('right_eye')

        face_image_data = None
        left_eye_image_data = None
        right_eye_image_data = None

        if face_image:
            face_image_data = face_image.read()

        if left_eye_image:
            left_eye_image_data = left_eye_image.read()

        if right_eye_image:
            right_eye_image_data = right_eye_image.read()

        UploadedImage.objects.create(
            user_id=user_id,
            face_image=face_image_data,
            left_eye_image=left_eye_image_data,
            right_eye_image=right_eye_image_data
        )

        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'failed'}, status=400)

@login_required
def download_dataset(request):
    with tempfile.TemporaryDirectory() as temp_dir:
        images = UploadedImage.objects.all()
        for idx, image in enumerate(images, start=1):
            subject_dir = os.path.join(temp_dir, f'Subject{idx}')
            os.makedirs(subject_dir, exist_ok=True)

            if image.face_image:
                face_image_path = os.path.join(subject_dir, 'FullFace.jpg')
                with open(face_image_path, 'wb') as f:
                    f.write(image.face_image)
            if image.left_eye_image:
                left_eye_image_path = os.path.join(subject_dir, 'LeftEye.jpg')
                with open(left_eye_image_path, 'wb') as f:
                    f.write(image.left_eye_image)
            if image.right_eye_image:
                right_eye_image_path = os.path.join(subject_dir, 'RightEye.jpg')
                with open(right_eye_image_path, 'wb') as f:
                    f.write(image.right_eye_image)

        zip_path = os.path.join(temp_dir, 'dataset.zip')
        with zipfile.ZipFile(zip_path, 'w') as zipf:
            for root, dirs, files in os.walk(temp_dir):
                for file in files:
                    zipf.write(os.path.join(root, file),
                               os.path.relpath(os.path.join(root, file), temp_dir))

        with open(zip_path, 'rb') as zip_file:
            response = HttpResponse(zip_file.read(), content_type='application/zip')
            response['Content-Disposition'] = 'attachment; filename="dataset.zip"'
            return response

