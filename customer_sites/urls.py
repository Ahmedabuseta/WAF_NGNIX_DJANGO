from django.urls import path
from .views import (
    SiteListView, SiteDetailView, SiteCreateView, SiteUpdateView, SiteDeleteView
)

app_name = 'sites'

urlpatterns = [
    path('', SiteListView.as_view(), name='list'),
    path('create/', SiteCreateView.as_view(), name='create'),
    path('<int:pk>/', SiteDetailView.as_view(), name='detail'),
    path('<int:pk>/edit/', SiteUpdateView.as_view(), name='edit'),
    path('<int:pk>/delete/', SiteDeleteView.as_view(), name='delete'),
]

