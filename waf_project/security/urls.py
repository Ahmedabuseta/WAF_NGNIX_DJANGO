from django.urls import path
from . import views

app_name = 'security'

urlpatterns = [
    # Security pages
    path('blocked/', views.blocked_request, name='blocked_request'),
    path('access-denied/', views.access_denied, name='access_denied'),
    path('rate-limited/', views.rate_limited, name='rate_limited'),
]
