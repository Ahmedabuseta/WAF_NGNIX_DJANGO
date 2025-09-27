from django.db import models
from web_sites.models import Site


class Rule(models.Model):
    RULE_TYPE_CHOICES = [
        ('sql_injection', 'SQL Injection'),
        ('xss', 'Cross-Site Scripting'),
        ('path_traversal', 'Path Traversal'),
        ('rate_limit', 'Rate Limiting'),
        ('bot_detection', 'Bot Detection'),
        ('custom', 'Custom Pattern'),
    ]

    ACTION_CHOICES = [
        ('BLOCK', 'Block'),
        ('ALLOW', 'Allow'),
        ('LOG', 'Log Only'),
    ]

    name = models.CharField(max_length=100)
    pattern = models.TextField()
    rule_type = models.CharField(max_length=50, choices=RULE_TYPE_CHOICES)
    action = models.CharField(max_length=20, choices=ACTION_CHOICES, default='BLOCK')
    description = models.TextField(blank=True)
    is_global = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.rule_type})"


class RequestLog(models.Model):
    STATUS_CHOICES = [
        ('ALLOWED', 'Allowed'),
        ('BLOCKED', 'Blocked'),
        ('RATE_LIMITED', 'Rate Limited'),
    ]

    site = models.ForeignKey(Site, on_delete=models.CASCADE)
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField()
    method = models.CharField(max_length=10)
    path = models.TextField()
    query_string = models.TextField(blank=True)
    headers = models.JSONField(default=dict)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    rule_triggered = models.ForeignKey(Rule, on_delete=models.SET_NULL, null=True, blank=True)
    response_time = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.site.domain} - {self.ip_address} - {self.status}"


class RateLimit(models.Model):
    site = models.ForeignKey(Site, on_delete=models.CASCADE)
    ip_address = models.GenericIPAddressField()
    request_count = models.IntegerField(default=1)
    window_start = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['site', 'ip_address']

    def __str__(self):
        return f"{self.site.domain} - {self.ip_address} - {self.request_count}"
