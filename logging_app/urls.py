from django.urls import path
from .views import RequestLogListView

app_name = 'logs'

urlpatterns = [
    path('', RequestLogListView.as_view(), name='list'),
]

