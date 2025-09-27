from django.urls import path
from . import views

app_name = 'web_sites'

urlpatterns = [
    # Site management
    path('', views.site_list, name='site_list'),
    path('add/', views.site_add, name='site_add'),
    path('<int:site_id>/', views.site_detail, name='site_detail'),
    path('<int:site_id>/edit/', views.site_edit, name='site_edit'),
    path('<int:site_id>/delete/', views.site_delete, name='site_delete'),
    
    # Site rules
    path('<int:site_id>/rules/', views.site_rules, name='site_rules'),
    path('<int:site_id>/rules/add/', views.site_rule_add, name='site_rule_add'),
    path('<int:site_id>/rules/<int:rule_id>/edit/', views.site_rule_edit, name='site_rule_edit'),
    path('<int:site_id>/rules/<int:rule_id>/delete/', views.site_rule_delete, name='site_rule_delete'),
    path('<int:site_id>/rules/import/', views.site_rules_import, name='site_rules_import'),
    path('<int:site_id>/rules/export/', views.site_rules_export, name='site_rules_export'),
    
    # Site statistics
    path('<int:site_id>/stats/', views.site_stats, name='site_stats'),
]
