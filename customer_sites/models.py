from django.db import models
from django.core.validators import RegexValidator


class Site(models.Model):
    """Customer site configuration"""
    tenant = models.ForeignKey('tenants.Tenant', on_delete=models.CASCADE, related_name='sites')
    name = models.CharField(max_length=150)
    domain = models.CharField(
        max_length=255,
        validators=[RegexValidator(
            regex=r'^[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?)*$',
            message='Enter a valid domain name'
        )]
    )
    ip = models.GenericIPAddressField()
    port = models.PositiveIntegerField(default=80)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['tenant', 'domain']
        ordering = ['name']

    def __str__(self):
        return f"{self.domain} ({self.tenant.name})"

    @property
    def origin_url(self):
        """Get the origin URL for this site"""
        protocol = 'https' if self.port == 443 else 'http'
        return f"{protocol}://{self.ip}:{self.port}"