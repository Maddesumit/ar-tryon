"""
Models for users app.
Models define the structure of our database tables.
"""

from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from PIL import Image

class UserProfile(models.Model):
    """
    Extended user profile model.
    This model extends Django's built-in User model with additional fields.
    OneToOneField creates a one-to-one relationship - each User has exactly one UserProfile.
    """
    
    # Link to Django's built-in User model
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    
    # Profile information
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    
    # Profile picture
    avatar = models.ImageField(
        upload_to='avatars/',  # Images will be saved in media/avatars/
        default='avatars/default.png',  # Default avatar if none uploaded
        blank=True
    )
    
    # Physical measurements for better try-on experience
    height = models.IntegerField(help_text="Height in centimeters", blank=True, null=True)
    weight = models.IntegerField(help_text="Weight in kilograms", blank=True, null=True)
    
    # Clothing preferences
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
        ('P', 'Prefer not to say'),
    ]
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True)
    
    SIZE_CHOICES = [
        ('XS', 'Extra Small'),
        ('S', 'Small'),
        ('M', 'Medium'),
        ('L', 'Large'),
        ('XL', 'Extra Large'),
        ('XXL', 'Double Extra Large'),
    ]
    preferred_size = models.CharField(max_length=3, choices=SIZE_CHOICES, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        """
        String representation of the model.
        This is what shows up when we print a UserProfile object.
        """
        return f"{self.user.username}'s Profile"
    
    def save(self, *args, **kwargs):
        """
        Override the save method to resize large images.
        This prevents huge image files from taking up too much space.
        """
        super().save(*args, **kwargs)
        
        if self.avatar:
            try:
                img = Image.open(self.avatar.path)
                if img.height > 300 or img.width > 300:
                    output_size = (300, 300)
                    img.thumbnail(output_size)
                    img.save(self.avatar.path)
            except Exception as e:
                # If image processing fails, just continue
                pass

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """
    Signal handler to automatically create a UserProfile when a User is created.
    This ensures every user automatically gets a profile.
    """
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """
    Signal handler to save the UserProfile when the User is saved.
    """
    try:
        instance.profile.save()
    except UserProfile.DoesNotExist:
        # If profile doesn't exist, create it
        UserProfile.objects.create(user=instance)
