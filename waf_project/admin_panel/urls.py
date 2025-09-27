from django.urls import path
from . import views

app_name = 'admin_panel'

urlpatterns = [
    # Admin dashboard
    path('dashboard/', views.admin_dashboard, name='admin_dashboard'),
    
    # Customer management
    path('customers/', views.customer_list, name='customer_list'),
    path('customers/<int:customer_id>/', views.customer_detail, name='customer_detail'),
    
    # Site management
    path('sites/', views.admin_site_list, name='admin_site_list'),
    
    # Rule management
    path('rules/', views.rule_list, name='rule_list'),
    path('rules/add/', views.rule_add, name='rule_add'),
    path('rules/<int:rule_id>/edit/', views.rule_edit, name='rule_edit'),
    path('rules/<int:rule_id>/delete/', views.rule_delete, name='rule_delete'),
    
    # System management
    path('logs/', views.log_list, name='log_list'),
    path('system/', views.system_status, name='system_status'),
]
