import re
import time
import json
from typing import Optional
from django.utils.deprecation import MiddlewareMixin
from django.http import HttpResponseForbidden, JsonResponse
from django.core.cache import cache
from django.conf import settings
from customer_sites.models import Site
from rules.models import SiteRule
from .pattern_engine import pattern_engine
from .rate_limiter import rate_limiter


class SiteResolutionMiddleware(MiddlewareMixin):
    """
    Middleware to resolve request.site from Host header within current tenant
    """
    
    def process_request(self, request):
        request.site = None
        
        if not hasattr(request, 'tenant') or request.tenant is None:
            return None
            
        host = request.get_host().split(':')[0]  # Remove port if present
        
        try:
            request.site = Site.objects.get(
                tenant=request.tenant,
                domain=host,
                is_active=True
            )
        except Site.DoesNotExist:
            # No site found for this domain
            pass
            
        return None


class WAFInspectionMiddleware(MiddlewareMixin):
    """
    Enhanced WAF inspection middleware with pattern engine and rate limiting
    """
    
    def process_request(self, request):
        # Skip if no site resolved
        if not hasattr(request, 'site') or request.site is None:
            return None
            
        # Skip for admin and static files
        if request.path.startswith(('/admin/', '/static/', '/media/')):
            return None
            
        start_time = time.time()
        client_ip = self._get_client_ip(request)
        
        # Rate limiting checks
        if self._check_rate_limits(request, client_ip):
            return self._create_block_response('Rate limit exceeded', 'rate_limit')
        
        # Get enabled rules for this site
        site_rules = self._get_site_rules(request.site)
        
        # Enhanced pattern matching
        block_reason = self._evaluate_rules(request, site_rules)
        if block_reason:
            self._log_request(request, block_reason['rule'], 'block', start_time, block_reason)
            return self._create_block_response(
                block_reason['message'], 
                block_reason['reason'],
                block_reason.get('rule')
            )
        
        # Request allowed
        self._log_request(request, None, 'allow', start_time)
        return None
    
    def _check_rate_limits(self, request, client_ip: str) -> bool:
        """Check various rate limits"""
        # IP-based rate limiting
        is_limited, rate_info = rate_limiter.get_ip_rate_limit(client_ip)
        if is_limited:
            return True
        
        # Endpoint-based rate limiting
        is_limited, _ = rate_limiter.get_endpoint_rate_limit(client_ip, request.path)
        if is_limited:
            return True
        
        # Brute force protection for login endpoints
        if request.path in ['/accounts/login/', '/accounts/signup/']:
            is_limited, _ = rate_limiter.get_brute_force_limit(client_ip)
            if is_limited:
                return True
        
        return False
    
    def _get_site_rules(self, site) -> list:
        """Get cached site rules"""
        cache_key = f"site_rules_{site.id}"
        site_rules = cache.get(cache_key)
        
        if site_rules is None:
            site_rules = SiteRule.objects.filter(
                site=site,
                enabled=True
            ).select_related('rule').order_by('priority')
            cache.set(cache_key, list(site_rules), 300)  # Cache for 5 minutes
        
        return site_rules
    
    def _evaluate_rules(self, request, site_rules) -> Optional[dict]:
        """Evaluate all rules against the request"""
        # Build content to check
        content_to_check = {
            'path': request.path,
            'query_string': request.META.get('QUERY_STRING', ''),
            'user_agent': request.META.get('HTTP_USER_AGENT', ''),
            'referer': request.META.get('HTTP_REFERER', ''),
            'host': request.get_host(),
        }
        
        # Add all headers
        for header_name, header_value in request.META.items():
            if header_name.startswith('HTTP_'):
                content_to_check[f"header_{header_name[5:].lower()}"] = header_value
        
        # Check built-in security patterns first
        security_check = self._check_security_patterns(content_to_check)
        if security_check:
            return security_check
        
        # Check custom rules
        for site_rule in site_rules:
            pattern = site_rule.effective_pattern
            
            for content_type, content in content_to_check.items():
                if pattern_engine.match_patterns(content, [pattern])[0]:
                    return {
                        'rule': site_rule.rule,
                        'message': f'Request blocked by rule: {site_rule.rule.name}',
                        'reason': f'Pattern match in {content_type}',
                        'severity': pattern_engine.get_rule_severity(site_rule.rule.name)
                    }
        
        return None
    
    def _check_security_patterns(self, content: dict) -> Optional[dict]:
        """Check built-in security patterns"""
        # SQL Injection
        for content_type, content in content.items():
            if pattern_engine.check_sql_injection(content):
                return {
                    'rule': None,
                    'message': 'SQL injection attempt detected',
                    'reason': f'SQL injection pattern in {content_type}',
                    'severity': 'critical'
                }
        
        # XSS
        for content_type, content in content.items():
            if pattern_engine.check_xss(content):
                return {
                    'rule': None,
                    'message': 'XSS attempt detected',
                    'reason': f'XSS pattern in {content_type}',
                    'severity': 'high'
                }
        
        # Path Traversal
        for content_type, content in content.items():
            if pattern_engine.check_path_traversal(content):
                return {
                    'rule': None,
                    'message': 'Path traversal attempt detected',
                    'reason': f'Path traversal pattern in {content_type}',
                    'severity': 'high'
                }
        
        # Command Injection
        for content_type, content in content.items():
            if pattern_engine.check_command_injection(content):
                return {
                    'rule': None,
                    'message': 'Command injection attempt detected',
                    'reason': f'Command injection pattern in {content_type}',
                    'severity': 'critical'
                }
        
        # Suspicious User Agent
        if pattern_engine.check_user_agent_anomalies(content.get('user_agent', '')):
            return {
                'rule': None,
                'message': 'Suspicious user agent detected',
                'reason': 'Suspicious user agent pattern',
                'severity': 'medium'
            }
        
        return None
    
    def _create_block_response(self, message: str, reason: str, rule=None) -> HttpResponseForbidden:
        """Create a standardized block response"""
        response_data = {
            'error': 'Request blocked by WAF',
            'message': message,
            'reason': reason,
            'timestamp': int(time.time())
        }
        
        if rule:
            response_data['rule'] = rule.name if hasattr(rule, 'name') else str(rule)
        
        return HttpResponseForbidden(
            JsonResponse(response_data),
            content_type='application/json'
        )
    
    def _get_client_ip(self, request) -> str:
        """Get client IP address from request"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR', '127.0.0.1')
        return ip
    
    def _log_request(self, request, matched_rule, action, start_time, block_reason=None):
        """Log the request decision"""
        from logging_app.models import RequestLog
        
        processing_time = int((time.time() - start_time) * 1000)  # Convert to milliseconds
        
        # Create log entry
        RequestLog.objects.create(
            tenant=request.tenant,
            site=request.site,
            method=request.method,
            path=request.path,
            query_string=request.META.get('QUERY_STRING', ''),
            remote_ip=self._get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
            headers={k: v for k, v in request.META.items() if k.startswith('HTTP_')},
            matched_rule=matched_rule,
            action=action,
            status_code=403 if action == 'block' else 200,
            processing_time_ms=processing_time
        )