from django.views.generic import TemplateView
from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta
from core.mixins import TenantScopedQuerysetMixin
from customer_sites.models import Site
from rules.models import SiteRule
from logging_app.models import RequestLog


class DashboardHomeView(TenantScopedQuerysetMixin, TemplateView):
    template_name = 'dashboard/home.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        tenant = self.request.tenant
        now = timezone.now()
        last_24h = now - timedelta(hours=24)

        # Sites
        sites = Site.objects.filter(tenant=tenant)
        ctx['sites'] = sites
        ctx['sites_count'] = sites.count()
        ctx['active_sites'] = sites.filter(is_active=True).count()

        # Rules
        site_rules = SiteRule.objects.filter(tenant=tenant)
        ctx['rules_count'] = site_rules.count()
        ctx['enabled_rules'] = site_rules.filter(enabled=True).count()

        # Logs (last 24h)
        logs = RequestLog.objects.filter(tenant=tenant, request_ts__gte=last_24h)
        ctx['logs_24h'] = logs.count()
        ctx['blocks_24h'] = logs.filter(action='block').count()
        ctx['allows_24h'] = logs.filter(action='allow').count()

        # Top blocked IPs
        ctx['top_blocked_ips'] = (
            logs.filter(action='block')
            .values('remote_ip')
            .annotate(count=Count('id'))
            .order_by('-count')[:5]
        )

        # Top rules triggered
        ctx['top_rules'] = (
            logs.filter(matched_rule__isnull=False)
            .values('matched_rule__name')
            .annotate(count=Count('id'))
            .order_by('-count')[:5]
        )

        return ctx