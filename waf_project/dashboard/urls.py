from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    # Dashboard views
    path('', views.dashboard, name='dashboard'),
    path('customer/', views.customer_dashboard, name='customer_dashboard'),
]
