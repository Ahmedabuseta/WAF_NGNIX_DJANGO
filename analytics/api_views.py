from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.db.models import Count, Sum, Avg, Q, F
from django.utils import timezone
from datetime import timedelta, datetime
from .models import (
    AnalyticsMetric, SecurityReport, ThreatIntelligence, 
    PerformanceMetric, GeographicData, Alert, AlertRule
)
from logging_app.models import RequestLog
import json


class AnalyticsAPIView(LoginRequiredMixin, TemplateView):
    """API endpoints for analytics data"""
    
    def get(self, request, *args, **kwargs):
        """Handle API requests"""
        endpoint = kwargs.get('endpoint')
        
        if endpoint == 'traffic_timeline':
            return self._get_traffic_timeline(request)
        elif endpoint == 'geographic_data':
            return self._get_geographic_data(request)
        elif endpoint == 'performance_metrics':
            return self._get_performance_metrics_api(request)
        elif endpoint == 'security_summary':
            return self._get_security_summary(request)
        elif endpoint == 'top_ips':
            return self._get_top_ips(request)
        elif endpoint == 'top_rules':
            return self._get_top_rules(request)
        else:
            return JsonResponse({'error': 'Invalid endpoint'}, status=400)
    
    def _get_traffic_timeline(self, request):
        """Get traffic data for timeline charts"""
        tenant = request.tenant
        hours = int(request.GET.get('hours', 24))
        
        now = timezone.now()
        start_time = now - timedelta(hours=hours)
        
        # Group by hour
        logs = RequestLog.objects.filter(
            tenant=tenant,
            request_ts__gte=start_time
        ).extra(
            select={'hour': "date_trunc('hour', request_ts)"}
        ).values('hour').annotate(
            total=Count('id'),
            blocked=Count('id', filter=Q(action='block')),
            allowed=Count('id', filter=Q(action='allow'))
        ).order_by('hour')
        
        data = []
        for log in logs:
            data.append({
                'timestamp': log['hour'].isoformat(),
                'total': log['total'],
                'blocked': log['blocked'],
                'allowed': log['allowed'],
                'block_rate': (log['blocked'] / log['total'] * 100) if log['total'] > 0 else 0
            })
        
        return JsonResponse({'data': data})
    
    def _get_geographic_data(self, request):
        """Get geographic distribution data"""
        tenant = request.tenant
        hours = int(request.GET.get('hours', 24))
        
        now = timezone.now()
        start_time = now - timedelta(hours=hours)
        
        geo_data = GeographicData.objects.filter(
            tenant=tenant,
            timestamp__gte=start_time
        ).values(
            'country_name', 'country_code', 'latitude', 'longitude',
            'request_count', 'blocked_count', 'threat_count'
        ).order_by('-request_count')
        
        return JsonResponse({'data': list(geo_data)})
    
    def _get_performance_metrics_api(self, request):
        """Get performance metrics for charts"""
        tenant = request.tenant
        hours = int(request.GET.get('hours', 24))
        
        now = timezone.now()
        start_time = now - timedelta(hours=hours)
        
        metrics = PerformanceMetric.objects.filter(
            tenant=tenant,
            timestamp__gte=start_time
        ).order_by('timestamp')
        
        data = []
        for metric in metrics:
            data.append({
                'timestamp': metric.timestamp.isoformat(),
                'response_time_avg': metric.response_time_avg,
                'response_time_p95': metric.response_time_p95,
                'response_time_p99': metric.response_time_p99,
                'requests_per_second': metric.requests_per_second,
                'error_rate': metric.error_rate,
                'cpu_usage': metric.cpu_usage,
                'memory_usage': metric.memory_usage,
            })
        
        return JsonResponse({'data': data})
    
    def _get_security_summary(self, request):
        """Get security summary data"""
        tenant = request.tenant
        hours = int(request.GET.get('hours', 24))
        
        now = timezone.now()
        start_time = now - timedelta(hours=hours)
        
        # Security metrics
        logs = RequestLog.objects.filter(tenant=tenant, request_ts__gte=start_time)
        total_requests = logs.count()
        blocked_requests = logs.filter(action='block').count()
        
        # Threat types
        threat_types = ThreatIntelligence.objects.filter(
            tenant=tenant,
            is_active=True
        ).values('threat_type').annotate(count=Count('id'))
        
        # Recent incidents
        recent_incidents = SecurityReport.objects.filter(
            tenant=tenant,
            generated_at__gte=start_time
        ).order_by('-generated_at')[:5]
        
        return JsonResponse({
            'total_requests': total_requests,
            'blocked_requests': blocked_requests,
            'block_rate': (blocked_requests / total_requests * 100) if total_requests > 0 else 0,
            'threat_types': list(threat_types),
            'recent_incidents': list(recent_incidents.values(
                'title', 'severity', 'generated_at'
            ))
        })
    
    def _get_top_ips(self, request):
        """Get top IP addresses by activity"""
        tenant = request.tenant
        hours = int(request.GET.get('hours', 24))
        limit = int(request.GET.get('limit', 20))
        
        now = timezone.now()
        start_time = now - timedelta(hours=hours)
        
        top_ips = RequestLog.objects.filter(
            tenant=tenant,
            request_ts__gte=start_time
        ).values('remote_ip').annotate(
            total_requests=Count('id'),
            blocked_requests=Count('id', filter=Q(action='block')),
            allowed_requests=Count('id', filter=Q(action='allow'))
        ).order_by('-total_requests')[:limit]
        
        return JsonResponse({'data': list(top_ips)})
    
    def _get_top_rules(self, request):
        """Get top triggered rules"""
        tenant = request.tenant
        hours = int(request.GET.get('hours', 24))
        limit = int(request.GET.get('limit', 20))
        
        now = timezone.now()
        start_time = now - timedelta(hours=hours)
        
        top_rules = RequestLog.objects.filter(
            tenant=tenant,
            request_ts__gte=start_time,
            action='block',
            matched_rule__isnull=False
        ).values(
            'matched_rule__name',
            'matched_rule__description'
        ).annotate(
            trigger_count=Count('id')
        ).order_by('-trigger_count')[:limit]
        
        return JsonResponse({'data': list(top_rules)})
