"""
URL configuration for waf_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
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

urlpatterns = [
    # Root dashboard
    path('', include('dashboard.urls')),
    
    # Authentication and user management
    path('auth/', include('accounts.urls')),
    
    # Site management
    path('sites/', include('web_sites.urls')),
    
    # Security pages
    path('security/', include('security.urls')),
    
    # Admin panel
    path('admin/', include('admin_panel.urls')),
    
    # Core utilities
    path('', include('core.urls')),
    
    # OAuth URLs (django-allauth)
    path('accounts/', include('allauth.urls')),
    
    # Django built-in admin (MUST come after custom admin routes)
    path('django-admin/', admin.site.urls),
]

# Serve static files during development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
