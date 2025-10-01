from django.db import models


class Tenant(models.Model):
    """Multi-tenant organization model"""
    name = models.CharField(max_length=150)
    slug = models.SlugField(unique=True)
    owner = models.ForeignKey('accounts.User', on_delete=models.PROTECT, related_name='owned_tenants')
    plan = models.CharField(max_length=50, default='basic', choices=[
        ('basic', 'Basic'),
        ('pro', 'Pro'),
        ('enterprise', 'Enterprise'),
    ])
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name