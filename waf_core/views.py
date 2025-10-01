from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils.decorators import method_decorator
from django.views import View
import json
import time
from .pattern_engine import pattern_engine
from .rate_limiter import rate_limiter
from customer_sites.models import Site
from rules.models import SiteRule


@method_decorator(csrf_exempt, name='dispatch')
class WAFDecisionView(View):
    """
    WAF decision API for external auth with Caddy
    """
    
    def post(self, request):
        """Process WAF decision request from Caddy"""
        try:
            # Try to parse JSON data first (for direct API calls)
            try:
                data = json.loads(request.body)
                method = data.get('method', 'GET')
                path = data.get('path', '/')
                headers = data.get('headers', {})
                if isinstance(headers, str):
                    headers = {}
                query_string = data.get('query_string', '')
                client_ip = data.get('remote_addr', '127.0.0.1')
            except (json.JSONDecodeError, ValueError):
                # If not JSON, extract from HTTP request (for Caddy proxy)
                method = request.method
                path = request.path
                headers = dict(request.headers)
                query_string = request.GET.urlencode()
                client_ip = request.META.get('REMOTE_ADDR', '127.0.0.1')
            
            site_id = headers.get('X-Site-ID') or headers.get('X-Site-Id')
            tenant_id = headers.get('X-Tenant-ID') or headers.get('X-Tenant-Id')
            
            
            # Get site and tenant
            try:
                site = Site.objects.get(id=site_id, is_active=True)
                tenant = site.tenant
            except Site.DoesNotExist:
                return self._create_decision_response(False, f"Site not found: site_id={site_id}")
            
            # Rate limiting check
            is_limited, rate_info = rate_limiter.get_ip_rate_limit(client_ip)
            if is_limited:
                return self._create_decision_response(False, "Rate limit exceeded")
            
            # Get site rules
            site_rules = SiteRule.objects.filter(
                site=site,
                enabled=True
            ).select_related('rule').order_by('priority')
            
            # Build content to check
            content_to_check = {
                'path': path,
                'query_string': query_string,
                'user_agent': headers.get('User-Agent', headers.get('user-agent', '')),
                'referer': headers.get('Referer', headers.get('referer', '')),
                'host': headers.get('Host', headers.get('host', '')),
            }
            
            # Add all headers
            if isinstance(headers, dict):
                for header_name, header_value in headers.items():
                    content_to_check[f"header_{header_name.lower()}"] = header_value
            
            # Check security patterns
            security_check = self._check_security_patterns(content_to_check)
            if security_check:
                return self._create_decision_response(False, security_check['message'])
            
            # Check custom rules
            for site_rule in site_rules:
                pattern = site_rule.effective_pattern
                
                for content_type, content in content_to_check.items():
                    if pattern_engine.match_patterns(content, [pattern])[0]:
                        return self._create_decision_response(
                            False, 
                            f"Blocked by rule: {site_rule.rule.name}"
                        )
            
            # Request allowed
            return self._create_decision_response(True, "Request allowed")
            
        except Exception as e:
            return self._create_decision_response(False, f"WAF error: {str(e)}")
    
    def _check_security_patterns(self, content: dict) -> dict:
        """Check built-in security patterns"""
        # SQL Injection
        for content_type, content_value in content.items():
            if pattern_engine.check_sql_injection(content_value):
                return {
                    'message': 'SQL injection attempt detected',
                    'reason': f'SQL injection pattern in {content_type}'
                }
        
        # XSS
        for content_type, content_value in content.items():
            if pattern_engine.check_xss(content_value):
                return {
                    'message': 'XSS attempt detected',
                    'reason': f'XSS pattern in {content_type}'
                }
        
        # Path Traversal
        for content_type, content_value in content.items():
            if pattern_engine.check_path_traversal(content_value):
                return {
                    'message': 'Path traversal attempt detected',
                    'reason': f'Path traversal pattern in {content_type}'
                }
        
        # Command Injection
        for content_type, content_value in content.items():
            if pattern_engine.check_command_injection(content_value):
                return {
                    'message': 'Command injection attempt detected',
                    'reason': f'Command injection pattern in {content_type}'
                }
        
        # Suspicious User Agent
        if pattern_engine.check_user_agent_anomalies(content.get('user_agent', '')):
            return {
                'message': 'Suspicious user agent detected',
                'reason': 'Suspicious user agent pattern'
            }
        
        return None
    
    def _create_decision_response(self, allowed: bool, message: str) -> JsonResponse:
        """Create WAF decision response"""
        response_data = {
            'allowed': allowed,
            'message': message,
            'timestamp': int(time.time())
        }
        
        if not allowed:
            response_data['status_code'] = 403
        
        return JsonResponse(response_data)


@method_decorator(csrf_exempt, name='dispatch')
class WAFStatsView(View):
    """WAF statistics API"""
    
    def get(self, request):
        """Get WAF statistics"""
        from logging_app.models import RequestLog
        from django.db.models import Count
        from datetime import timedelta
        from django.utils import timezone
        
        # Get stats for last 24 hours
        last_24h = timezone.now() - timedelta(hours=24)
        
        stats = {
            'total_requests': RequestLog.objects.filter(
                request_ts__gte=last_24h
            ).count(),
            'blocked_requests': RequestLog.objects.filter(
                request_ts__gte=last_24h,
                action='block'
            ).count(),
            'allowed_requests': RequestLog.objects.filter(
                request_ts__gte=last_24h,
                action='allow'
            ).count(),
            'top_blocked_ips': list(
                RequestLog.objects.filter(
                    request_ts__gte=last_24h,
                    action='block'
                ).values('remote_ip').annotate(
                    count=Count('remote_ip')
                ).order_by('-count')[:10]
            ),
            'top_rules_triggered': list(
                RequestLog.objects.filter(
                    request_ts__gte=last_24h,
                    action='block',
                    matched_rule__isnull=False
                ).values('matched_rule__name').annotate(
                    count=Count('matched_rule__name')
                ).order_by('-count')[:10]
            )
        }
        
        return JsonResponse(stats)