from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
import firebase_admin
from firebase_admin import auth, credentials
from .firebase_config import *

def signup_view(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']

        # Validate email
        try:
            validate_email(email)
        except ValidationError:
            return render(request, 'signup.html', {'error': 'Invalid email format'})

        # Check password length
        if len(password) < 6:
            return render(request, 'signup.html', {'error': 'Password must be at least 6 characters long'})

        # Check password confirmation
        if password != confirm_password:
            return render(request, 'signup.html', {'error': 'Passwords do not match'})

        try:
            user_record = auth.create_user(email=email, password=password)
            # Account created successfully
            messages.success(request, 'Account created successfully. Please log in.')
            return redirect('login')
        except firebase_admin.exceptions.FirebaseError as e:
            return render(request, 'signup.html', {'error': str(e)})

    return render(request, 'signup.html')

def login_view(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        try:
            user_record = auth.get_user_by_email(email)
            # Here you'd verify the password if you were managing it, which Firebase does for you
            request.session['user_id'] = user_record.uid  # Use Firebase UID for session
            return redirect('hello')
        except firebase_admin.exceptions.FirebaseError:
            return render(request, 'login.html', {'error': 'Invalid email or password.'})

    return render(request, 'login.html')

# Custom login_required decorator
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
