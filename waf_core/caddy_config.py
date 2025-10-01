import json
from typing import Dict, List, Any
from django.conf import settings
from customer_sites.models import Site
from tenants.models import Tenant


class CaddyConfigGenerator:
    """
    Generate Caddy configuration for L7 and L4 proxies
    """
    
    def __init__(self):
        self.waf_api_url = getattr(settings, 'WAF_API_URL', 'http://django:8000')
        self.l4_forwarder_url = getattr(settings, 'L4_FORWARDER_URL', 'localhost:8080')
    
    def generate_l7_config(self) -> str:
        """Generate L7 Caddy configuration (SSL termination + external auth)"""
        config = {
            "apps": {
                "http": {
                    "servers": {
                        "srv0": {
                            "listen": [":443"],
                            "routes": self._generate_l7_routes()
                        }
                    }
                },
                "tls": {
                    "automation": {
                        "policies": [
                            {
                                "subjects": ["*.waf.local"],
                                "issuers": [
                                    {
                                        "module": "acme",
                                        "ca": "https://acme-staging-v02.api.letsencrypt.org/directory"
                                    }
                                ]
                            }
                        ]
                    }
                }
            }
        }
        
        return json.dumps(config, indent=2)
    
    def generate_l4_config(self) -> str:
        """Generate L4 Caddy configuration (TCP forwarding)"""
        config = {
            "apps": {
                "layer4": {
                    "servers": {
                        "tcp_forwarder": {
                            "listen": [":80"],
                            "routes": self._generate_l4_routes()
                        }
                    }
                }
            }
        }
        
        return json.dumps(config, indent=2)
    
    def _generate_l7_routes(self) -> List[Dict[str, Any]]:
        """Generate L7 routes for external auth"""
        routes = []
        
        # Get all active sites
        sites = Site.objects.filter(is_active=True).select_related('tenant')
        
        for site in sites:
            route = {
                "match": [
                    {
                        "host": [site.domain]
                    }
                ],
                "handle": [
                    {
                        "handler": "reverse_proxy",
                        "upstreams": [
                            {
                                "dial": f"{self.l4_forwarder_url}"
                            }
                        ],
                        "headers": {
                            "request": {
                                "set": {
                                    "X-Original-Host": [site.domain],
                                    "X-Target-IP": [site.ip],
                                    "X-Target-Port": [str(site.port)]
                                }
                            }
                        }
                    }
                ]
            }
            
            # Add external auth for WAF decisions
            route["handle"].insert(0, {
                "handler": "subroute",
                "routes": [
                    {
                        "handle": [
                            {
                                "handler": "reverse_proxy",
                                "upstreams": [
                                    {
                                        "dial": f"{self.waf_api_url}/waf/waf/decision/"
                                    }
                                ],
                                "headers": {
                                    "request": {
                                        "set": {
                                            "X-Site-ID": [str(site.id)],
                                            "X-Tenant-ID": [str(site.tenant.id)]
                                        }
                                    }
                                }
                            }
                        ]
                    }
                ]
            })
            
            routes.append(route)
        
        return routes
    
    def _generate_l4_routes(self) -> List[Dict[str, Any]]:
        """Generate L4 routes for TCP forwarding"""
        routes = []
        
        # Get all active sites
        sites = Site.objects.filter(is_active=True)
        
        for site in sites:
            route = {
                "match": [
                    {
                        "tls": {
                            "sni": [site.domain]
                        }
                    }
                ],
                "handle": [
                    {
                        "handler": "proxy",
                        "upstreams": [
                            {
                                "dial": f"{site.ip}:{site.port}"
                            }
                        ]
                    }
                ]
            }
            routes.append(route)
        
        return routes
    
    def generate_combined_config(self) -> str:
        """Generate combined L7 + L4 configuration"""
        config = {
            "apps": {
                "http": {
                    "servers": {
                        "srv0": {
                            "listen": [":443"],
                            "routes": self._generate_l7_routes()
                        }
                    }
                },
                "layer4": {
                    "servers": {
                        "tcp_forwarder": {
                            "listen": [":80"],
                            "routes": self._generate_l4_routes()
                        }
                    }
                },
                "tls": {
                    "automation": {
                        "policies": [
                            {
                                "subjects": ["*.waf.local"],
                                "issuers": [
                                    {
                                        "module": "acme",
                                        "ca": "https://acme-staging-v02.api.letsencrypt.org/directory"
                                    }
                                ]
                            }
                        ]
                    }
                }
            }
        }
        
        return json.dumps(config, indent=2)
    
    def update_caddy_config(self, config_type: str = "combined") -> bool:
        """Update Caddy configuration via Admin API or file"""
        import requests
        import os
        
        try:
            if config_type == "l7":
                config = self.generate_l7_config()
            elif config_type == "l4":
                config = self.generate_l4_config()
            else:
                config = self.generate_combined_config()
            
            # Try file-based configuration first
            if self.update_caddy_config_file(config):
                print("✅ Caddy configuration updated via file")
                return True
            
            # Fallback to Admin API
            caddy_admin_url = getattr(settings, 'CADDY_ADMIN_URL', 'http://caddy-l7:2019')
            
            response = requests.post(
                f"{caddy_admin_url}/load",
                headers={"Content-Type": "application/json"},
                data=config,
                timeout=10
            )
            
            if response.status_code == 200:
                print("✅ Caddy configuration updated via API")
                return True
            else:
                print(f"⚠️ Caddy API update failed: {response.status_code}")
                return False
            
        except Exception as e:
            print(f"Error updating Caddy config: {e}")
            return False
    
    def update_caddy_config_file(self, config: str) -> bool:
        """Update Caddy configuration file"""
        import os
        
        try:
            # Define config file path
            config_file = "/app/configs/caddy/Caddyfile-dynamic.json"
            
            # Ensure directory exists
            os.makedirs(os.path.dirname(config_file), exist_ok=True)
            
            # Write configuration to file
            with open(config_file, 'w') as f:
                f.write(config)
            
            print(f"✅ Caddy config written to: {config_file}")
            print(f"📊 Config size: {len(config)} characters")
            
            # Log configuration details
            import json
            try:
                config_data = json.loads(config)
                routes = config_data.get('apps', {}).get('http', {}).get('servers', {}).get('srv0', {}).get('routes', [])
                print(f"🌐 Configured domains: {len(routes)}")
                for route in routes:
                    if 'match' in route and route['match']:
                        host = route['match'][0].get('host', ['unknown'])[0]
                        print(f"   - {host}")
            except Exception as e:
                print(f"⚠️ Could not parse config for logging: {e}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error writing Caddy config file: {e}")
            return False


# Global config generator instance
caddy_config_generator = CaddyConfigGenerator()
