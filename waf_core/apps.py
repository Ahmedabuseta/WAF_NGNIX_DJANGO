from django.apps import AppConfig


class WafCoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'waf_core'
    
    def ready(self):
        import waf_core.signals