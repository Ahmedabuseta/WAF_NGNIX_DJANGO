from django.views.generic import ListView, UpdateView, CreateView, DeleteView, TemplateView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.shortcuts import redirect, get_object_or_404
from django.db import transaction
from django.http import JsonResponse
from core.mixins import TenantScopedQuerysetMixin, TenantFormValidMixin
from .models import Rule, SiteRule
from .forms import SiteRuleForm, BulkRuleAssignmentForm, RuleSearchForm
from customer_sites.models import Site


class RuleManagementView(LoginRequiredMixin, TemplateView):
    """Main rule management dashboard"""
    template_name = 'rules/rule_management.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        tenant = self.request.tenant
        
        # Get available rules
        available_rules = Rule.objects.filter(is_global=True)
        
        # Get sites with their rule assignments
        sites = Site.objects.filter(tenant=tenant, is_active=True)
        sites_with_rules = []
        
        for site in sites:
            site_rules = SiteRule.objects.filter(site=site, tenant=tenant).select_related('rule')
            sites_with_rules.append({
                'site': site,
                'rules': site_rules,
                'rule_count': site_rules.count(),
                'enabled_count': site_rules.filter(enabled=True).count()
            })
        
        context.update({
            'available_rules': available_rules,
            'sites_with_rules': sites_with_rules,
            'total_rules': available_rules.count(),
            'total_sites': sites.count(),
        })
        
        return context


class SiteRuleListView(TenantScopedQuerysetMixin, LoginRequiredMixin, ListView):
    """List all site rules for the current tenant"""
    model = SiteRule
    template_name = 'rules/site_rule_list.html'
    context_object_name = 'site_rules'
    paginate_by = 20

    def get_queryset(self):
        queryset = super().get_queryset()
        site_id = self.request.GET.get('site')
        if site_id:
            queryset = queryset.filter(site__id=site_id)
        return queryset.select_related('site', 'rule').order_by('site__name', 'priority')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['sites'] = Site.objects.filter(tenant=self.request.tenant, is_active=True)
        context['selected_site'] = self.request.GET.get('site')
        return context


class SiteRuleCreateView(TenantFormValidMixin, LoginRequiredMixin, CreateView):
    """Create a new site rule"""
    model = SiteRule
    form_class = SiteRuleForm
    template_name = 'rules/site_rule_form.html'
    success_url = reverse_lazy('rules:site_rule_list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['tenant'] = self.request.tenant
        return kwargs

    def form_valid(self, form):
        messages.success(self.request, 'Rule successfully assigned to site.')
        return super().form_valid(form)


class SiteRuleUpdateView(TenantScopedQuerysetMixin, TenantFormValidMixin, LoginRequiredMixin, UpdateView):
    """Update an existing site rule"""
    model = SiteRule
    form_class = SiteRuleForm
    template_name = 'rules/site_rule_form.html'
    context_object_name = 'site_rule'
    success_url = reverse_lazy('rules:site_rule_list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['tenant'] = self.request.tenant
        return kwargs

    def form_valid(self, form):
        messages.success(self.request, 'Rule configuration updated successfully.')
        return super().form_valid(form)


class SiteRuleDeleteView(TenantScopedQuerysetMixin, LoginRequiredMixin, DeleteView):
    """Delete a site rule"""
    model = SiteRule
    template_name = 'rules/site_rule_confirm_delete.html'
    success_url = reverse_lazy('rules:site_rule_list')

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Rule removed from site successfully.')
        return super().delete(request, *args, **kwargs)


class BulkRuleAssignmentView(LoginRequiredMixin, TemplateView):
    """Bulk assign rules to multiple sites"""
    template_name = 'rules/bulk_rule_assignment.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = BulkRuleAssignmentForm(tenant=self.request.tenant)
        return context
    
    def post(self, request, *args, **kwargs):
        form = BulkRuleAssignmentForm(request.POST, tenant=request.tenant)
        
        if form.is_valid():
            sites = form.cleaned_data['sites']
            rules = form.cleaned_data['rules']
            enabled = form.cleaned_data['enabled']
            priority = form.cleaned_data['priority']
            
            created_count = 0
            updated_count = 0
            
            with transaction.atomic():
                for site in sites:
                    for rule in rules:
                        site_rule, created = SiteRule.objects.get_or_create(
                            site=site,
                            rule=rule,
                            tenant=request.tenant,
                            defaults={
                                'enabled': enabled,
                                'priority': priority
                            }
                        )
                        
                        if not created:
                            site_rule.enabled = enabled
                            site_rule.priority = priority
                            site_rule.save()
                            updated_count += 1
                        else:
                            created_count += 1
            
            messages.success(
                request, 
                f'Successfully assigned {created_count} rules and updated {updated_count} existing assignments.'
            )
            return redirect('rules:rule_management')
        
        context = self.get_context_data()
        context['form'] = form
        return self.render_to_response(context)


class AvailableRulesView(LoginRequiredMixin, ListView):
    """View available rules that can be assigned"""
    model = Rule
    template_name = 'rules/available_rules.html'
    context_object_name = 'rules'
    paginate_by = 20

    def get_queryset(self):
        queryset = Rule.objects.filter(is_global=True)
        
        # Apply search filters
        search_form = RuleSearchForm(self.request.GET)
        if search_form.is_valid():
            search = search_form.cleaned_data.get('search')
            category = search_form.cleaned_data.get('category')
            severity = search_form.cleaned_data.get('severity')
            
            if search:
                queryset = queryset.filter(name__icontains=search)
            
            # Note: We don't have category/severity fields in Rule model yet
            # This would be added in a real implementation
        
        return queryset.order_by('name')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_form'] = RuleSearchForm(self.request.GET)
        return context


def toggle_rule_status(request, pk):
    """Toggle rule enabled/disabled status via AJAX"""
    if request.method == 'POST':
        try:
            site_rule = get_object_or_404(
                SiteRule, 
                pk=pk, 
                tenant=request.tenant
            )
            site_rule.enabled = not site_rule.enabled
            site_rule.save()
            
            return JsonResponse({
                'success': True,
                'enabled': site_rule.enabled,
                'message': f'Rule {"enabled" if site_rule.enabled else "disabled"} successfully.'
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Error updating rule: {str(e)}'
            })
    
    return JsonResponse({'success': False, 'message': 'Invalid request method'})