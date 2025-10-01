from django.db import models
from django.utils import timezone
from datetime import timedelta


class AnalyticsMetric(models.Model):
    """Base analytics metric model"""
    METRIC_TYPES = [
        ('requests_total', 'Total Requests'),
        ('requests_blocked', 'Blocked Requests'),
        ('requests_allowed', 'Allowed Requests'),
        ('response_time_avg', 'Average Response Time'),
        ('bandwidth_used', 'Bandwidth Used'),
        ('unique_visitors', 'Unique Visitors'),
        ('top_ips', 'Top IP Addresses'),
        ('top_rules', 'Top Triggered Rules'),
        ('geographic_data', 'Geographic Data'),
        ('hourly_stats', 'Hourly Statistics'),
    ]
    
    tenant = models.ForeignKey('tenants.Tenant', on_delete=models.CASCADE, related_name='analytics_metrics')
    site = models.ForeignKey('customer_sites.Site', on_delete=models.CASCADE, null=True, blank=True, related_name='analytics_metrics')
    metric_type = models.CharField(max_length=50, choices=METRIC_TYPES)
    value = models.FloatField()
    metadata = models.JSONField(default=dict, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['tenant', 'metric_type', 'timestamp']),
            models.Index(fields=['site', 'metric_type', 'timestamp']),
        ]
    
    def __str__(self):
        return f"{self.tenant.name} - {self.get_metric_type_display()} - {self.value}"


class SecurityReport(models.Model):
    """Security incident reports and summaries"""
    REPORT_TYPES = [
        ('daily', 'Daily Security Report'),
        ('weekly', 'Weekly Security Report'),
        ('monthly', 'Monthly Security Report'),
        ('incident', 'Security Incident Report'),
        ('threat_intel', 'Threat Intelligence Report'),
    ]
    
    SEVERITY_LEVELS = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]
    
    tenant = models.ForeignKey('tenants.Tenant', on_delete=models.CASCADE, related_name='security_reports')
    site = models.ForeignKey('customer_sites.Site', on_delete=models.CASCADE, null=True, blank=True, related_name='security_reports')
    report_type = models.CharField(max_length=20, choices=REPORT_TYPES)
    severity = models.CharField(max_length=10, choices=SEVERITY_LEVELS, default='medium')
    title = models.CharField(max_length=200)
    summary = models.TextField()
    details = models.JSONField(default=dict, blank=True)
    generated_at = models.DateTimeField(auto_now_add=True)
    period_start = models.DateTimeField()
    period_end = models.DateTimeField()
    
    class Meta:
        ordering = ['-generated_at']
    
    def __str__(self):
        return f"{self.tenant.name} - {self.title}"


class ThreatIntelligence(models.Model):
    """Threat intelligence data and indicators"""
    THREAT_TYPES = [
        ('ip_reputation', 'IP Reputation'),
        ('malware_signature', 'Malware Signature'),
        ('attack_pattern', 'Attack Pattern'),
        ('geo_threat', 'Geographic Threat'),
        ('user_agent_anomaly', 'User Agent Anomaly'),
    ]
    
    tenant = models.ForeignKey('tenants.Tenant', on_delete=models.CASCADE, related_name='threat_intelligence')
    threat_type = models.CharField(max_length=30, choices=THREAT_TYPES)
    indicator = models.CharField(max_length=500)  # IP, hash, pattern, etc.
    confidence_score = models.FloatField(default=0.0)  # 0.0 to 1.0
    severity = models.CharField(max_length=10, choices=SecurityReport.SEVERITY_LEVELS)
    description = models.TextField(blank=True)
    source = models.CharField(max_length=100, default='internal')
    first_seen = models.DateTimeField(auto_now_add=True)
    last_seen = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    metadata = models.JSONField(default=dict, blank=True)
    
    class Meta:
        ordering = ['-last_seen']
        unique_together = ['tenant', 'threat_type', 'indicator']
    
    def __str__(self):
        return f"{self.get_threat_type_display()} - {self.indicator}"


class PerformanceMetric(models.Model):
    """Performance and system metrics"""
    tenant = models.ForeignKey('tenants.Tenant', on_delete=models.CASCADE, related_name='performance_metrics')
    site = models.ForeignKey('customer_sites.Site', on_delete=models.CASCADE, null=True, blank=True, related_name='performance_metrics')
    
    # Performance metrics
    response_time_avg = models.FloatField(help_text="Average response time in milliseconds")
    response_time_p95 = models.FloatField(help_text="95th percentile response time in milliseconds")
    response_time_p99 = models.FloatField(help_text="99th percentile response time in milliseconds")
    requests_per_second = models.FloatField(help_text="Requests per second")
    error_rate = models.FloatField(help_text="Error rate percentage")
    
    # System metrics
    cpu_usage = models.FloatField(help_text="CPU usage percentage")
    memory_usage = models.FloatField(help_text="Memory usage percentage")
    disk_usage = models.FloatField(help_text="Disk usage percentage")
    
    # Network metrics
    bandwidth_in = models.BigIntegerField(help_text="Inbound bandwidth in bytes")
    bandwidth_out = models.BigIntegerField(help_text="Outbound bandwidth in bytes")
    
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['tenant', 'timestamp']),
            models.Index(fields=['site', 'timestamp']),
        ]
    
    def __str__(self):
        return f"{self.tenant.name} - Performance - {self.timestamp}"


class GeographicData(models.Model):
    """Geographic distribution of traffic and threats"""
    tenant = models.ForeignKey('tenants.Tenant', on_delete=models.CASCADE, related_name='geographic_data')
    site = models.ForeignKey('customer_sites.Site', on_delete=models.CASCADE, null=True, blank=True, related_name='geographic_data')
    
    country_code = models.CharField(max_length=2)
    country_name = models.CharField(max_length=100)
    region = models.CharField(max_length=100, blank=True)
    city = models.CharField(max_length=100, blank=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    
    # Traffic metrics
    request_count = models.PositiveIntegerField(default=0)
    blocked_count = models.PositiveIntegerField(default=0)
    allowed_count = models.PositiveIntegerField(default=0)
    
    # Threat metrics
    threat_count = models.PositiveIntegerField(default=0)
    unique_ips = models.PositiveIntegerField(default=0)
    
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-request_count']
        unique_together = ['tenant', 'site', 'country_code', 'timestamp']
    
    def __str__(self):
        return f"{self.tenant.name} - {self.country_name} - {self.request_count} requests"


class AlertRule(models.Model):
    """Alert rules for monitoring and notifications"""
    ALERT_TYPES = [
        ('high_block_rate', 'High Block Rate'),
        ('unusual_traffic', 'Unusual Traffic Pattern'),
        ('new_threat', 'New Threat Detected'),
        ('performance_degradation', 'Performance Degradation'),
        ('geographic_anomaly', 'Geographic Anomaly'),
        ('rule_triggered', 'Rule Triggered'),
    ]
    
    tenant = models.ForeignKey('tenants.Tenant', on_delete=models.CASCADE, related_name='alert_rules')
    name = models.CharField(max_length=100)
    alert_type = models.CharField(max_length=30, choices=ALERT_TYPES)
    condition = models.TextField(help_text="JSON condition for triggering alert")
    threshold = models.FloatField(help_text="Threshold value for alert")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.tenant.name} - {self.name}"


class Alert(models.Model):
    """Generated alerts and notifications"""
    ALERT_STATUS = [
        ('active', 'Active'),
        ('acknowledged', 'Acknowledged'),
        ('resolved', 'Resolved'),
        ('dismissed', 'Dismissed'),
    ]
    
    tenant = models.ForeignKey('tenants.Tenant', on_delete=models.CASCADE, related_name='alerts')
    site = models.ForeignKey('customer_sites.Site', on_delete=models.CASCADE, null=True, blank=True, related_name='alerts')
    rule = models.ForeignKey(AlertRule, on_delete=models.CASCADE, related_name='alerts')
    
    title = models.CharField(max_length=200)
    message = models.TextField()
    severity = models.CharField(max_length=10, choices=SecurityReport.SEVERITY_LEVELS)
    status = models.CharField(max_length=15, choices=ALERT_STATUS, default='active')
    
    triggered_at = models.DateTimeField(auto_now_add=True)
    acknowledged_at = models.DateTimeField(null=True, blank=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    
    metadata = models.JSONField(default=dict, blank=True)
    
    class Meta:
        ordering = ['-triggered_at']
    
    def __str__(self):
        return f"{self.tenant.name} - {self.title}"