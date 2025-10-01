from django.contrib import admin
from .models import (
    AnalyticsMetric, SecurityReport, ThreatIntelligence,
    PerformanceMetric, GeographicData, Alert, AlertRule
)


@admin.register(AnalyticsMetric)
class AnalyticsMetricAdmin(admin.ModelAdmin):
    list_display = ('tenant', 'site', 'metric_type', 'value', 'timestamp')
    list_filter = ('metric_type', 'tenant', 'timestamp')
    search_fields = ('tenant__name', 'site__name')
    readonly_fields = ('timestamp',)
    raw_id_fields = ('tenant', 'site')


@admin.register(SecurityReport)
class SecurityReportAdmin(admin.ModelAdmin):
    list_display = ('tenant', 'site', 'report_type', 'severity', 'title', 'generated_at')
    list_filter = ('report_type', 'severity', 'tenant', 'generated_at')
    search_fields = ('title', 'summary', 'tenant__name')
    readonly_fields = ('generated_at',)
    raw_id_fields = ('tenant', 'site')


@admin.register(ThreatIntelligence)
class ThreatIntelligenceAdmin(admin.ModelAdmin):
    list_display = ('tenant', 'threat_type', 'indicator', 'confidence_score', 'severity', 'is_active', 'last_seen')
    list_filter = ('threat_type', 'severity', 'is_active', 'tenant', 'last_seen')
    search_fields = ('indicator', 'description', 'tenant__name')
    readonly_fields = ('first_seen', 'last_seen')
    raw_id_fields = ('tenant',)


@admin.register(PerformanceMetric)
class PerformanceMetricAdmin(admin.ModelAdmin):
    list_display = ('tenant', 'site', 'response_time_avg', 'requests_per_second', 'error_rate', 'timestamp')
    list_filter = ('tenant', 'timestamp')
    search_fields = ('tenant__name', 'site__name')
    readonly_fields = ('timestamp',)
    raw_id_fields = ('tenant', 'site')


@admin.register(GeographicData)
class GeographicDataAdmin(admin.ModelAdmin):
    list_display = ('tenant', 'site', 'country_name', 'request_count', 'blocked_count', 'threat_count', 'timestamp')
    list_filter = ('country_code', 'tenant', 'timestamp')
    search_fields = ('country_name', 'city', 'tenant__name')
    readonly_fields = ('timestamp',)
    raw_id_fields = ('tenant', 'site')


@admin.register(AlertRule)
class AlertRuleAdmin(admin.ModelAdmin):
    list_display = ('tenant', 'name', 'alert_type', 'threshold', 'is_active', 'created_at')
    list_filter = ('alert_type', 'is_active', 'tenant', 'created_at')
    search_fields = ('name', 'tenant__name')
    readonly_fields = ('created_at', 'updated_at')
    raw_id_fields = ('tenant',)


@admin.register(Alert)
class AlertAdmin(admin.ModelAdmin):
    list_display = ('tenant', 'site', 'title', 'severity', 'status', 'triggered_at')
    list_filter = ('severity', 'status', 'tenant', 'triggered_at')
    search_fields = ('title', 'message', 'tenant__name')
    readonly_fields = ('triggered_at', 'acknowledged_at', 'resolved_at')
    raw_id_fields = ('tenant', 'site', 'rule')