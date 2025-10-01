from django.urls import path
from .views import (
    AnalyticsDashboardView, SecurityReportsView, 
    ThreatIntelligenceView, AlertsView
)
from .api_views import AnalyticsAPIView

app_name = 'analytics'

urlpatterns = [
    path('', AnalyticsDashboardView.as_view(), name='dashboard'),
    path('reports/', SecurityReportsView.as_view(), name='security_reports'),
    path('threats/', ThreatIntelligenceView.as_view(), name='threat_intelligence'),
    path('alerts/', AlertsView.as_view(), name='alerts'),
    path('api/<str:endpoint>/', AnalyticsAPIView.as_view(), name='api'),
]
