from django.contrib import admin
from .models import Site


@admin.register(Site)
class SiteAdmin(admin.ModelAdmin):
    list_display = ('name', 'domain', 'ip', 'port', 'tenant', 'is_active', 'created_at')
    list_filter = ('is_active', 'tenant', 'created_at')
    search_fields = ('name', 'domain', 'ip', 'tenant__name')
    raw_id_fields = ('tenant',)