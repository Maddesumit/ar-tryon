"""
Admin configuration for users app.
This file defines how models appear in the Django admin interface.
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import UserProfile

class UserProfileInline(admin.StackedInline):
    """
    Inline admin for UserProfile.
    This allows editing the profile directly from the User admin page.
    """
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Profile'
    fields = ('phone_number', 'date_of_birth', 'avatar', 'height', 'weight', 'gender', 'preferred_size')

class UserAdmin(BaseUserAdmin):
    """
    Extended User admin that includes the UserProfile inline.
    """
    inlines = (UserProfileInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'date_joined')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'date_joined')

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    """
    Admin for UserProfile model.
    """
    list_display = ('user', 'phone_number', 'gender', 'preferred_size', 'created_at')
    list_filter = ('gender', 'preferred_size', 'created_at')
    search_fields = ('user__username', 'user__email', 'phone_number')
    readonly_fields = ('created_at', 'updated_at')

# Unregister the default User admin and register our custom one
admin.site.unregister(User)
admin.site.register(User, UserAdmin)
