from django.urls import path
from .views import (
    RuleManagementView, SiteRuleListView, SiteRuleCreateView, 
    SiteRuleUpdateView, SiteRuleDeleteView, BulkRuleAssignmentView,
    AvailableRulesView, toggle_rule_status
)

app_name = 'rules'

urlpatterns = [
    path('', RuleManagementView.as_view(), name='rule_management'),
    path('site/', SiteRuleListView.as_view(), name='site_rule_list'),
    path('site/create/', SiteRuleCreateView.as_view(), name='site_rule_create'),
    path('site/<int:pk>/edit/', SiteRuleUpdateView.as_view(), name='site_rule_update'),
    path('site/<int:pk>/delete/', SiteRuleDeleteView.as_view(), name='site_rule_delete'),
    path('bulk-assign/', BulkRuleAssignmentView.as_view(), name='bulk_rule_assignment'),
    path('available/', AvailableRulesView.as_view(), name='available_rules'),
    path('toggle/<int:pk>/', toggle_rule_status, name='toggle_rule_status'),
]