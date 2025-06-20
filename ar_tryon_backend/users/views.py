"""
Views for users app.
Views are Python functions that take a web request and return a web response.
"""

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from .forms import CustomUserCreationForm, UserProfileForm, UserUpdateForm
from .models import UserProfile
import json

def user_home(request):
    """
    A simple view that returns a JSON response.
    This is our 'Hello World' view for the users app.
    """
    return JsonResponse({
        'message': 'Hello from Users app!',
        'app': 'users',
        'description': 'This app handles user authentication and profiles',
        'authenticated': request.user.is_authenticated,
        'user': request.user.username if request.user.is_authenticated else None
    })

def register_view(request):
    """
    User registration view.
    Handles both GET (show form) and POST (process form) requests.
    """
    if request.user.is_authenticated:
        # If user is already logged in, redirect to profile
        return redirect('users:profile')
    
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            # Save the new user
            user = form.save()
            
            # Log the user in automatically after registration
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=password)
            login(request, user)
            
            messages.success(request, f'Account created successfully! Welcome, {username}!')
            return redirect('users:profile')
        else:
            # Form has errors, they will be displayed in the template
            messages.error(request, 'Please correct the errors below.')
    else:
        # GET request - show empty form
        form = CustomUserCreationForm()
    
    return render(request, 'users/register.html', {'form': form})

def login_view(request):
    """
    User login view.
    """
    if request.user.is_authenticated:
        return redirect('users:profile')
    
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        
        # Authenticate user
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            # Login successful
            login(request, user)
            messages.success(request, f'Welcome back, {user.first_name or username}!')
            
            # Redirect to the page they were trying to access, or profile
            next_page = request.GET.get('next', 'users:profile')
            return redirect(next_page)
        else:
            # Login failed
            messages.error(request, 'Invalid username or password.')
    
    return render(request, 'users/login.html')

def logout_view(request):
    """
    User logout view.
    """
    if request.user.is_authenticated:
        username = request.user.username
        logout(request)
        messages.success(request, f'You have been logged out successfully. Goodbye, {username}!')
    
    return redirect('users:login')

@login_required
def profile_view(request):
    """
    User profile view and edit form.
    Only accessible to logged-in users (@login_required decorator).
    """
    user = request.user
    
    # Get or create user profile (should exist due to signals, but just in case)
    profile, created = UserProfile.objects.get_or_create(user=user)
    
    if request.method == 'POST':
        # Process form submission
        user_form = UserUpdateForm(request.POST, instance=user)
        profile_form = UserProfileForm(request.POST, request.FILES, instance=profile)
        
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Your profile has been updated successfully!')
            return redirect('users:profile')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        # GET request - show forms with current data
        user_form = UserUpdateForm(instance=user)
        profile_form = UserProfileForm(instance=profile)
    
    context = {
        'user_form': user_form,
        'profile_form': profile_form,
        'user': user,
    }
    
    return render(request, 'users/profile.html', context)
