"""
Utility functions for WAF authentication
"""

from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.urls import reverse
from accounts.models import EmailVerificationToken, PasswordResetToken
import logging

logger = logging.getLogger(__name__)


def send_verification_email(user):
    """Send email verification to user"""

    # Create or get existing token
    token, created = EmailVerificationToken.objects.get_or_create(
        user=user,
        is_used=False,
        defaults={}
    )

    # If token exists but is expired, create a new one
    if not created and token.is_expired():
        token.delete()
        token = EmailVerificationToken.objects.create(user=user)

    # Build verification URL
    verification_url = f"{settings.SITE_URL}{reverse('verify_email', args=[token.token])}"

    # Email context
    context = {
        'user': user,
        'verification_url': verification_url,
        'site_name': 'WAF Security',
    }

    # Render email templates
    subject = f"Verify your email - {context['site_name']}"
    html_message = render_to_string('waf_proxy/emails/verification_email.html', context)
    plain_message = f"Please click the following link to verify your email: {verification_url}"

    try:
        send_mail(
            subject=subject,
            message=plain_message,
            html_message=html_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )
        logger.info(f"Verification email sent to {user.email}")
        return True
    except Exception as e:
        logger.error(f"Failed to send verification email to {user.email}: {e}")
        return False


def send_password_reset_email(user):
    """Send password reset email to user"""

    # Create or get existing token
    token, created = PasswordResetToken.objects.get_or_create(
        user=user,
        is_used=False,
        defaults={}
    )

    # If token exists but is expired, create a new one
    if not created and token.is_expired():
        token.delete()
        token = PasswordResetToken.objects.create(user=user)

    # Build reset URL
    reset_url = f"{settings.SITE_URL}{reverse('reset_password', args=[token.token])}"

    # Email context
    context = {
        'user': user,
        'reset_url': reset_url,
        'site_name': 'WAF Security',
    }

    # Render email templates
    subject = f"Password Reset - {context['site_name']}"
    html_message = render_to_string('waf_proxy/emails/password_reset_email.html', context)
    plain_message = f"Please click the following link to reset your password: {reset_url}"

    try:
        send_mail(
            subject=subject,
            message=plain_message,
            html_message=html_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )
        logger.info(f"Password reset email sent to {user.email}")
        return True
    except Exception as e:
        logger.error(f"Failed to send password reset email to {user.email}: {e}")
        return False


def send_welcome_email(user):
    """Send welcome email to new user"""

    # Email context
    context = {
        'user': user,
        'site_name': 'WAF Security',
        'login_url': f"{settings.SITE_URL}{reverse('login')}",
    }

    # Render email templates
    subject = f"Welcome to {context['site_name']}!"
    html_message = render_to_string('waf_proxy/emails/welcome_email.html', context)
    plain_message = f"Welcome to {context['site_name']}! You can now log in and start using our services."

    try:
        send_mail(
            subject=subject,
            message=plain_message,
            html_message=html_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )
        logger.info(f"Welcome email sent to {user.email}")
        return True
    except Exception as e:
        logger.error(f"Failed to send welcome email to {user.email}: {e}")
        return False
