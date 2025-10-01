from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('google/', views.google_login, name='google_login'),
]
