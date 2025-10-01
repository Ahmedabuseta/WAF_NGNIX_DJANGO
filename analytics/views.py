from django.views.generic import TemplateView, ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.db.models import Count, Sum, Avg, Q, F
from django.utils import timezone
from datetime import timedelta, datetime
from core.mixins import TenantScopedQuerysetMixin
from .models import (
    AnalyticsMetric, SecurityReport, ThreatIntelligence, 
    PerformanceMetric, GeographicData, Alert, AlertRule
)
from logging_app.models import RequestLog
import json


class AnalyticsDashboardView(LoginRequiredMixin, TemplateView):
    """Main analytics dashboard"""
    template_name = 'analytics/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        tenant = self.request.tenant
        
        if tenant:
            # Time ranges
            now = timezone.now()
            last_24h = now - timedelta(hours=24)
            last_7d = now - timedelta(days=7)
            last_30d = now - timedelta(days=30)
            
            # Basic metrics
            context.update(self._get_basic_metrics(tenant, last_24h, last_7d, last_30d))
            
            # Security metrics
            context.update(self._get_security_metrics(tenant, last_24h, last_7d))
            
            # Performance metrics
            context.update(self._get_performance_metrics(tenant, last_24h))
            
            # Geographic data
            context.update(self._get_geographic_metrics(tenant, last_24h))
            
            # Recent alerts
            context['recent_alerts'] = Alert.objects.filter(
                tenant=tenant
            ).order_by('-triggered_at')[:5]
        
        return context
    
    def _get_basic_metrics(self, tenant, last_24h, last_7d, last_30d):
        """Get basic traffic metrics"""
        # 24h metrics
        logs_24h = RequestLog.objects.filter(tenant=tenant, request_ts__gte=last_24h)
        total_24h = logs_24h.count()
        blocked_24h = logs_24h.filter(action='block').count()
        allowed_24h = logs_24h.filter(action='allow').count()
        
        # 7d metrics
        logs_7d = RequestLog.objects.filter(tenant=tenant, request_ts__gte=last_7d)
        total_7d = logs_7d.count()
        blocked_7d = logs_7d.filter(action='block').count()
        
        # 30d metrics
        logs_30d = RequestLog.objects.filter(tenant=tenant, request_ts__gte=last_30d)
        total_30d = logs_30d.count()
        
        return {
            'total_requests_24h': total_24h,
            'blocked_requests_24h': blocked_24h,
            'allowed_requests_24h': allowed_24h,
            'block_rate_24h': (blocked_24h / total_24h * 100) if total_24h > 0 else 0,
            'total_requests_7d': total_7d,
            'blocked_requests_7d': blocked_7d,
            'block_rate_7d': (blocked_7d / total_7d * 100) if total_7d > 0 else 0,
            'total_requests_30d': total_30d,
        }
    
    def _get_security_metrics(self, tenant, last_24h, last_7d):
        """Get security-related metrics"""
        # Top blocked IPs (24h)
        top_blocked_ips = RequestLog.objects.filter(
            tenant=tenant,
            request_ts__gte=last_24h,
            action='block'
        ).values('remote_ip').annotate(
            count=Count('remote_ip')
        ).order_by('-count')[:10]
        
        # Top triggered rules (24h)
        top_rules = RequestLog.objects.filter(
            tenant=tenant,
            request_ts__gte=last_24h,
            action='block',
            matched_rule__isnull=False
        ).values('matched_rule__name').annotate(
            count=Count('matched_rule__name')
        ).order_by('-count')[:10]
        
        # Threat intelligence
        active_threats = ThreatIntelligence.objects.filter(
            tenant=tenant,
            is_active=True
        ).count()
        
        return {
            'top_blocked_ips': list(top_blocked_ips),
            'top_rules': list(top_rules),
            'active_threats': active_threats,
        }
    
    def _get_performance_metrics(self, tenant, last_24h):
        """Get performance metrics"""
        # Get latest performance data
        latest_perf = PerformanceMetric.objects.filter(
            tenant=tenant,
            timestamp__gte=last_24h
        ).order_by('-timestamp').first()
        
        if latest_perf:
            return {
                'avg_response_time': latest_perf.response_time_avg,
                'p95_response_time': latest_perf.response_time_p95,
                'p99_response_time': latest_perf.response_time_p99,
                'requests_per_second': latest_perf.requests_per_second,
                'error_rate': latest_perf.error_rate,
                'cpu_usage': latest_perf.cpu_usage,
                'memory_usage': latest_perf.memory_usage,
            }
        
        return {
            'avg_response_time': 0,
            'p95_response_time': 0,
            'p99_response_time': 0,
            'requests_per_second': 0,
            'error_rate': 0,
            'cpu_usage': 0,
            'memory_usage': 0,
        }
    
    def _get_geographic_metrics(self, tenant, last_24h):
        """Get geographic distribution metrics"""
        # Top countries by request count
        top_countries = GeographicData.objects.filter(
            tenant=tenant,
            timestamp__gte=last_24h
        ).order_by('-request_count')[:10]
        
        return {
            'top_countries': list(top_countries.values(
                'country_name', 'country_code', 'request_count', 
                'blocked_count', 'allowed_count'
            )),
        }


class SecurityReportsView(TenantScopedQuerysetMixin, LoginRequiredMixin, ListView):
    """Security reports list view"""
    model = SecurityReport
    template_name = 'analytics/security_reports.html'
    context_object_name = 'reports'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = super().get_queryset()
        report_type = self.request.GET.get('type')
        severity = self.request.GET.get('severity')
        
        if report_type:
            queryset = queryset.filter(report_type=report_type)
        if severity:
            queryset = queryset.filter(severity=severity)
        
        return queryset.order_by('-generated_at')


class ThreatIntelligenceView(TenantScopedQuerysetMixin, LoginRequiredMixin, ListView):
    """Threat intelligence list view"""
    model = ThreatIntelligence
    template_name = 'analytics/threat_intelligence.html'
    context_object_name = 'threats'
    paginate_by = 50
    
    def get_queryset(self):
        queryset = super().get_queryset()
        threat_type = self.request.GET.get('type')
        severity = self.request.GET.get('severity')
        is_active = self.request.GET.get('active')
        
        if threat_type:
            queryset = queryset.filter(threat_type=threat_type)
        if severity:
            queryset = queryset.filter(severity=severity)
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        
        return queryset.order_by('-last_seen')


class AlertsView(TenantScopedQuerysetMixin, LoginRequiredMixin, ListView):
    """Alerts and notifications view"""
    model = Alert
    template_name = 'analytics/alerts.html'
    context_object_name = 'alerts'
    paginate_by = 25
    
    def get_queryset(self):
        queryset = super().get_queryset()
        status = self.request.GET.get('status')
        severity = self.request.GET.get('severity')
        
        if status:
            queryset = queryset.filter(status=status)
        if severity:
            queryset = queryset.filter(severity=severity)
        
        return queryset.order_by('-triggered_at')