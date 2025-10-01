from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib import messages
from allauth.socialaccount.models import SocialAccount
from .models import Profile, User
from tenants.models import Tenant


def google_login(request):
    """Custom Google OAuth login view"""
    if request.user.is_authenticated:
        return redirect('dashboard:home')
    
    # This will be handled by allauth, but we can customize the redirect
    return redirect('account_login')


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