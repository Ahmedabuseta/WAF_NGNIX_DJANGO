import re
import time
from typing import List, Dict, Tuple, Optional
from django.core.cache import cache
from django.conf import settings
from rules.models import SiteRule


class PatternEngine:
    """High-performance pattern matching engine for WAF rules"""
    
    def __init__(self):
        self.compiled_patterns = {}
        self.cache_timeout = getattr(settings, 'WAF_PATTERN_CACHE_TIMEOUT', 300)
    
    def compile_pattern(self, pattern: str) -> re.Pattern:
        """Compile and cache regex patterns"""
        cache_key = f"waf_pattern_{hash(pattern)}"
        compiled = cache.get(cache_key)
        
        if compiled is None:
            try:
                compiled = re.compile(pattern, re.IGNORECASE | re.MULTILINE)
                cache.set(cache_key, compiled, self.cache_timeout)
            except re.error as e:
                # Log error and return a pattern that never matches
                print(f"Invalid regex pattern: {pattern}, error: {e}")
                compiled = re.compile(r'(?!.*)')  # Never matches
        
        return compiled
    
    def match_patterns(self, content: str, patterns: List[str]) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Match content against multiple patterns
        Returns: (matched, matched_pattern, match_type)
        """
        for pattern in patterns:
            compiled = self.compile_pattern(pattern)
            if compiled.search(content):
                return True, pattern, 'regex'
        
        return False, None, None
    
    def check_sql_injection(self, content: str) -> bool:
        """Check for SQL injection patterns"""
        sql_patterns = [
            r"(\b(union|select|insert|update|delete|drop|create|alter|exec|execute)\b)",
            r"(\b(or|and)\s+\d+\s*=\s*\d+)",
            r"(\b(union|select).*from)",
            r"(--|\#|\/\*|\*\/)",
            r"(\b(union|select).*information_schema)",
            r"(\b(union|select).*pg_|mysql\.|sys\.)",
        ]
        
        matched, _, _ = self.match_patterns(content, sql_patterns)
        return matched
    
    def check_xss(self, content: str) -> bool:
        """Check for XSS patterns"""
        xss_patterns = [
            r"<script[^>]*>.*?</script>",
            r"javascript:",
            r"on\w+\s*=",
            r"<iframe[^>]*>",
            r"<object[^>]*>",
            r"<embed[^>]*>",
            r"<link[^>]*>",
            r"<meta[^>]*>",
            r"expression\s*\(",
            r"vbscript:",
        ]
        
        matched, _, _ = self.match_patterns(content, xss_patterns)
        return matched
    
    def check_path_traversal(self, content: str) -> bool:
        """Check for path traversal patterns"""
        traversal_patterns = [
            r"\.\./",
            r"\.\.\\",
            r"\.\.%2f",
            r"\.\.%5c",
            r"\.\.%252f",
            r"\.\.%255c",
            r"\.\.%c0%af",
            r"\.\.%c1%9c",
        ]
        
        matched, _, _ = self.match_patterns(content, traversal_patterns)
        return matched
    
    def check_command_injection(self, content: str) -> bool:
        """Check for command injection patterns"""
        cmd_patterns = [
            r"[;&|`$]",
            r"\b(cat|ls|pwd|whoami|id|uname|ps|netstat|ifconfig)\b",
            r"\b(rm|del|mkdir|rmdir|copy|move)\b",
            r"\b(ping|nslookup|traceroute|telnet|ssh|ftp)\b",
            r"\b(wget|curl|nc|netcat)\b",
            r"\b(perl|python|ruby|php|bash|sh|cmd|powershell)\b",
        ]
        
        matched, _, _ = self.match_patterns(content, cmd_patterns)
        return matched
    
    def check_user_agent_anomalies(self, user_agent: str) -> bool:
        """Check for suspicious user agents"""
        if not user_agent:
            return True  # Empty user agent is suspicious
        
        suspicious_patterns = [
            r"sqlmap",
            r"nikto",
            r"nmap",
            r"masscan",
            r"zap",
            r"burp",
            r"w3af",
            r"havij",
            r"acunetix",
            r"nessus",
            r"openvas",
            r"wget",
            r"curl",
            r"python-requests",
            r"go-http-client",
            r"libwww-perl",
            r"lwp-",
            r"^$",  # Empty user agent
        ]
        
        matched, _, _ = self.match_patterns(user_agent, suspicious_patterns)
        return matched
    
    def get_rule_severity(self, rule_name: str) -> str:
        """Get rule severity based on rule name patterns"""
        if any(keyword in rule_name.lower() for keyword in ['sql', 'injection', 'xss', 'rce']):
            return 'critical'
        elif any(keyword in rule_name.lower() for keyword in ['traversal', 'injection', 'bypass']):
            return 'high'
        elif any(keyword in rule_name.lower() for keyword in ['scan', 'probe', 'test']):
            return 'medium'
        else:
            return 'low'


# Global pattern engine instance
pattern_engine = PatternEngine()
