#!/bin/bash

# Kibana Setup Script for WAF Application
# This script sets up index patterns and dashboards in Kibana

set -e

KIBANA_URL="http://localhost:5601"
ELASTICSEARCH_URL="http://localhost:9200"

echo "🚀 Setting up Kibana for WAF Application..."

# Wait for Kibana to be ready
echo "⏳ Waiting for Kibana to be ready..."
until curl -f "$KIBANA_URL/api/status" > /dev/null 2>&1; do
    echo "Waiting for Kibana..."
    sleep 5
done

echo "✅ Kibana is ready!"

# Wait for Elasticsearch to be ready
echo "⏳ Waiting for Elasticsearch to be ready..."
until curl -f "$ELASTICSEARCH_URL/_cluster/health" > /dev/null 2>&1; do
    echo "Waiting for Elasticsearch..."
    sleep 5
done

echo "✅ Elasticsearch is ready!"

# Create WAF logs index pattern
echo "📊 Creating WAF logs index pattern..."
curl -X POST "$KIBANA_URL/api/saved_objects/index-pattern" \
  -H "Content-Type: application/json" \
  -H "kbn-xsrf: true" \
  -d '{
    "attributes": {
      "title": "waf-logs-*",
      "timeFieldName": "@timestamp"
    }
  }' || echo "Index pattern may already exist"

# Create WAF analytics index pattern
echo "📈 Creating WAF analytics index pattern..."
curl -X POST "$KIBANA_URL/api/saved_objects/index-pattern" \
  -H "Content-Type: application/json" \
  -H "kbn-xsrf: true" \
  -d '{
    "attributes": {
      "title": "waf-analytics-*",
      "timeFieldName": "@timestamp"
    }
  }' || echo "Index pattern may already exist"

# Create sample WAF logs index with mapping
echo "📝 Creating sample WAF logs index..."
curl -X PUT "$ELASTICSEARCH_URL/waf-logs-2024.01.01" \
  -H "Content-Type: application/json" \
  -d '{
    "mappings": {
      "properties": {
        "@timestamp": {
          "type": "date"
        },
        "client_ip": {
          "type": "ip"
        },
        "request_method": {
          "type": "keyword"
        },
        "request_uri": {
          "type": "keyword"
        },
        "response_status": {
          "type": "integer"
        },
        "rule_matched": {
          "type": "keyword"
        },
        "threat_level": {
          "type": "keyword"
        },
        "site_id": {
          "type": "keyword"
        },
        "user_agent": {
          "type": "text"
        },
        "response_time": {
          "type": "float"
        }
      }
    }
  }' || echo "Index may already exist"

# Create sample WAF analytics index with mapping
echo "📊 Creating sample WAF analytics index..."
curl -X PUT "$ELASTICSEARCH_URL/waf-analytics-2024.01.01" \
  -H "Content-Type: application/json" \
  -d '{
    "mappings": {
      "properties": {
        "@timestamp": {
          "type": "date"
        },
        "site_id": {
          "type": "keyword"
        },
        "total_requests": {
          "type": "long"
        },
        "blocked_requests": {
          "type": "long"
        },
        "response_time_avg": {
          "type": "float"
        },
        "top_threats": {
          "type": "keyword"
        },
        "geo_location": {
          "type": "geo_point"
        }
      }
    }
  }' || echo "Index may already exist"

# Insert sample data
echo "📄 Inserting sample WAF log data..."
curl -X POST "$ELASTICSEARCH_URL/waf-logs-2024.01.01/_doc" \
  -H "Content-Type: application/json" \
  -d '{
    "@timestamp": "'$(date -u +%Y-%m-%dT%H:%M:%S.%3NZ)'",
    "client_ip": "192.168.1.100",
    "request_method": "GET",
    "request_uri": "/api/users",
    "response_status": 200,
    "rule_matched": "none",
    "threat_level": "low",
    "site_id": "site-001",
    "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "response_time": 45.2
  }'

curl -X POST "$ELASTICSEARCH_URL/waf-logs-2024.01.01/_doc" \
  -H "Content-Type: application/json" \
  -d '{
    "@timestamp": "'$(date -u +%Y-%m-%dT%H:%M:%S.%3NZ)'",
    "client_ip": "10.0.0.50",
    "request_method": "POST",
    "request_uri": "/admin/login",
    "response_status": 403,
    "rule_matched": "sql_injection",
    "threat_level": "high",
    "site_id": "site-001",
    "user_agent": "curl/7.68.0",
    "response_time": 12.8
  }'

echo "📈 Inserting sample WAF analytics data..."
curl -X POST "$ELASTICSEARCH_URL/waf-analytics-2024.01.01/_doc" \
  -H "Content-Type: application/json" \
  -d '{
    "@timestamp": "'$(date -u +%Y-%m-%dT%H:%M:%S.%3NZ)'",
    "site_id": "site-001",
    "total_requests": 1250,
    "blocked_requests": 45,
    "response_time_avg": 89.5,
    "top_threats": ["sql_injection", "xss", "csrf"]
  }'

echo "🎉 Kibana setup completed successfully!"
echo "🌐 Access Kibana at: $KIBANA_URL"
echo "📊 Default index patterns created:"
echo "   - waf-logs-*"
echo "   - waf-analytics-*"
echo ""
echo "Next steps:"
echo "1. Open Kibana in your browser"
echo "2. Go to Stack Management > Index Patterns"
echo "3. Create visualizations and dashboards"
echo "4. Set up alerts for threat detection"