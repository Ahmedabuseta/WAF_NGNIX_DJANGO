from django.db import models
from accounts.models import User


class Site(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    domain = models.CharField(max_length=255)
    backend_url = models.URLField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.domain} - {self.owner.email}"


class SiteStats(models.Model):
    site = models.ForeignKey(Site, on_delete=models.CASCADE)
    date = models.DateField()
    total_requests = models.IntegerField(default=0)
    blocked_requests = models.IntegerField(default=0)
    allowed_requests = models.IntegerField(default=0)
    avg_response_time = models.FloatField(default=0)

    class Meta:
        unique_together = ['site', 'date']

    def __str__(self):
        return f"{self.site.domain} - {self.date}"


class SiteRule(models.Model):
    ACTION_CHOICES = [
        ('BLOCK', 'Block'),
        ('ALLOW', 'Allow'),
        ('LOG', 'Log Only'),
    ]
    
    site = models.ForeignKey(Site, on_delete=models.CASCADE)
    rule = models.ForeignKey('security.Rule', on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)
    custom_action = models.CharField(max_length=20, choices=ACTION_CHOICES, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['site', 'rule']

    def __str__(self):
        return f"{self.site.domain} - {self.rule.name}"
