from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    # API Documentation
    path('api/docs/', views.api_docs, name='api_docs'),
    
    # Test routes
    path('test/', views.test_protected_site, name='test_protected_site'),
    path('chart-test/', views.chart_test, name='chart_test'),
]
