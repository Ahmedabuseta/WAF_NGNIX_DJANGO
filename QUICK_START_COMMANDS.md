# Quick Start Commands 🚀

## 🏃‍♂️ Essential Commands

### Start Everything
```bash
# Start all services
docker-compose up -d

# Check status
docker-compose ps
```

### Stop Everything
```bash
# Stop all services
docker-compose down

# Stop and remove volumes (⚠️ deletes data)
docker-compose down -v
```

### Restart Services
```bash
# Restart all
docker-compose restart

# Restart specific service
docker-compose restart django
docker-compose restart elasticsearch
docker-compose restart kibana
```

## 🗄️ Database Commands

### Migrations
```bash
# Apply migrations
docker-compose exec django python manage.py migrate

# Create superuser
docker-compose exec django python manage.py createsuperuser

# Show migrations status
docker-compose exec django python manage.py showmigrations
```

### Database Access
```bash
# Access PostgreSQL
docker-compose exec db psql -U waf_user -d waf_db

# Create backup
docker-compose exec db pg_dump -U waf_user waf_db > backup.sql
```

## 🎨 Frontend Commands

### Tailwind CSS
```bash
# Install dependencies
npm install

# Compile CSS (development)
npx @tailwindcss/cli -i ./static/src/input.css -o ./static/src/output.css --watch

# Compile CSS (production)
npx @tailwindcss/cli -i ./static/src/input.css -o ./static/src/output.css --minify
```

### Static Files
```bash
# Collect static files
docker-compose exec django python manage.py collectstatic --noinput
```

## 📊 Analytics & Monitoring

### Kibana Setup
```bash
# Run Kibana setup
./setup-kibana.sh

# Check Kibana status
curl http://localhost:5601/api/status
```

### Elasticsearch
```bash
# Check health
curl http://localhost:9200/_cluster/health

# List indices
curl http://localhost:9200/_cat/indices
```

## 🔍 Debugging Commands

### View Logs
```bash
# All services
docker-compose logs

# Specific service
docker-compose logs django
docker-compose logs elasticsearch
docker-compose logs kibana
docker-compose logs db
docker-compose logs redis

# Follow logs (real-time)
docker-compose logs -f django
```

### Service Health Checks
```bash
# Django application
curl http://localhost:8000/health/

# Elasticsearch
curl http://localhost:9200/_cluster/health

# Kibana
curl http://localhost:5601/api/status

# Redis
docker-compose exec redis redis-cli ping
```

### Django Management
```bash
# Django shell
docker-compose exec django python manage.py shell

# Django checks
docker-compose exec django python manage.py check

# Create test data
docker-compose exec django python manage.py loaddata fixtures/test_data.json
```

## 🏭 Production Commands

### Production Deployment
```bash
# Start production stack
docker-compose -f docker-compose.prod.yml up -d

# Production migrations
docker-compose -f docker-compose.prod.yml exec django python manage.py migrate

# Production static files
docker-compose -f docker-compose.prod.yml exec django python manage.py collectstatic --noinput
```

### Environment Setup
```bash
# Copy environment template
cp .env.example .env

# Edit environment variables
nano .env
```

## 🧹 Cleanup Commands

### Clean Docker
```bash
# Remove unused containers
docker container prune

# Remove unused images
docker image prune

# Remove unused volumes
docker volume prune

# Remove everything unused
docker system prune -a
```

### Reset System
```bash
# Stop and remove everything
docker-compose down -v

# Remove all containers and images
docker-compose down --rmi all -v

# Start fresh
docker-compose up -d
```

## 📱 Service URLs

| Service | URL | Purpose |
|---------|-----|---------|
| Django App | http://localhost:8000 | Main application |
| Django Admin | http://localhost:8000/admin/ | Admin interface |
| Kibana | http://localhost:5601 | Analytics dashboard |
| Elasticsearch | http://localhost:9200 | Search engine |
| Grafana | http://localhost:3000 | Metrics dashboard |
| Prometheus | http://localhost:9090 | Metrics collection |

## 🚨 Emergency Commands

### If Everything Breaks
```bash
# Nuclear option - reset everything
docker-compose down -v
docker system prune -a
docker-compose up -d
```

### If Database is Corrupted
```bash
# Stop services
docker-compose down

# Remove database volume
docker volume rm waf_app_postgres_data

# Start fresh
docker-compose up -d
docker-compose exec django python manage.py migrate
```

### If Elasticsearch is Broken
```bash
# Stop services
docker-compose down

# Remove Elasticsearch volume
docker volume rm waf_app_elasticsearch_data

# Start fresh
docker-compose up -d elasticsearch kibana
./setup-kibana.sh
```

## 🔧 Development Tips

### Hot Reload
```bash
# For Django changes (auto-reloads)
docker-compose up django

# For CSS changes (run separately)
npx @tailwindcss/cli -i ./static/src/input.css -o ./static/src/output.css --watch
```

### Debug Mode
```bash
# Enable Django debug mode
export DEBUG=1
docker-compose up django
```

### Access Running Container
```bash
# Access Django container
docker-compose exec django bash

# Access database container
docker-compose exec db bash

# Access Elasticsearch container
docker-compose exec elasticsearch bash
```

---

## 💡 Pro Tips

1. **Always check logs first** when something isn't working
2. **Use `docker-compose ps`** to see service status
3. **Keep Tailwind CSS watcher running** during development
4. **Check service health** before troubleshooting
5. **Use `docker-compose logs -f`** to follow logs in real-time

**Happy coding!** 🎉