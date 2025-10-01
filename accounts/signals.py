from django.db.models.signals import post_save
from django.dispatch import receiver
from allauth.socialaccount.signals import social_account_added
from .models import Profile
from tenants.models import Tenant


@receiver(social_account_added)
def create_profile_for_social_user(sender, request, sociallogin, **kwargs):
    """Signal handler to create profile for social login users"""
    user = sociallogin.user
    
    # Create a default tenant for the user if they don't have one
    if not hasattr(user, 'profile') or not user.profile.tenant:
        # Create a personal tenant for the user
        tenant = Tenant.objects.create(
            name=f"{user.email.split('@')[0]}'s Organization",
            slug=f"{user.email.split('@')[0]}-org",
            owner=user
        )
        
        # Create profile
        Profile.objects.create(
            user=user,
            tenant=tenant,
            role='customer_admin'
        )
