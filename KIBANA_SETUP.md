# Kibana Configuration for WAF Application

This document provides comprehensive instructions for configuring and using Kibana with your WAF application.

## Overview

Kibana is configured to work with Elasticsearch to provide real-time visualization and analysis of WAF logs and analytics data. The setup includes:

- **Kibana 8.11.0** - Latest stable version
- **Elasticsearch 8.11.0** - Compatible version
- **Custom Configuration** - Optimized for WAF monitoring
- **Pre-configured Dashboards** - Ready-to-use security and performance dashboards
- **Index Patterns** - Pre-defined for WAF logs and analytics

## Quick Start

### 1. Start the Services

```bash
# Development environment
docker-compose up -d elasticsearch kibana

# Production environment
docker-compose -f docker-compose.prod.yml up -d elasticsearch kibana
```

### 2. Wait for Services to be Ready

```bash
# Check Elasticsearch health
curl http://localhost:9200/_cluster/health

# Check Kibana status
curl http://localhost:5601/api/status
```

### 3. Run the Setup Script

```bash
./setup-kibana.sh
```

This script will:
- Create index patterns for WAF logs and analytics
- Set up sample data for testing
- Configure basic dashboards

### 4. Access Kibana

Open your browser and navigate to: `http://localhost:5601`

## Configuration Files

### Kibana Configuration (`kibana.yml`)

The main Kibana configuration file includes:

- **Server Settings**: Host, port, and performance optimizations
- **Elasticsearch Connection**: Timeout and retry configurations
- **Security**: Disabled for development (enable for production)
- **Logging**: Structured logging configuration
- **WAF-specific Settings**: Custom configurations for WAF monitoring

### Docker Compose Configuration

Both `docker-compose.yml` and `docker-compose.prod.yml` include:

- **Volume Mounting**: Custom configuration and data persistence
- **Environment Variables**: Kibana-specific settings
- **Health Checks**: Automated service monitoring
- **Dependencies**: Proper startup order with Elasticsearch

## Index Patterns

### WAF Logs (`waf-logs-*`)

This index pattern captures real-time WAF request logs:

**Fields:**
- `@timestamp` - Request timestamp
- `client_ip` - Client IP address
- `request_method` - HTTP method (GET, POST, etc.)
- `request_uri` - Requested URI
- `response_status` - HTTP response status
- `rule_matched` - WAF rule that triggered
- `threat_level` - Threat severity (low, medium, high, critical)
- `site_id` - Protected site identifier
- `user_agent` - Client user agent
- `response_time` - Request processing time

### WAF Analytics (`waf-analytics-*`)

This index pattern stores aggregated analytics data:

**Fields:**
- `@timestamp` - Analytics timestamp
- `site_id` - Site identifier
- `total_requests` - Total request count
- `blocked_requests` - Blocked request count
- `response_time_avg` - Average response time
- `top_threats` - Most common threat types
- `geo_location` - Geographic data

## Dashboards

### Security Dashboard

**Purpose**: Real-time security monitoring and threat analysis

**Panels:**
- Threat Level Distribution (Pie Chart)
- Requests Over Time (Line Chart)
- Top Blocked IPs (Table)
- Response Status Codes (Pie Chart)
- Top Attack Patterns (Table)

### Performance Dashboard

**Purpose**: WAF performance metrics and response time analysis

**Panels:**
- Response Time Trend (Line Chart)
- Request Volume (Histogram)
- Average Response Time (Metric)
- Total Requests (Metric)
- Blocked Requests (Metric)

## Advanced Configuration

### Production Security

For production environments, enable security:

```yaml
# In kibana.yml
xpack.security.enabled: true
xpack.encryptedSavedObjects.encryptionKey: "your-32-character-encryption-key"
```

### Custom Visualizations

Create custom visualizations for specific WAF metrics:

1. Go to **Visualize Library** in Kibana
2. Click **Create visualization**
3. Choose visualization type
4. Select index pattern (`waf-logs-*` or `waf-analytics-*`)
5. Configure aggregations and metrics

### Alerting

Set up alerts for security events:

1. Go to **Stack Management > Rules and Connectors**
2. Create alert rules for:
   - High threat level detections
   - Unusual traffic patterns
   - Failed authentication attempts
   - Response time anomalies

### Data Retention

Configure index lifecycle management:

1. Go to **Stack Management > Index Lifecycle Policies**
2. Create policies for:
   - Hot phase: Recent data (7 days)
   - Warm phase: Older data (30 days)
   - Cold phase: Archived data (90 days)
   - Delete phase: Data cleanup (365 days)

## Troubleshooting

### Common Issues

**Kibana won't start:**
```bash
# Check logs
docker-compose logs kibana

# Verify Elasticsearch connection
curl http://elasticsearch:9200/_cluster/health
```

**Index patterns not found:**
```bash
# Re-run setup script
./setup-kibana.sh

# Manually create index pattern
curl -X POST "http://localhost:5601/api/saved_objects/index-pattern" \
  -H "Content-Type: application/json" \
  -H "kbn-xsrf: true" \
  -d '{"attributes":{"title":"waf-logs-*","timeFieldName":"@timestamp"}}'
```

**Performance issues:**
- Increase Elasticsearch heap size
- Optimize Kibana configuration
- Use index lifecycle management
- Monitor resource usage

### Log Locations

- **Kibana Logs**: `/usr/share/kibana/logs/kibana.log`
- **Elasticsearch Logs**: `/usr/share/elasticsearch/logs/`
- **Docker Logs**: `docker-compose logs kibana elasticsearch`

## Monitoring and Maintenance

### Health Checks

```bash
# Elasticsearch cluster health
curl http://localhost:9200/_cluster/health?pretty

# Kibana status
curl http://localhost:5601/api/status

# Index statistics
curl http://localhost:9200/_stats?pretty
```

### Backup and Restore

```bash
# Backup Kibana objects
curl -X GET "http://localhost:5601/api/saved_objects/_export" \
  -H "kbn-xsrf: true" > kibana-backup.json

# Restore Kibana objects
curl -X POST "http://localhost:5601/api/saved_objects/_import" \
  -H "kbn-xsrf: true" \
  -F file=@kibana-backup.json
```

## Integration with WAF Application

### Django Integration

The WAF application integrates with Elasticsearch/Kibana through:

1. **Logging App**: Sends WAF logs to Elasticsearch
2. **Analytics App**: Generates analytics data
3. **Dashboard App**: Provides Kibana links and embedded views

### Custom Dashboards

Create custom dashboards for specific WAF features:

1. **Site-specific Dashboards**: Filter by `site_id`
2. **Rule Performance**: Monitor specific WAF rules
3. **Geographic Analysis**: Use geo-location data
4. **Real-time Monitoring**: Live threat detection

## Best Practices

1. **Regular Monitoring**: Check dashboards daily
2. **Alert Configuration**: Set up meaningful alerts
3. **Data Retention**: Implement proper lifecycle policies
4. **Security**: Enable authentication in production
5. **Performance**: Monitor resource usage
6. **Backup**: Regular backup of configurations
7. **Updates**: Keep Kibana and Elasticsearch updated

## Support and Resources

- **Kibana Documentation**: https://www.elastic.co/guide/en/kibana/current/index.html
- **Elasticsearch Documentation**: https://www.elastic.co/guide/en/elasticsearch/reference/current/index.html
- **WAF Application Logs**: Check Django application logs for integration issues
- **Community Support**: Elastic Stack community forums

---

For additional help or custom configurations, refer to the Elastic Stack documentation or contact your system administrator.