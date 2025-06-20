"""
Forms for users app.
Forms handle user input validation and rendering HTML form elements.
"""

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import UserProfile

class CustomUserCreationForm(UserCreationForm):
    """
    Extended user registration form.
    This extends Django's built-in UserCreationForm to include email.
    """
    email = forms.EmailField(required=True, help_text="Required. Enter a valid email address.")
    first_name = forms.CharField(max_length=30, required=True, help_text="Required.")
    last_name = forms.CharField(max_length=30, required=True, help_text="Required.")
    
    class Meta:
        model = User
        fields = ("username", "first_name", "last_name", "email", "password1", "password2")
    
    def clean_email(self):
        """
        Validate that the email is unique.
        This method is automatically called when the form is validated.
        """
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("A user with this email already exists.")
        return email
    
    def save(self, commit=True):
        """
        Save the user with the additional fields.
        """
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data["last_name"]
        if commit:
            user.save()
        return user

class UserProfileForm(forms.ModelForm):
    """
    Form for editing user profile information.
    ModelForm automatically creates form fields based on the model.
    """
    
    class Meta:
        model = UserProfile
        fields = [
            'phone_number', 'date_of_birth', 'avatar', 
            'height', 'weight', 'gender', 'preferred_size'
        ]
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
            'phone_number': forms.TextInput(attrs={'placeholder': '+1234567890'}),
            'height': forms.NumberInput(attrs={'placeholder': 'Height in cm'}),
            'weight': forms.NumberInput(attrs={'placeholder': 'Weight in kg'}),
        }
        help_texts = {
            'height': 'Enter your height in centimeters',
            'weight': 'Enter your weight in kilograms',
            'avatar': 'Upload a profile picture (optional)',
        }

class UserUpdateForm(forms.ModelForm):
    """
    Form for updating basic user information.
    """
    email = forms.EmailField()
    
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
    
    def clean_email(self):
        """
        Validate that the email is unique (excluding current user).
        """
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("A user with this email already exists.")
        return email
