from django.views.generic import ListView
from django.utils import timezone
from core.mixins import TenantScopedQuerysetMixin
from .models import RequestLog


class RequestLogListView(TenantScopedQuerysetMixin, ListView):
    model = RequestLog
    template_name = 'logs/request_log_list.html'
    context_object_name = 'logs'
    paginate_by = 25

    def get_queryset(self):
        qs = super().get_queryset()
        method = self.request.GET.get('method')
        action = self.request.GET.get('action')
        start = self.request.GET.get('start')
        end = self.request.GET.get('end')

        if method:
            qs = qs.filter(method__iexact=method)
        if action:
            qs = qs.filter(action=action)
        if start:
            qs = qs.filter(request_ts__gte=start)
        if end:
            qs = qs.filter(request_ts__lte=end)

        return qs.select_related('site', 'matched_rule')

# Create your views here.
