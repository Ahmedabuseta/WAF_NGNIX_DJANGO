## WAF App Compass

Scope: Multi-tenant WAF SaaS using Django (CBV), Flowbite UI, Caddy, Postgres, Redis, Celery, Elasticsearch. No i18n for now. Cloudflare-like theme with dark mode.

### Multitenancy
- Row-based multitenancy via `tenant` FK on all domain models.
- `TenantMiddleware` sets `request.tenant` from authenticated user's profile.
- Queryset mixins/managers enforce filtering by `tenant`.

### Apps and Responsibilities
- accounts: Custom `User`, Google OAuth login, email verification, password reset; `Profile(tenant, role, theme)`.
- tenants: `Tenant(name, slug, owner, plan, is_active)`; admin-only CRUD.
- sites: `Site(tenant, name, domain, ip, port, is_active)`; customer CRUD.
- rules: `Rule(name, pattern, description, is_global)`, `SiteRule(tenant, site, rule, enabled, priority)`; admin/global rules, customer enable/ordering.
- waf_core: WAF inspection middleware; L4 forwarding service to origin `ip:port` per site.
- logging_app: `RequestLog` ORM store; Celery tasks to index to Elasticsearch.
- analytics: ES aggregations for traffic, top rules, geo map endpoints.
- dashboard: Customer portal CBVs; sites, rules, logs, analytics.
- admin_panel: Operator surface beyond Django admin.
- ui: Shared Flowbite/Tailwind base, components, dark mode.

### Auth (accounts)
- Google OAuth using `django-allauth` (only Google enabled).
- Email verification on signup; password reset via Django auth views.
- Enforce `tenant` on session; role-based access control (admin, customer_admin, customer_member).

### WAF Architecture Flow
```
Client (HTTPS)
    ↓
Caddy L7 (SSL termination + external auth)
    ↓
Python WAF (security decisions via FastAPI)
    ↓
Caddy L4 (high-performance TCP forwarding)
    ↓
Customer Server (raw TCP with original client IP)
```

### WAF Core
- **Caddy L7**: TLS termination, basic routing, external auth to Python WAF
- **Python WAF**: FastAPI/ASGI service for security decisions (rules, patterns, allow/block)
- **Caddy L4**: Layer 4 proxy for pure TCP forwarding to customer origins
- **Django**: Control plane only - manages rules, tenants, sites, dynamic config updates

### Caddy Integration
- **L7 Caddy**: Handles HTTPS, calls Python WAF for decisions, adds security headers
- **L4 Caddy**: High-performance TCP forwarding (using layer4 plugin via xcaddy)
- **Dynamic Updates**: Django signals -> Celery tasks -> update both Caddy instances via Admin API

### Logging & Elasticsearch
- Minimal fields persisted in Postgres for UI; full detail in ES.
- ES index `waf-requests-YYYY.MM.DD`; ILM retention; optional ingest-geoip for geo mapping.
- Bulk indexer via Celery with retry/backoff.

### Analytics
- Endpoints providing JSON for charts: traffic histogram, action ratios, top rules, top IPs, geo distribution.
- UI uses Flowbite + Chart.js and Leaflet for map.

### UI/Theme
- Cloudflare-like shell: topbar + sidebar, cards, tables.
- Dark mode via `class` strategy; toggle stored in profile/localStorage.

### Docker & One-Line Production
- Services: web (gunicorn), worker, beat, db (postgres), redis, es, caddy.
- One-liner: `make prod` builds, migrates, collects static, starts stack.

### Initial Milestones
1) Scaffold apps and base templates
2) Implement models (Tenant, Site, Rule, SiteRule, RequestLog)
3) Tenant & site resolution middleware
4) Basic WAF inspection and logging to DB
5) ES integration and Celery worker
6) Dashboard CBVs with Flowbite UI
7) Dynamic Caddy updates on site create/update/delete
8) Analytics endpoints and map
9) Dockerize and one-line deploy


