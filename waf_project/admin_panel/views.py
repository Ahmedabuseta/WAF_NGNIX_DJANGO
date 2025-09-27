from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.paginator import Paginator
from waf_proxy.models import User, Site, Rule, RequestLog, SiteStats
from core.decorators import admin_required


@admin_required
def admin_dashboard(request):
    """Admin dashboard with system overview"""
    # Get system statistics
    total_users = User.objects.count()
    total_sites = Site.objects.count()
    total_rules = Rule.objects.count()
    
    # Get recent activity
    recent_logs = RequestLog.objects.order_by('-timestamp')[:10]
    
    context = {
        'total_users': total_users,
        'total_sites': total_sites,
        'total_rules': total_rules,
        'recent_logs': recent_logs,
    }
    
    return render(request, 'admin_panel/dashboard.html', context)


@admin_required
def customer_list(request):
    """List all customers"""
    customers = User.objects.filter(user_type='customer').order_by('-created_at')
    paginator = Paginator(customers, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'admin_panel/customer_list.html', {'page_obj': page_obj})


@admin_required
def customer_detail(request, customer_id):
    """View customer details"""
    customer = get_object_or_404(User, id=customer_id, user_type='customer')
    sites = Site.objects.filter(owner=customer)
    
    context = {
        'customer': customer,
        'sites': sites,
    }
    
    return render(request, 'admin_panel/customer_detail.html', context)


@admin_required
def admin_site_list(request):
    """List all sites (admin view)"""
    sites = Site.objects.all().order_by('-created_at')
    paginator = Paginator(sites, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'admin_panel/site_list.html', {'page_obj': page_obj})


@admin_required
def rule_list(request):
    """List all rules"""
    rules = Rule.objects.all().order_by('-created_at')
    return render(request, 'admin_panel/rule_list.html', {'rules': rules})


@admin_required
def rule_add(request):
    """Add new rule"""
    if request.method == 'POST':
        name = request.POST.get('name')
        pattern = request.POST.get('pattern')
        rule_type = request.POST.get('rule_type')
        action = request.POST.get('action', 'BLOCK')
        description = request.POST.get('description', '')
        
        if not name or not pattern or not rule_type:
            messages.error(request, 'Name, pattern, and rule type are required')
            return render(request, 'admin_panel/rule_add.html')
        
        Rule.objects.create(
            name=name,
            pattern=pattern,
            rule_type=rule_type,
            action=action,
            description=description
        )
        
        messages.success(request, f'Rule {name} created successfully!')
        return redirect('admin_panel:rule_list')
    
    return render(request, 'admin_panel/rule_add.html')


@admin_required
def rule_edit(request, rule_id):
    """Edit rule"""
    rule = get_object_or_404(Rule, id=rule_id)
    
    if request.method == 'POST':
        rule.name = request.POST.get('name', rule.name)
        rule.pattern = request.POST.get('pattern', rule.pattern)
        rule.rule_type = request.POST.get('rule_type', rule.rule_type)
        rule.action = request.POST.get('action', rule.action)
        rule.description = request.POST.get('description', rule.description)
        rule.is_active = request.POST.get('is_active') == 'on'
        rule.save()
        
        messages.success(request, 'Rule updated successfully!')
        return redirect('admin_panel:rule_list')
    
    return render(request, 'admin_panel/rule_edit.html', {'rule': rule})


@admin_required
def rule_delete(request, rule_id):
    """Delete rule"""
    rule = get_object_or_404(Rule, id=rule_id)
    
    if request.method == 'POST':
        rule.delete()
        messages.success(request, f'Rule {rule.name} deleted successfully!')
        return redirect('admin_panel:rule_list')
    
    return render(request, 'admin_panel/rule_delete.html', {'rule': rule})


@admin_required
def log_list(request):
    """List request logs"""
    logs = RequestLog.objects.order_by('-timestamp')
    paginator = Paginator(logs, 50)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
    }
    
    return render(request, 'admin_panel/log_list.html', context)


@admin_required
def system_status(request):
    """System status page"""
    import psutil
    
    # Get system information
    cpu_percent = psutil.cpu_percent()
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    
    context = {
        'cpu_percent': cpu_percent,
        'memory_percent': memory.percent,
        'disk_percent': disk.percent,
    }
    
    return render(request, 'admin_panel/system_status.html', context)
