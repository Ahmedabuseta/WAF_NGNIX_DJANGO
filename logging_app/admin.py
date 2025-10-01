from django.contrib import admin
from .models import RequestLog


@admin.register(RequestLog)
class RequestLogAdmin(admin.ModelAdmin):
    list_display = ('method', 'path', 'remote_ip', 'action', 'matched_rule', 'status_code', 'request_ts')
    list_filter = ('action', 'method', 'status_code', 'matched_rule', 'tenant', 'request_ts')
    search_fields = ('path', 'remote_ip', 'user_agent', 'host')
    raw_id_fields = ('tenant', 'site', 'matched_rule')
    date_hierarchy = 'request_ts'
    readonly_fields = ('request_ts',)