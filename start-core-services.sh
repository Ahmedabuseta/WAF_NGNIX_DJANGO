#!/bin/bash

# Start Core WAF Services (without Caddy proxies)
# This script starts the essential services to get your WAF system running

echo "🚀 Starting Core WAF Services..."

# Start essential services only
docker-compose up -d db redis elasticsearch kibana django celery celery-beat

echo "⏳ Waiting for services to be ready..."

# Wait for database
echo "Waiting for PostgreSQL..."
until docker-compose exec db pg_isready -U waf_user -d waf_db > /dev/null 2>&1; do
    echo "PostgreSQL not ready yet..."
    sleep 2
done
echo "✅ PostgreSQL is ready!"

# Wait for Redis
echo "Waiting for Redis..."
until docker-compose exec redis redis-cli ping > /dev/null 2>&1; do
    echo "Redis not ready yet..."
    sleep 2
done
echo "✅ Redis is ready!"

# Wait for Elasticsearch
echo "Waiting for Elasticsearch..."
until curl -f http://localhost:9200/_cluster/health > /dev/null 2>&1; do
    echo "Elasticsearch not ready yet..."
    sleep 5
done
echo "✅ Elasticsearch is ready!"

# Wait for Kibana
echo "Waiting for Kibana..."
until curl -f http://localhost:5601/api/status > /dev/null 2>&1; do
    echo "Kibana not ready yet..."
    sleep 5
done
echo "✅ Kibana is ready!"

# Run migrations
echo "📊 Running database migrations..."
docker-compose exec django python manage.py migrate

# Collect static files
echo "📁 Collecting static files..."
docker-compose exec django python manage.py collectstatic --noinput

# Setup Kibana
echo "📈 Setting up Kibana..."
./setup-kibana.sh

echo ""
echo "🎉 Core WAF Services are now running!"
echo ""
echo "🌐 Access your services:"
echo "   Main App: http://localhost:8000"
echo "   Admin:    http://localhost:8000/admin/"
echo "   Kibana:   http://localhost:5601"
echo ""
echo "📊 Service Status:"
docker-compose ps
echo ""
echo "💡 To start Caddy proxies later (after fixing config):"
echo "   docker-compose up -d caddy-l7 caddy-l4"