from django.core.management.base import BaseCommand
from django.test import RequestFactory
from waf_core.pattern_engine import pattern_engine
from waf_core.rate_limiter import rate_limiter
from waf_core.caddy_config import caddy_config_generator


class Command(BaseCommand):
    help = 'Test WAF functionality'

    def handle(self, *args, **options):
        self.stdout.write("Testing WAF Core Components...")
        
        # Test Pattern Engine
        self.test_pattern_engine()
        
        # Test Rate Limiter
        self.test_rate_limiter()
        
        # Test Caddy Config Generator
        self.test_caddy_config()
        
        self.stdout.write(self.style.SUCCESS("WAF Core tests completed!"))

    def test_pattern_engine(self):
        """Test pattern engine functionality"""
        self.stdout.write("\n--- Testing Pattern Engine ---")
        
        # Test SQL injection detection
        sql_payloads = [
            "'; DROP TABLE users; --",
            "1' OR '1'='1",
            "UNION SELECT * FROM users",
            "admin'--",
        ]
        
        for payload in sql_payloads:
            result = pattern_engine.check_sql_injection(payload)
            self.stdout.write(f"SQL Injection '{payload}': {'BLOCKED' if result else 'ALLOWED'}")
        
        # Test XSS detection
        xss_payloads = [
            "<script>alert('xss')</script>",
            "javascript:alert('xss')",
            "<img src=x onerror=alert('xss')>",
            "normal text",
        ]
        
        for payload in xss_payloads:
            result = pattern_engine.check_xss(payload)
            self.stdout.write(f"XSS '{payload}': {'BLOCKED' if result else 'ALLOWED'}")
        
        # Test path traversal detection
        traversal_payloads = [
            "../../../etc/passwd",
            "..\\..\\..\\windows\\system32\\config\\sam",
            "normal/path/file.txt",
        ]
        
        for payload in traversal_payloads:
            result = pattern_engine.check_path_traversal(payload)
            self.stdout.write(f"Path Traversal '{payload}': {'BLOCKED' if result else 'ALLOWED'}")

    def test_rate_limiter(self):
        """Test rate limiter functionality"""
        self.stdout.write("\n--- Testing Rate Limiter ---")
        
        test_ip = "192.168.1.100"
        
        # Test IP rate limiting
        for i in range(5):
            is_limited, rate_info = rate_limiter.get_ip_rate_limit(test_ip)
            self.stdout.write(f"Request {i+1}: {'LIMITED' if is_limited else 'ALLOWED'} - {rate_info['remaining']} remaining")
        
        # Test endpoint rate limiting
        test_endpoint = "/api/test"
        for i in range(3):
            is_limited, rate_info = rate_limiter.get_endpoint_rate_limit(test_ip, test_endpoint)
            self.stdout.write(f"Endpoint Request {i+1}: {'LIMITED' if is_limited else 'ALLOWED'} - {rate_info['remaining']} remaining")

    def test_caddy_config(self):
        """Test Caddy configuration generation"""
        self.stdout.write("\n--- Testing Caddy Config Generator ---")
        
        try:
            # Generate L7 config
            l7_config = caddy_config_generator.generate_l7_config()
            self.stdout.write(f"L7 Config generated: {len(l7_config)} characters")
            
            # Generate L4 config
            l4_config = caddy_config_generator.generate_l4_config()
            self.stdout.write(f"L4 Config generated: {len(l4_config)} characters")
            
            # Generate combined config
            combined_config = caddy_config_generator.generate_combined_config()
            self.stdout.write(f"Combined Config generated: {len(combined_config)} characters")
            
            self.stdout.write("Caddy configuration generation successful!")
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Caddy config generation failed: {e}"))
