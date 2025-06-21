"""
URL configuration for ar_tryon_backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import JsonResponse

def api_home(request):
    """Simple API home view"""
    return JsonResponse({
        'message': 'Welcome to AR Try-On API!',
        'version': '1.0',
        'endpoints': {
            'admin': '/admin/',
            'users': '/api/users/',
            'catalog': '/api/catalog/',
            'tryon': '/api/tryon/',
        }
    })

urlpatterns = [
    path("admin/", admin.site.urls),
    path("dashboard/", include("dashboard.urls")),  # Custom admin dashboard
    path("api/", api_home, name="api_home"),  # API home page
    path("api/users/", include("users.urls")),  # User authentication & profiles
    path("api/catalog/", include("catalog.api_urls", namespace="api_catalog")),  # Product catalog API
    path("api/tryon/", include("tryon.urls")),  # Try-on functionality
    path("", include("catalog.urls", namespace="frontend_catalog")),  # Frontend catalog views
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
