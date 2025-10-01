from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from accounts.models import Profile
from tenants.models import Tenant
from customer_sites.models import Site
from rules.models import Rule, SiteRule
from logging_app.models import RequestLog
from analytics.models import AnalyticsMetric, SecurityReport, ThreatIntelligence
from datetime import datetime, timedelta
import random
import json

User = get_user_model()


class Command(BaseCommand):
    help = 'Seed the database with sample data'

    def handle(self, *args, **options):
        self.stdout.write('Seeding database with sample data...')
        
        # Create additional tenants and users
        self.create_tenants_and_users()
        
        # Create sample sites
        self.create_sample_sites()
        
        # Create sample rules
        self.create_sample_rules()
        
        # Create sample logs
        self.create_sample_logs()
        
        # Create sample analytics data
        self.create_sample_analytics()
        
        self.stdout.write(
            self.style.SUCCESS('Successfully seeded database with sample data!')
        )

    def create_tenants_and_users(self):
        """Create additional tenants and users"""
        # Create a few more tenants
        tenants_data = [
            {'name': 'Acme Corp', 'slug': 'acme-corp'},
            {'name': 'TechStart Inc', 'slug': 'techstart-inc'},
            {'name': 'Global Solutions', 'slug': 'global-solutions'},
        ]
        
        for tenant_data in tenants_data:
            tenant, created = Tenant.objects.get_or_create(
                slug=tenant_data['slug'],
                defaults={
                    'name': tenant_data['name'],
                    'owner': User.objects.get(email='admin@waf.com'),
                    'plan': random.choice(['basic', 'pro', 'enterprise']),
                    'is_active': True
                }
            )
            
            if created:
                # Create a user for this tenant
                user = User.objects.create_user(
                    email=f"{tenant_data['slug']}@example.com",
                    username=f"{tenant_data['slug']}@example.com",
                    password='password123',
                    first_name=tenant_data['name'].split()[0],
                    last_name=tenant_data['name'].split()[-1] if len(tenant_data['name'].split()) > 1 else 'User'
                )
                
                Profile.objects.create(
                    user=user,
                    tenant=tenant,
                    role=random.choice(['customer_admin', 'customer_member']),
                    theme_preference=random.choice(['light', 'dark'])
                )

    def create_sample_sites(self):
        """Create sample customer sites"""
        sites_data = [
            {'name': 'Main Website', 'domain': 'example.com', 'ip': '192.168.1.100', 'port': 80},
            {'name': 'API Server', 'domain': 'api.example.com', 'ip': '192.168.1.101', 'port': 443},
            {'name': 'Admin Panel', 'domain': 'admin.example.com', 'ip': '192.168.1.102', 'port': 8080},
            {'name': 'Blog', 'domain': 'blog.example.com', 'ip': '192.168.1.103', 'port': 80},
            {'name': 'E-commerce', 'domain': 'shop.example.com', 'ip': '192.168.1.104', 'port': 443},
        ]
        
        for tenant in Tenant.objects.all():
            for site_data in sites_data:
                Site.objects.get_or_create(
                    tenant=tenant,
                    domain=site_data['domain'],
                    defaults={
                        'name': site_data['name'],
                        'ip': site_data['ip'],
                        'port': site_data['port'],
                        'is_active': random.choice([True, True, True, False])  # 75% active
                    }
                )

    def create_sample_rules(self):
        """Create sample WAF rules"""
        rules_data = [
            {
                'name': 'SQL Injection Protection',
                'pattern': r'(?i)(union|select|insert|delete|update|drop|create|alter|exec|execute).*?(from|into|table|database)',
                'description': 'Blocks common SQL injection patterns',
                'is_global': True
            },
            {
                'name': 'XSS Protection',
                'pattern': r'(?i)<script[^>]*>.*?</script>|<iframe[^>]*>.*?</iframe>|javascript:|on\w+\s*=',
                'description': 'Blocks cross-site scripting attempts',
                'is_global': True
            },
            {
                'name': 'Path Traversal',
                'pattern': r'(?i)\.\./|\.\.\\|%2e%2e%2f|%2e%2e%5c',
                'description': 'Blocks directory traversal attempts',
                'is_global': True
            },
            {
                'name': 'Command Injection',
                'pattern': r'(?i)(;|\||&|`|\$\(|\$\{).*(ls|cat|pwd|whoami|id|uname|ps|netstat)',
                'description': 'Blocks command injection attempts',
                'is_global': True
            },
            {
                'name': 'Suspicious User Agent',
                'pattern': r'(?i)(bot|crawler|spider|scraper|scanner|hack|exploit)',
                'description': 'Blocks suspicious user agents',
                'is_global': False
            },
            {
                'name': 'Rate Limiting',
                'pattern': r'.*',
                'description': 'Rate limiting rule (applied per IP)',
                'is_global': True
            }
        ]
        
        for rule_data in rules_data:
            rule, created = Rule.objects.get_or_create(
                name=rule_data['name'],
                defaults=rule_data
            )
            
            # Create site rules for active sites
            for site in Site.objects.filter(is_active=True):
                SiteRule.objects.get_or_create(
                    site=site,
                    rule=rule,
                    defaults={
                        'tenant': site.tenant,
                        'enabled': random.choice([True, True, True, False]),  # 75% enabled
                        'priority': random.randint(1, 1000)
                    }
                )

    def create_sample_logs(self):
        """Create sample request logs"""
        actions = ['allow', 'block', 'challenge']
        methods = ['GET', 'POST', 'PUT', 'DELETE', 'HEAD', 'OPTIONS']
        paths = [
            '/', '/api/users', '/api/auth/login', '/admin/', '/dashboard/',
            '/products/', '/cart/', '/checkout/', '/search', '/contact',
            '/about', '/blog/', '/news/', '/support/', '/api/data'
        ]
        
        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36',
            'Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15',
            'Mozilla/5.0 (Android 10; Mobile; rv:68.0) Gecko/68.0 Firefox/68.0',
            'python-requests/2.25.1',
            'curl/7.68.0',
            'PostmanRuntime/7.26.8'
        ]
        
        countries = ['US', 'CA', 'GB', 'DE', 'FR', 'JP', 'AU', 'BR', 'IN', 'CN']
        cities = ['New York', 'London', 'Tokyo', 'Berlin', 'Paris', 'Sydney', 'Toronto', 'Mumbai']
        
        # Create logs for the last 7 days
        for days_ago in range(7):
            date = datetime.now() - timedelta(days=days_ago)
            
            # Create 50-200 logs per day
            num_logs = random.randint(50, 200)
            
            for _ in range(num_logs):
                site = random.choice(Site.objects.filter(is_active=True))
                action = random.choices(actions, weights=[70, 25, 5])[0]  # 70% allow, 25% block, 5% challenge
                
                # Generate realistic IP addresses
                if random.random() < 0.8:  # 80% legitimate IPs
                    ip = f"{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}"
                else:  # 20% suspicious IPs
                    ip = random.choice([
                        '192.168.1.1', '10.0.0.1', '172.16.0.1',  # Private IPs
                        '127.0.0.1', '0.0.0.0'  # Localhost
                    ])
                
                log = RequestLog.objects.create(
                    tenant=site.tenant,
                    site=site,
                    method=random.choice(methods),
                    path=random.choice(paths),
                    query_string=f"param{random.randint(1, 10)}={random.randint(1, 100)}" if random.random() < 0.3 else "",
                    remote_ip=ip,
                    user_agent=random.choice(user_agents),
                    host=site.domain,
                    matched_rule=random.choice(site.site_rules.filter(enabled=True)).rule if action == 'block' and site.site_rules.filter(enabled=True).exists() else None,
                    action=action,
                    status_code=200 if action == 'allow' else (403 if action == 'block' else 429),
                    response_time_ms=random.randint(1, 100),
                    bytes_sent=random.randint(100, 50000),
                    request_ts=date + timedelta(seconds=random.randint(0, 86399)),
                    country_code=random.choice(countries),
                    country_name=random.choice(['United States', 'Canada', 'United Kingdom', 'Germany', 'France', 'Japan', 'Australia', 'Brazil', 'India', 'China']),
                    city=random.choice(cities),
                    latitude=round(random.uniform(-90, 90), 6),
                    longitude=round(random.uniform(-180, 180), 6)
                )

    def create_sample_analytics(self):
        """Create sample analytics data"""
        # Create analytics metrics for the last 30 days
        for days_ago in range(30):
            date = datetime.now() - timedelta(days=days_ago)
            
            for tenant in Tenant.objects.all():
                # Traffic metrics
                AnalyticsMetric.objects.create(
                    tenant=tenant,
                    metric_type='requests_total',
                    value=random.randint(1000, 10000),
                    timestamp=date,
                    metadata={'source': 'waf'}
                )
                
                # Security metrics
                AnalyticsMetric.objects.create(
                    tenant=tenant,
                    metric_type='blocks_total',
                    value=random.randint(10, 500),
                    timestamp=date,
                    metadata={'source': 'waf'}
                )
                
                # Performance metrics
                AnalyticsMetric.objects.create(
                    tenant=tenant,
                    metric_type='avg_response_time',
                    value=round(random.uniform(50, 500), 2),
                    timestamp=date,
                    metadata={'source': 'waf'}
                )
        
        # Create security reports
        for tenant in Tenant.objects.all():
            SecurityReport.objects.create(
                tenant=tenant,
                report_type='daily',
                severity=random.choice(['low', 'medium', 'high']),
                title=f'Daily Security Report - {tenant.name}',
                summary=f'Security summary for {tenant.name} showing various threats and blocked requests.',
                details={
                    'total_requests': random.randint(5000, 50000),
                    'blocked_requests': random.randint(50, 1000),
                    'top_threats': [
                        {'threat': 'SQL Injection', 'count': random.randint(10, 100)},
                        {'threat': 'XSS', 'count': random.randint(5, 50)},
                        {'threat': 'Path Traversal', 'count': random.randint(3, 30)},
                    ],
                    'top_ips': [
                        {'ip': '192.168.1.100', 'count': random.randint(5, 50)},
                        {'ip': '10.0.0.1', 'count': random.randint(3, 30)},
                    ]
                },
                period_start=datetime.now() - timedelta(days=1),
                period_end=datetime.now()
            )
        
        # Create threat intelligence data
        threats = [
            {'name': 'SQL Injection', 'severity': 'high', 'type': 'attack_pattern', 'indicator': 'union select'},
            {'name': 'XSS Attack', 'severity': 'medium', 'type': 'attack_pattern', 'indicator': '<script>'},
            {'name': 'Path Traversal', 'severity': 'high', 'type': 'attack_pattern', 'indicator': '../'},
            {'name': 'Command Injection', 'severity': 'critical', 'type': 'attack_pattern', 'indicator': '; ls'},
            {'name': 'Suspicious IP', 'severity': 'low', 'type': 'ip_reputation', 'indicator': '192.168.1.100'},
        ]
        
        for tenant in Tenant.objects.all():
            for threat_data in threats:
                ThreatIntelligence.objects.create(
                    tenant=tenant,
                    threat_type=threat_data['type'],
                    indicator=threat_data['indicator'],
                    confidence_score=round(random.uniform(0.5, 1.0), 2),
                    severity=threat_data['severity'],
                    description=f"Sample {threat_data['name']} threat detected",
                    source='internal',
                    is_active=True
                )
