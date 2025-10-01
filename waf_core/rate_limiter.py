import time
from typing import Optional, Dict, Any, Tuple
from django.core.cache import cache
from django.conf import settings


class RateLimiter:
    """Rate limiting implementation for WAF"""
    
    def __init__(self):
        self.cache_timeout = getattr(settings, 'WAF_RATE_LIMIT_CACHE_TIMEOUT', 3600)
    
    def is_rate_limited(self, 
                       identifier: str, 
                       limit: int, 
                       window: int,
                       rule_name: str = "default") -> Tuple[bool, Dict[str, Any]]:
        """
        Check if identifier is rate limited
        
        Args:
            identifier: Unique identifier (IP, user, etc.)
            limit: Number of requests allowed
            window: Time window in seconds
            rule_name: Name of the rate limiting rule
        
        Returns:
            (is_limited, rate_info)
        """
        cache_key = f"waf_rate_limit_{rule_name}_{identifier}"
        now = int(time.time())
        window_start = now - window
        
        # Get existing requests from cache
        requests = cache.get(cache_key, [])
        
        # Filter requests within the current window
        requests = [req_time for req_time in requests if req_time > window_start]
        
        # Check if limit exceeded
        is_limited = len(requests) >= limit
        
        if not is_limited:
            # Add current request
            requests.append(now)
            cache.set(cache_key, requests, self.cache_timeout)
        
        rate_info = {
            'current_requests': len(requests),
            'limit': limit,
            'window': window,
            'reset_time': window_start + window,
            'remaining': max(0, limit - len(requests))
        }
        
        return is_limited, rate_info
    
    def get_ip_rate_limit(self, ip: str) -> Tuple[bool, Dict[str, Any]]:
        """Rate limit by IP address"""
        return self.is_rate_limited(
            identifier=ip,
            limit=100,  # 100 requests
            window=60,  # per minute
            rule_name="ip"
        )
    
    def get_user_rate_limit(self, user_id: str) -> Tuple[bool, Dict[str, Any]]:
        """Rate limit by user ID"""
        return self.is_rate_limited(
            identifier=user_id,
            limit=200,  # 200 requests
            window=60,  # per minute
            rule_name="user"
        )
    
    def get_endpoint_rate_limit(self, ip: str, endpoint: str) -> Tuple[bool, Dict[str, Any]]:
        """Rate limit by IP + endpoint combination"""
        identifier = f"{ip}:{endpoint}"
        return self.is_rate_limited(
            identifier=identifier,
            limit=50,  # 50 requests
            window=60,  # per minute
            rule_name="endpoint"
        )
    
    def get_brute_force_limit(self, ip: str) -> Tuple[bool, Dict[str, Any]]:
        """Rate limit for brute force protection"""
        return self.is_rate_limited(
            identifier=ip,
            limit=5,  # 5 attempts
            window=300,  # per 5 minutes
            rule_name="brute_force"
        )


# Global rate limiter instance
rate_limiter = RateLimiter()
