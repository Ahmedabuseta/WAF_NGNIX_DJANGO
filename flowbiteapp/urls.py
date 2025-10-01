"""
URL configuration for flowbiteapp project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from .views import index, accordion, carousel, collapse, dial, dismiss, modal, drawer, dropdown, popover, tabs, tooltip, input_counter, datepicker, health

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')),
    path('accounts/', include('accounts.urls')),
    path('waf/', include('waf_core.urls', namespace='waf')),
    path('analytics/', include('analytics.urls', namespace='analytics')),
    path('dashboard/', include('dashboard.urls', namespace='dashboard')),
    path('sites/', include('customer_sites.urls', namespace='sites')),
    path('rules/', include('rules.urls', namespace='rules')),
    path('logs/', include('logging_app.urls', namespace='logs')),
    path('health/', health, name='health'),
    path('', index, name='index'),
    path('accordion', accordion, name='accordion'),
    path('carousel', carousel, name='carousel'),
    path('collapse', collapse, name='collapse'),    
    path('dial', dial, name='dial'),
    path('dismiss', dismiss, name='dismiss'),
    path('modal', modal, name='modal'),
    path('drawer', drawer, name='drawer'),
    path('dropdown', dropdown, name='dropdown'),
    path('popover', popover, name='popover'),
    path('tabs', tabs, name='tabs'),
    path('tooltip', tooltip, name='tooltip'),
    path('input-counter', input_counter, name='input-counter'),
    path('datepicker', datepicker, name='datepicker'),
]