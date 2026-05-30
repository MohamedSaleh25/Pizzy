"""
URL configuration for project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
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
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from accounts.models import CustomUser

@csrf_exempt
@require_http_methods(["POST", "GET"])
def create_superuser(request):
    """Create a superuser - only works once"""
    if CustomUser.objects.filter(is_superuser=True).exists():
        return JsonResponse({'error': 'Superuser already exists'}, status=400)
    
    try:
        CustomUser.objects.create_superuser(
            email='admin@example.com',
            password='admin123'
        )
        return JsonResponse({'success': 'Superuser created! Email: admin@example.com, Password: admin123'})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('create-superuser/', create_superuser, name='create_superuser'),
    path('', include('pages.urls')),
    path('products/', include('products.urls')),
    path('accounts/', include('accounts.urls')),
    path('profiles/', include('profiles.urls')),
    path('orders/', include('orders.urls')),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

