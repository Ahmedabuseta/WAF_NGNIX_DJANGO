from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from core.mixins import TenantScopedQuerysetMixin, TenantFormValidMixin
from .models import Site


class SiteListView(TenantScopedQuerysetMixin, ListView):
    model = Site
    template_name = 'sites/site_list.html'
    context_object_name = 'sites'


class SiteDetailView(TenantScopedQuerysetMixin, DetailView):
    model = Site
    template_name = 'sites/site_detail.html'
    context_object_name = 'site'


class SiteCreateView(TenantFormValidMixin, CreateView):
    model = Site
    fields = ['name', 'domain', 'ip', 'port', 'is_active']
    template_name = 'sites/site_form.html'
    success_url = reverse_lazy('sites:list')


class SiteUpdateView(TenantScopedQuerysetMixin, UpdateView):
    model = Site
    fields = ['name', 'domain', 'ip', 'port', 'is_active']
    template_name = 'sites/site_form.html'
    success_url = reverse_lazy('sites:list')


class SiteDeleteView(TenantScopedQuerysetMixin, DeleteView):
    model = Site
    template_name = 'sites/site_confirm_delete.html'
    success_url = reverse_lazy('sites:list')

# Create your views here.
