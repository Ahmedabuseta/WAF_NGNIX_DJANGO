from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.cache import cache
from .caddy_config import caddy_config_generator
from customer_sites.models import Site
from rules.models import SiteRule, Rule


@receiver(post_save, sender=Site)
@receiver(post_delete, sender=Site)
def update_caddy_on_site_change(sender, instance, **kwargs):
    """Update Caddy configuration when sites change"""
    # Clear site rules cache
    cache_key = f"site_rules_{instance.id}"
    cache.delete(cache_key)
    
    # Update Caddy configuration
    try:
        caddy_config_generator.update_caddy_config("combined")
    except Exception as e:
        print(f"Error updating Caddy config after site change: {e}")


@receiver(post_save, sender=SiteRule)
@receiver(post_delete, sender=SiteRule)
def update_caddy_on_rule_change(sender, instance, **kwargs):
    """Update Caddy configuration when site rules change"""
    # Clear site rules cache
    cache_key = f"site_rules_{instance.site.id}"
    cache.delete(cache_key)
    
    # Update Caddy configuration
    try:
        caddy_config_generator.update_caddy_config("combined")
    except Exception as e:
        print(f"Error updating Caddy config after rule change: {e}")


@receiver(post_save, sender=Rule)
@receiver(post_delete, sender=Rule)
def update_caddy_on_global_rule_change(sender, instance, **kwargs):
    """Update Caddy configuration when global rules change"""
    # Clear all site rules caches
    sites = Site.objects.filter(is_active=True)
    for site in sites:
        cache_key = f"site_rules_{site.id}"
        cache.delete(cache_key)
    
    # Update Caddy configuration
    try:
        caddy_config_generator.update_caddy_config("combined")
    except Exception as e:
        print(f"Error updating Caddy config after global rule change: {e}")


@receiver(post_save, sender=Site)
def clear_site_cache(sender, instance, **kwargs):
    """Clear site-related caches when site changes"""
    # Clear site resolution cache
    cache_key = f"site_{instance.tenant.id}_{instance.domain}"
    cache.delete(cache_key)
    
    # Clear site rules cache
    cache_key = f"site_rules_{instance.id}"
    cache.delete(cache_key)
