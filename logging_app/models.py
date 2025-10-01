from django.db import models


class RequestLog(models.Model):
    """WAF request logs"""
    ACTION_CHOICES = [
        ('allow', 'Allow'),
        ('block', 'Block'),
        ('challenge', 'Challenge'),
    ]

    tenant = models.ForeignKey('tenants.Tenant', on_delete=models.CASCADE, related_name='request_logs')
    site = models.ForeignKey('customer_sites.Site', on_delete=models.SET_NULL, null=True, blank=True, related_name='request_logs')
    
    # Request details
    method = models.CharField(max_length=10)
    path = models.TextField()
    query_string = models.TextField(blank=True)
    remote_ip = models.GenericIPAddressField()
    user_agent = models.TextField(blank=True)
    host = models.CharField(max_length=255)
    
    # WAF decision
    matched_rule = models.ForeignKey('rules.Rule', null=True, blank=True, on_delete=models.SET_NULL)
    action = models.CharField(max_length=10, choices=ACTION_CHOICES)
    status_code = models.PositiveIntegerField()
    
    # Response details
    response_time_ms = models.PositiveIntegerField(null=True, blank=True)
    bytes_sent = models.PositiveIntegerField(null=True, blank=True)
    
    # Geo information (populated by ES ingest-geoip)
    country_code = models.CharField(max_length=2, blank=True)
    country_name = models.CharField(max_length=100, blank=True)
    city = models.CharField(max_length=100, blank=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    
    # Timestamps
    request_ts = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-request_ts']
        indexes = [
            models.Index(fields=['tenant', 'request_ts']),
            models.Index(fields=['site', 'request_ts']),
            models.Index(fields=['action', 'request_ts']),
            models.Index(fields=['remote_ip', 'request_ts']),
        ]

    def __str__(self):
        return f"{self.method} {self.path} - {self.action} ({self.remote_ip})"