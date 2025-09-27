# Legacy waf_proxy models - These have been moved to separate apps
# This file is kept for backward compatibility during migration
# Models have been moved to:
# - User, EmailVerificationToken, PasswordResetToken -> accounts app
# - Site, SiteStats, SiteRule -> sites app  
# - Rule, RequestLog, RateLimit -> security app

# Import models from the new apps for backward compatibility
from accounts.models import User, EmailVerificationToken, PasswordResetToken
from web_sites.models import Site, SiteStats, SiteRule
from security.models import Rule, RequestLog, RateLimit

# Re-export for backward compatibility
__all__ = [
    'User', 'EmailVerificationToken', 'PasswordResetToken',
    'Site', 'SiteStats', 'SiteRule', 
    'Rule', 'RequestLog', 'RateLimit'
]
