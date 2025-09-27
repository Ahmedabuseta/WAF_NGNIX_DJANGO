from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.utils import timezone
from datetime import timedelta
from allauth.account.signals import user_signed_up
from allauth.socialaccount.signals import social_account_added
from django.dispatch import receiver
import secrets


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('user_type', 'admin')
        extra_fields.setdefault('is_active', True)
        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser):
    USER_TYPE_CHOICES = [
        ('customer', 'Customer'),
        ('admin', 'Admin'),
    ]
    username = models.CharField(max_length=150, unique=False, blank=True, null=True)

    email = models.EmailField(unique=True)
    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES, default='customer')
    is_active = models.BooleanField(default=False)  # Changed to False for email verification
    is_email_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(null=True, blank=True)

    # Customer-specific fields
    company_name = models.CharField(max_length=100, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    first_name = models.CharField(max_length=50, blank=True)
    last_name = models.CharField(max_length=50, blank=True)

    # Admin-specific fields
    admin_level = models.CharField(max_length=20, choices=[
        ('super', 'Super Admin'),
        ('support', 'Support Admin'),
    ], blank=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return f"{self.email} ({self.user_type})"

    def has_perm(self, perm, obj=None):
        return self.user_type == 'admin'

    def has_module_perms(self, app_label):
        return self.user_type == 'admin'

    def get_all_permissions(self, obj=None):
        """Return a set of permission strings that this user has."""
        if self.user_type == 'admin':
            # Return common Django permissions for admin users
            return {
                'auth.add_user', 'auth.change_user', 'auth.delete_user', 'auth.view_user',
                'web_sites.add_site', 'web_sites.change_site', 'web_sites.delete_site', 'web_sites.view_site',
                'security.add_rule', 'security.change_rule', 'security.delete_rule', 'security.view_rule',
                'security.view_requestlog', 'security.delete_requestlog'
            }
        return set()

    def get_group_permissions(self, obj=None):
        """Return a set of permission strings that this user has through their groups."""
        return set()

    def get_user_permissions(self, obj=None):
        """Return a set of permission strings that this user has directly."""
        if self.user_type == 'admin':
            return {
                'auth.add_user', 'auth.change_user', 'auth.delete_user', 'auth.view_user',
                'web_sites.add_site', 'web_sites.change_site', 'web_sites.delete_site', 'web_sites.view_site',
                'security.add_rule', 'security.change_rule', 'security.delete_rule', 'security.view_rule',
                'security.view_requestlog', 'security.delete_requestlog'
            }
        return set()

    @property
    def is_staff(self):
        return self.user_type == 'admin'

    @property
    def is_superuser(self):
        return self.user_type == 'admin' and self.admin_level == 'super'


# Signal handlers for Google OAuth
@receiver(user_signed_up)
def activate_user_on_google_signup(request, user, **kwargs):
    """لو اليوزر عامل تسجيل أول مرة بجوجل"""
    if user and not user.is_active:
        user.is_active = True
        user.is_email_verified = True
        user.save()


@receiver(social_account_added)
def activate_user_on_google_connect(request, sociallogin, **kwargs):
    """لو يوزر قديم وربط حساب جوجل"""
    user = sociallogin.user
    if user and not user.is_active:
        user.is_active = True
        user.is_email_verified = True
        user.save()


class EmailVerificationToken(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    token = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if not self.token:
            self.token = secrets.token_urlsafe(50)
        if not self.expires_at:
            self.expires_at = timezone.now() + timedelta(hours=24)
        super().save(*args, **kwargs)

    def is_expired(self):
        return timezone.now() > self.expires_at

    def __str__(self):
        return f"Verification token for {self.user.email}"


class PasswordResetToken(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    token = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if not self.token:
            self.token = secrets.token_urlsafe(50)
        if not self.expires_at:
            self.expires_at = timezone.now() + timedelta(hours=1)
        super().save(*args, **kwargs)

    def is_expired(self):
        return timezone.now() > self.expires_at

    def __str__(self):
        return f"Password reset token for {self.user.email}"
