from django.contrib import admin
from .models import Rule, SiteRule


@admin.register(Rule)
class RuleAdmin(admin.ModelAdmin):
    list_display = ('name', 'severity', 'is_global', 'created_at')
    list_filter = ('severity', 'is_global', 'created_at')
    search_fields = ('name', 'description', 'pattern')


@admin.register(SiteRule)
class SiteRuleAdmin(admin.ModelAdmin):
    list_display = ('site', 'rule', 'enabled', 'priority', 'tenant')
    list_filter = ('enabled', 'priority', 'tenant', 'rule__severity')
    search_fields = ('site__domain', 'rule__name', 'tenant__name')
    raw_id_fields = ('site', 'rule', 'tenant')