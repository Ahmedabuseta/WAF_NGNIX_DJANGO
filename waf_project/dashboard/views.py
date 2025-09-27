from django.shortcuts import render, redirect
from django.contrib import messages
from django.db.models import Count, Avg
from waf_proxy.models import User, Site, RequestLog, SiteStats
from core.decorators import login_required_custom, admin_required, customer_required


@login_required_custom
def dashboard(request):
    """Main dashboard - redirects based on user type"""
    if request.user.user_type == 'admin':
        return redirect('admin_panel:admin_dashboard')
    else:
        return redirect('dashboard:customer_dashboard')


@customer_required
def customer_dashboard(request):
    """Customer dashboard with site statistics"""
    user = request.user
    sites = Site.objects.filter(owner=user).order_by('-created_at')
    
    # Get statistics
    total_sites = sites.count()
    
    # Get today's statistics
    from django.utils import timezone
    today = timezone.now().date()
    
    total_requests_today = 0
    blocked_today = 0
    
    for site in sites:
        try:
            stats = SiteStats.objects.get(site=site, date=today)
            total_requests_today += stats.total_requests
            blocked_today += stats.blocked_requests
        except SiteStats.DoesNotExist:
            pass
    
    # Get recent logs
    recent_logs = RequestLog.objects.filter(site__owner=user).order_by('-timestamp')[:10]
    
    context = {
        'user': user,
        'sites': sites,
        'total_sites': total_sites,
        'total_requests_today': total_requests_today,
        'blocked_today': blocked_today,
        'recent_logs': recent_logs,
    }
    
    return render(request, 'dashboard/customer_dashboard.html', context)
