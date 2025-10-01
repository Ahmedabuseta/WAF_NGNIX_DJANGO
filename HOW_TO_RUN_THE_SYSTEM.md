# How to Run the WAF System 🚀

This comprehensive guide will walk you through running your multi-tenant WAF (Web Application Firewall) system in both development and production environments.

## 📋 System Overview

Your WAF system is a sophisticated multi-tenant SaaS platform that includes:

- **Django Backend**: Control plane for managing tenants, sites, and rules
- **Elasticsearch + Kibana**: Logging and analytics platform
- **Redis**: Caching and message broker
- **PostgreSQL**: Primary database
- **Celery**: Background task processing
- **Caddy**: L7 and L4 proxy services
- **Flowbite UI**: Modern frontend interface

## 🏗️ Architecture Flow

```
Client Request (HTTPS)
    ↓
Caddy L7 (SSL termination + auth)
    ↓
Python WAF (security decisions)
    ↓
Caddy L4 (TCP forwarding)
    ↓
Customer Server (origin)
```

## 🚀 Quick Start (Development)

### Prerequisites

Make sure you have installed:
- **Docker & Docker Compose**
- **Node.js** (for Tailwind CSS compilation)
- **Python 3.8+** (if running locally)

### 1. Clone and Setup

```bash
cd /home/override/Desktop/WAF_APP
```

### 2. Install Frontend Dependencies

```bash
# Install Node.js dependencies for Tailwind CSS
npm install
```

### 3. Start All Services

```bash
# Start the entire stack
docker-compose up -d
```

This will start:
- ✅ PostgreSQL database
- ✅ Redis cache & message broker
- ✅ Elasticsearch for logging
- ✅ Kibana for analytics
- ✅ Django application
- ✅ Celery worker
- ✅ Celery beat scheduler

### 4. Run Database Migrations

```bash
# Apply database migrations
docker-compose exec django python manage.py migrate

# Create superuser (optional)
docker-compose exec django python manage.py createsuperuser
```

### 5. Collect Static Files

```bash
# Collect static files for production
docker-compose exec django python manage.py collectstatic --noinput
```

### 6. Compile Tailwind CSS

```bash
# Compile Tailwind CSS (run in separate terminal)
npx @tailwindcss/cli -i ./static/src/input.css -o ./static/src/output.css --watch
```

### 7. Access the System

- **Main Application**: http://localhost:8000
- **Admin Panel**: http://localhost:8000/admin/
- **Kibana Analytics**: http://localhost:5601
- **Elasticsearch**: http://localhost:9200

## 🏭 Production Setup

### 1. Environment Configuration

Create a `.env` file for production:

```bash
# Database
POSTGRES_DB=waf_prod_db
POSTGRES_USER=waf_prod_user
POSTGRES_PASSWORD=your_secure_password

# Redis
REDIS_PASSWORD=your_redis_password

# Django
SECRET_KEY=your_django_secret_key
DEBUG=0
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

# Kibana
KIBANA_PUBLIC_URL=https://yourdomain.com/kibana

# Grafana
GRAFANA_PASSWORD=your_grafana_password
```

### 2. Production Deployment

```bash
# Start production stack
docker-compose -f docker-compose.prod.yml up -d

# Run migrations
docker-compose -f docker-compose.prod.yml exec django python manage.py migrate

# Collect static files
docker-compose -f docker-compose.prod.yml exec django python manage.py collectstatic --noinput
```

## 🔧 Individual Service Management

### Start Specific Services

```bash
# Start only database services
docker-compose up -d db redis elasticsearch

# Start only application services
docker-compose up -d django celery celery-beat

# Start monitoring stack
docker-compose up -d prometheus grafana kibana
```

### Service Status Check

```bash
# Check all services status
docker-compose ps

# Check specific service logs
docker-compose logs django
docker-compose logs elasticsearch
docker-compose logs kibana
```

### Restart Services

```bash
# Restart all services
docker-compose restart

# Restart specific service
docker-compose restart django
```

## 🛠️ Development Workflow

### 1. Local Development (Without Docker)

If you prefer to run Django locally:

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install frontend dependencies
npm install

# Set up environment variables
export DEBUG=1
export DATABASE_URL=postgresql://waf_user:waf_password@localhost:5432/waf_db
export REDIS_URL=redis://localhost:6379/0

# Run database migrations
python manage.py migrate

# Start Django development server
python manage.py runserver

# In another terminal, start Celery worker
celery -A flowbiteapp worker -l info

# In another terminal, start Celery beat
celery -A flowbiteapp beat -l info

# In another terminal, compile Tailwind CSS
npx @tailwindcss/cli -i ./static/src/input.css -o ./static/src/output.css --watch
```

### 2. Database Management

```bash
# Access PostgreSQL
docker-compose exec db psql -U waf_user -d waf_db

# Create database backup
docker-compose exec db pg_dump -U waf_user waf_db > backup.sql

# Restore database backup
docker-compose exec -T db psql -U waf_user -d waf_db < backup.sql
```

### 3. Elasticsearch Management

```bash
# Check Elasticsearch health
curl http://localhost:9200/_cluster/health

# List indices
curl http://localhost:9200/_cat/indices

# Setup Kibana (if not done already)
./setup-kibana.sh
```

## 📊 Monitoring and Analytics

### Kibana Setup

```bash
# Run the Kibana setup script
./setup-kibana.sh
```

Access Kibana at: http://localhost:5601

### Grafana Monitoring

Access Grafana at: http://localhost:3000
- Username: `admin`
- Password: `admin` (or your configured password)

### Prometheus Metrics

Access Prometheus at: http://localhost:9090

## 🔍 Troubleshooting

### Common Issues

#### 1. Services Won't Start

```bash
# Check Docker status
docker ps -a

# Check service logs
docker-compose logs [service_name]

# Restart specific service
docker-compose restart [service_name]
```

#### 2. Database Connection Issues

```bash
# Check PostgreSQL status
docker-compose exec db pg_isready -U waf_user -d waf_db

# Check database logs
docker-compose logs db
```

#### 3. Elasticsearch Issues

```bash
# Check Elasticsearch health
curl http://localhost:9200/_cluster/health

# Check Elasticsearch logs
docker-compose logs elasticsearch
```

#### 4. Kibana Issues

```bash
# Check Kibana status
curl http://localhost:5601/api/status

# Check Kibana logs
docker-compose logs kibana
```

#### 5. Django Application Issues

```bash
# Check Django logs
docker-compose logs django

# Access Django shell
docker-compose exec django python manage.py shell

# Run Django checks
docker-compose exec django python manage.py check
```

### Port Conflicts

If you have port conflicts, modify the ports in `docker-compose.yml`:

```yaml
services:
  django:
    ports:
      - "8001:8000"  # Change from 8000:8000
  kibana:
    ports:
      - "5602:5601"  # Change from 5601:5601
```

## 🎯 System Components

### Core Applications

1. **accounts**: User authentication, Google OAuth, profiles
2. **tenants**: Multi-tenant management
3. **customer_sites**: Site management for customers
4. **rules**: WAF rules and patterns
5. **waf_core**: WAF inspection middleware
6. **logging_app**: Request logging to Elasticsearch
7. **analytics**: Analytics endpoints and data processing
8. **dashboard**: Customer portal interface
9. **admin_panel**: Administrative interface

### External Services

- **PostgreSQL**: Primary database
- **Redis**: Cache and message broker
- **Elasticsearch**: Log storage and search
- **Kibana**: Log visualization and analytics
- **Prometheus**: Metrics collection
- **Grafana**: Metrics visualization

## 🔐 Security Considerations

### Development
- Security is disabled for easier development
- Use strong passwords for production
- Enable HTTPS in production

### Production
- Enable Django security features
- Use environment variables for secrets
- Configure proper CORS settings
- Set up SSL/TLS certificates

## 📈 Performance Optimization

### Database
- Use connection pooling
- Optimize queries with proper indexing
- Regular database maintenance

### Elasticsearch
- Configure proper sharding
- Set up index lifecycle management
- Monitor cluster health

### Application
- Use Redis for caching
- Optimize static file serving
- Configure proper logging levels

## 🚀 Deployment Checklist

### Pre-deployment
- [ ] Environment variables configured
- [ ] Database migrations applied
- [ ] Static files collected
- [ ] SSL certificates installed
- [ ] Domain DNS configured

### Post-deployment
- [ ] Health checks passing
- [ ] Monitoring configured
- [ ] Backup strategy implemented
- [ ] Log rotation configured
- [ ] Security scanning completed

## 📞 Support

### Documentation
- `COMPASS.md`: System architecture overview
- `KIBANA_SETUP.md`: Kibana configuration guide
- `README.md`: Basic setup instructions

### Logs Location
- Application logs: `docker-compose logs django`
- Database logs: `docker-compose logs db`
- Elasticsearch logs: `docker-compose logs elasticsearch`
- Kibana logs: `docker-compose logs kibana`

### Health Checks
```bash
# Application health
curl http://localhost:8000/health/

# Database health
docker-compose exec db pg_isready -U waf_user -d waf_db

# Elasticsearch health
curl http://localhost:9200/_cluster/health

# Kibana health
curl http://localhost:5601/api/status
```

---

## 🎉 You're Ready!

Your WAF system is now running! You can:

1. **Access the main application** at http://localhost:8000
2. **View analytics** in Kibana at http://localhost:5601
3. **Monitor metrics** in Grafana at http://localhost:3000
4. **Manage the system** through the Django admin at http://localhost:8000/admin/

For any issues, check the troubleshooting section above or review the service logs.

**Happy WAF-ing!** 🛡️