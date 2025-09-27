from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_protect
from django.utils import timezone
from waf_proxy.models import User, EmailVerificationToken, PasswordResetToken
from core.utils import send_verification_email, send_password_reset_email, send_welcome_email
from core.decorators import login_required_custom


@csrf_protect
def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard:dashboard')
    
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        captcha_answer = request.POST.get('captcha_answer')
        
        # Simple CAPTCHA validation
        try:
            captcha_value = int(captcha_answer) if captcha_answer else 0
            if captcha_value < 2 or captcha_value > 20:
                messages.error(request, 'Please complete the CAPTCHA correctly')
                return render(request, 'accounts/login.html')
        except (ValueError, TypeError):
            messages.error(request, 'Please complete the CAPTCHA correctly')
            return render(request, 'accounts/login.html')
        
        # Authenticate user
        user = authenticate(request, username=email, password=password)
        
        if user:
            if not user.is_email_verified:
                messages.error(request, 'Please verify your email address before signing in')
                return render(request, 'accounts/login.html')
            
            login(request, user)
            user.last_login = timezone.now()
            user.save()
            messages.success(request, f'Welcome back, {user.first_name or user.email}!')
            return redirect('dashboard:dashboard')
        else:
            messages.error(request, 'Invalid email or password')
    
    return render(request, 'accounts/login.html')


def logout_view(request):
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('accounts:login')


@csrf_protect
def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard:dashboard')
    
    if request.method == 'POST':
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        company_name = request.POST.get('company_name')
        phone = request.POST.get('phone')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        
        # Validation
        if not email:
            messages.error(request, 'Email is required')
            return render(request, 'accounts/register.html')
        
        if password1 != password2:
            messages.error(request, 'Passwords do not match')
            return render(request, 'accounts/register.html')
        
        if len(password1) < 8:
            messages.error(request, 'Password must be at least 8 characters long')
            return render(request, 'accounts/register.html')
        
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already exists')
            return render(request, 'accounts/register.html')
        
        # Create user
        user = User.objects.create_user(
            email=email,
            password=password1,
            company_name=company_name,
            phone=phone,
            first_name=first_name,
            last_name=last_name,
            user_type='customer'
        )
        
        # Send verification email
        if send_verification_email(user):
            messages.success(request, f'Registration successful! Please check your email ({email}) to verify your account.')
            return render(request, 'accounts/email_sent.html', {'email': email})
        else:
            messages.error(request, 'Registration successful, but failed to send verification email. Please contact support.')
            return render(request, 'accounts/register.html')
    
    return render(request, 'accounts/register.html')


@login_required_custom
def profile(request):
    return render(request, 'accounts/profile.html', {'user': request.user})


@login_required_custom
def user_settings(request):
    if request.method == 'POST':
        # Handle settings update
        user = request.user
        user.first_name = request.POST.get('first_name', user.first_name)
        user.last_name = request.POST.get('last_name', user.last_name)
        user.company_name = request.POST.get('company_name', user.company_name)
        user.phone = request.POST.get('phone', user.phone)
        user.save()
        messages.success(request, 'Settings updated successfully!')
        return redirect('accounts:user_settings')
    
    return render(request, 'accounts/settings.html')


def forgot_password(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            user = User.objects.get(email=email)
            if send_password_reset_email(user):
                messages.success(request, f'Password reset email sent to {email}')
                return render(request, 'accounts/email_sent.html', {'email': email})
            else:
                messages.error(request, 'Failed to send password reset email. Please try again.')
        except User.DoesNotExist:
            messages.error(request, 'Email not found')
    
    return render(request, 'accounts/forgot_password.html')


def reset_password(request, token):
    try:
        reset_token = PasswordResetToken.objects.get(token=token, is_used=False)
        if reset_token.is_expired():
            messages.error(request, 'Password reset link has expired')
            return redirect('accounts:forgot_password')
        
        if request.method == 'POST':
            password1 = request.POST.get('password1')
            password2 = request.POST.get('password2')
            
            if password1 != password2:
                messages.error(request, 'Passwords do not match')
                return render(request, 'accounts/reset_password.html', {'user': reset_token.user})
            
            if len(password1) < 8:
                messages.error(request, 'Password must be at least 8 characters long')
                return render(request, 'accounts/reset_password.html', {'user': reset_token.user})
            
            # Update password
            reset_token.user.set_password(password1)
            reset_token.user.save()
            reset_token.is_used = True
            reset_token.save()
            
            messages.success(request, 'Password updated successfully! Please log in with your new password.')
            return redirect('accounts:login')
        
        return render(request, 'accounts/reset_password.html', {'user': reset_token.user})
    
    except PasswordResetToken.DoesNotExist:
        messages.error(request, 'Invalid password reset link')
        return redirect('accounts:forgot_password')


def verify_email(request, token):
    try:
        verification_token = EmailVerificationToken.objects.get(token=token, is_used=False)
        if verification_token.is_expired():
            messages.error(request, 'Email verification link has expired')
            return redirect('accounts:login')
        
        # Activate user
        user = verification_token.user
        user.is_email_verified = True
        user.is_active = True
        user.save()
        
        verification_token.is_used = True
        verification_token.save()
        
        # Send welcome email
        send_welcome_email(user)
        
        messages.success(request, 'Email verified successfully! You can now log in.')
        return render(request, 'accounts/email_verified.html', {'user': user})
    
    except EmailVerificationToken.DoesNotExist:
        messages.error(request, 'Invalid email verification link')
        return redirect('accounts:login')


def resend_verification(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            user = User.objects.get(email=email)
            if user.is_email_verified:
                messages.info(request, 'Email is already verified')
                return redirect('accounts:login')
            
            if send_verification_email(user):
                messages.success(request, f'Verification email sent to {email}')
                return render(request, 'accounts/email_sent.html', {'email': email})
            else:
                messages.error(request, 'Failed to send verification email. Please try again.')
        except User.DoesNotExist:
            messages.error(request, 'Email not found')
    
    return render(request, 'accounts/forgot_password.html')
