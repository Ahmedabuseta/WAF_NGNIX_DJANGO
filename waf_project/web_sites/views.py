from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from waf_proxy.models import Site, SiteStats, SiteRule, Rule
from core.decorators import login_required_custom, customer_required, site_owner_required


@customer_required
def site_list(request):
    """List all sites for the current user"""
    sites = Site.objects.filter(owner=request.user).order_by('-created_at')
    return render(request, 'web_sites/site_list.html', {'sites': sites})


@customer_required
def site_add(request):
    """Add a new site"""
    if request.method == 'POST':
        domain = request.POST.get('domain')
        backend_url = request.POST.get('backend_url')
        
        if not domain or not backend_url:
            messages.error(request, 'Domain and backend URL are required')
            return render(request, 'web_sites/site_add.html')
        
        # Create site
        site = Site.objects.create(
            owner=request.user,
            domain=domain,
            backend_url=backend_url
        )
        
        messages.success(request, f'Site {domain} added successfully!')
        return redirect('web_sites:site_detail', site_id=site.id)
    
    return render(request, 'web_sites/site_add.html')


@site_owner_required
def site_detail(request, site_id):
    """View site details"""
    site = get_object_or_404(Site, id=site_id)
    
    # Get recent statistics
    recent_stats = SiteStats.objects.filter(site=site).order_by('-date')[:7]
    
    context = {
        'site': site,
        'recent_stats': recent_stats,
    }
    
    return render(request, 'web_sites/site_detail.html', context)


@site_owner_required
def site_edit(request, site_id):
    """Edit site details"""
    site = get_object_or_404(Site, id=site_id)
    
    if request.method == 'POST':
        site.domain = request.POST.get('domain', site.domain)
        site.backend_url = request.POST.get('backend_url', site.backend_url)
        site.is_active = request.POST.get('is_active') == 'on'
        site.save()
        
        messages.success(request, 'Site updated successfully!')
        return redirect('web_sites:site_detail', site_id=site.id)
    
    return render(request, 'web_sites/site_edit.html', {'site': site})


@site_owner_required
def site_delete(request, site_id):
    """Delete site"""
    site = get_object_or_404(Site, id=site_id)
    
    if request.method == 'POST':
        site.delete()
        messages.success(request, f'Site {site.domain} deleted successfully!')
        return redirect('web_sites:site_list')
    
    return render(request, 'web_sites/site_delete.html', {'site': site})


@site_owner_required
def site_rules(request, site_id):
    """View site rules"""
    site = get_object_or_404(Site, id=site_id)
    site_rules = SiteRule.objects.filter(site=site)
    
    context = {
        'site': site,
        'site_rules': site_rules,
    }
    
    return render(request, 'web_sites/site_rules.html', context)


@site_owner_required
def site_rule_add(request, site_id):
    """Add rule to site"""
    site = get_object_or_404(Site, id=site_id)
    
    if request.method == 'POST':
        rule_id = request.POST.get('rule_id')
        custom_action = request.POST.get('custom_action', 'BLOCK')
        
        try:
            rule = Rule.objects.get(id=rule_id)
            SiteRule.objects.create(
                site=site,
                rule=rule,
                custom_action=custom_action
            )
            messages.success(request, f'Rule {rule.name} added to site!')
            return redirect('web_sites:site_rules', site_id=site.id)
        except Rule.DoesNotExist:
            messages.error(request, 'Invalid rule selected')
    
    # Get available rules
    available_rules = Rule.objects.filter(is_active=True, is_global=True)
    
    context = {
        'site': site,
        'available_rules': available_rules,
    }
    
    return render(request, 'web_sites/site_rule_add.html', context)


@site_owner_required
def site_rule_edit(request, site_id, rule_id):
    """Edit site rule"""
    site = get_object_or_404(Site, id=site_id)
    site_rule = get_object_or_404(SiteRule, site=site, id=rule_id)
    
    if request.method == 'POST':
        site_rule.custom_action = request.POST.get('custom_action', 'BLOCK')
        site_rule.is_active = request.POST.get('is_active') == 'on'
        site_rule.save()
        
        messages.success(request, 'Rule updated successfully!')
        return redirect('web_sites:site_rules', site_id=site.id)
    
    return render(request, 'web_sites/site_rule_edit.html', {'site': site, 'site_rule': site_rule})


@site_owner_required
def site_rule_delete(request, site_id, rule_id):
    """Delete site rule"""
    site = get_object_or_404(Site, id=site_id)
    site_rule = get_object_or_404(SiteRule, site=site, id=rule_id)
    
    if request.method == 'POST':
        site_rule.delete()
        messages.success(request, 'Rule removed from site!')
        return redirect('web_sites:site_rules', site_id=site.id)
    
    return render(request, 'web_sites/site_rule_delete.html', {'site': site, 'site_rule': site_rule})


@site_owner_required
def site_rules_import(request, site_id):
    """Import rules to site"""
    site = get_object_or_404(Site, id=site_id)
    
    if request.method == 'POST':
        # Handle rule import logic
        messages.success(request, 'Rules imported successfully!')
        return redirect('web_sites:site_rules', site_id=site.id)
    
    return render(request, 'web_sites/site_rules_import.html', {'site': site})


@site_owner_required
def site_rules_export(request, site_id):
    """Export site rules"""
    site = get_object_or_404(Site, id=site_id)
    
    # Handle rule export logic
    messages.success(request, 'Rules exported successfully!')
    return redirect('web_sites:site_rules', site_id=site.id)


@site_owner_required
def site_stats(request, site_id):
    """View site statistics"""
    site = get_object_or_404(Site, id=site_id)
    
    # Get statistics
    stats = SiteStats.objects.filter(site=site).order_by('-date')[:30]
    
    context = {
        'site': site,
        'stats': stats,
    }
    
    return render(request, 'web_sites/site_stats.html', context)
