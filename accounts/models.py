from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    """Custom User model with email as primary identifier"""
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=150, blank=True, null=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.email


class Profile(models.Model):
    """User profile with tenant and role information"""
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('customer_admin', 'Customer Admin'),
        ('customer_member', 'Customer Member'),
    ]
    
    THEME_CHOICES = [
        ('light', 'Light'),
        ('dark', 'Dark'),
    ]

    user = models.OneToOneField('User', on_delete=models.CASCADE, related_name='profile')
    tenant = models.ForeignKey('tenants.Tenant', on_delete=models.CASCADE, related_name='profiles')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='customer_member')
    theme_preference = models.CharField(max_length=10, choices=THEME_CHOICES, default='light')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['user', 'tenant']

    def __str__(self):
        return f"{self.user.email} - {self.tenant.name} ({self.role})"