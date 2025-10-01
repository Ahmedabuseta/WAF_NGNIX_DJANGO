from django.urls import path
from .views import WAFDecisionView, WAFStatsView

app_name = 'waf_core'

urlpatterns = [
    path('waf/decision/', WAFDecisionView.as_view(), name='waf_decision'),
    path('waf/stats/', WAFStatsView.as_view(), name='waf_stats'),
]
