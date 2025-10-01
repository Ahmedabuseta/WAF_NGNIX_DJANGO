from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied


class TenantScopedQuerysetMixin(LoginRequiredMixin):
    """Filter queryset by request.tenant and enforce presence."""

    tenant_field_name = "tenant"

    def get_queryset(self):
        queryset = super().get_queryset()
        tenant = getattr(self.request, "tenant", None)
        if tenant is None:
            raise PermissionDenied("Tenant not resolved")
        return queryset.filter(**{self.tenant_field_name: tenant})


class TenantFormValidMixin:
    """On create, set instance.tenant to request.tenant automatically."""

    tenant_field_name = "tenant"

    def form_valid(self, form):
        tenant = getattr(self.request, "tenant", None)
        if tenant is None:
            raise PermissionDenied("Tenant not resolved")
        setattr(form.instance, self.tenant_field_name, tenant)
        return super().form_valid(form)

