"""
Views for tryon app.
This app handles virtual try-on functionality.
"""

from django.shortcuts import render
from django.http import JsonResponse

def tryon_home(request):
    """
    A simple view that returns a JSON response.
    This is our 'Hello World' view for the tryon app.
    """
    return JsonResponse({
        'message': 'Hello from Try-On app!',
        'app': 'tryon',
        'description': 'This app handles virtual try-on functionality'
    })

# Placeholder views for later phases
def upload_image(request):
    """Image upload view - to be implemented in Phase 5"""
    return JsonResponse({'message': 'Image upload - coming in Phase 5!'})

def tryon_results(request):
    """Try-on results view - to be implemented in Phase 6"""
    return JsonResponse({'message': 'Try-on results - coming in Phase 6!'})
