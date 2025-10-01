from django.utils.deprecation import MiddlewareMixin
from django.shortcuts import redirect
from django.contrib import messages
from .models import Tenant


class TenantMiddleware(MiddlewareMixin):
    """
    Middleware to set request.tenant based on authenticated user's profile
    """
    
    def process_request(self, request):
        request.tenant = None
        
        if request.user.is_authenticated:
            try:
                profile = request.user.profile
                request.tenant = profile.tenant
            except:
                # User has no profile or tenant
                pass
        
        return None


class TenantRequiredMiddleware(MiddlewareMixin):
    """
    Middleware to ensure user has a tenant for protected views
    """
    
    def process_request(self, request):
        # Skip for public URLs
        public_paths = ['/admin/', '/accounts/', '/static/', '/media/']
        if any(request.path.startswith(path) for path in public_paths):
            return None
            
        # Skip for unauthenticated users
        if not request.user.is_authenticated:
            return None

        # Check if user has a tenant
        if not hasattr(request, 'tenant') or request.tenant is None:
            messages.error(request, 'You must be associated with a tenant to access this area.')
            return redirect('account_login')

        return None
