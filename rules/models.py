from django.db import models


class Rule(models.Model):
    """WAF rule definitions (admin-created)"""
    name = models.CharField(max_length=150, unique=True)
    pattern = models.TextField(help_text="Regex pattern or signature to match")
    description = models.TextField(blank=True)
    is_global = models.BooleanField(default=False, help_text="Apply to all sites by default")
    severity = models.CharField(max_length=20, choices=[
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ], default='medium')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class SiteRule(models.Model):
    """Per-site rule enablement and configuration"""
    tenant = models.ForeignKey('tenants.Tenant', on_delete=models.CASCADE)
    site = models.ForeignKey('customer_sites.Site', on_delete=models.CASCADE, related_name='site_rules')
    rule = models.ForeignKey(Rule, on_delete=models.CASCADE)
    enabled = models.BooleanField(default=True)
    priority = models.PositiveIntegerField(default=100, help_text="Lower numbers = higher priority")
    custom_pattern = models.TextField(blank=True, help_text="Override the default pattern for this site")

    class Meta:
        unique_together = ['site', 'rule']
        ordering = ['priority', 'rule__name']

    def __str__(self):
        return f"{self.site.domain} - {self.rule.name}"

    @property
    def effective_pattern(self):
        """Get the pattern to use for this site rule"""
        return self.custom_pattern or self.rule.pattern