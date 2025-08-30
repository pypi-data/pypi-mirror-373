# Monitoring & Observability

!!! warning "Beta Software Notice"  

    Robutler is currently in **beta stage**. While the core functionality is stable and actively used, APIs and features may change. We recommend testing thoroughly before deploying to critical environments.

## Overview

Robutler V2 provides comprehensive monitoring and observability features for production deployments. This includes metrics collection, health checks, performance monitoring, and integration with popular observability platforms.

LLM and tool usage are recorded in `context.usage` and can be exported to your analytics pipeline (e.g., for cost dashboards). Payment charging reads from this same source, so you get both operational and financial visibility.

## Health Checks

The server exposes health check endpoints for monitoring service availability:

```bash
# Basic health check
curl http://localhost:8000/health

# Detailed health status
curl http://localhost:8000/health/detailed
```

## Metrics Collection

### Prometheus Metrics

Robutler exposes Prometheus-compatible metrics at `/metrics`:

```bash
curl http://localhost:8000/metrics
```

Key metrics include:
- Request count and latency
- Agent execution times
- Skill performance metrics
- Memory usage and cache statistics
- Error rates and types

### Custom Metrics

You can add custom metrics in your agents and skills:

```python
from robutler.monitoring import metrics

# Counter metric
metrics.increment('custom_operation_count', tags={'operation': 'data_processing'})

# Timing metric
with metrics.timer('custom_operation_duration'):
    # Your operation here
    pass
```

## Structured Logging

Robutler uses structured logging with configurable output formats:

```python
from robutler.utils.logging import get_logger

logger = get_logger('my_agent')
logger.info("Processing request", extra={
    'user_id': user_id,
    'operation': 'chat_completion',
    'model': 'gpt-4'
})
```

## Performance Monitoring

### Agent Performance

Monitor agent execution times and success rates:

```python
# Built-in performance tracking
@performance_monitor
async def my_agent_method(self, context):
    # Method implementation
    pass
```

### Skill Performance

Track individual skill performance:

```python
from robutler.monitoring import track_skill_performance

@track_skill_performance
async def my_skill_method(self, context):
    # Skill implementation
    pass
```

## Alerting Integration

### Webhook Alerts

Configure webhook alerts for critical events:

```yaml
monitoring:
  alerts:
    webhooks:
      - url: "https://your-webhook-url.com"
        events: ["error", "performance_degradation"]
        threshold:
          error_rate: 0.05  # 5% error rate
          response_time: 5000  # 5 seconds
```

### Email Notifications

Set up email notifications for system events:

```yaml
monitoring:
  email:
    smtp_host: "smtp.gmail.com"
    smtp_port: 587
    username: "alerts@yourcompany.com"
    password: "your-app-password"
    recipients: ["admin@yourcompany.com"]
```

## Production Deployment Monitoring

### Docker Container Monitoring

When deploying with Docker, use these best practices:

```dockerfile
# Health check in Dockerfile
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1
```

### Kubernetes Monitoring

Example Kubernetes monitoring configuration:

```yaml
apiVersion: v1
kind: Service
metadata:
  name: robutler-metrics
  labels:
    app: robutler
spec:
  ports:
  - name: metrics
    port: 8000
    targetPort: 8000
  selector:
    app: robutler
  
---
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: robutler-metrics
spec:
  selector:
    matchLabels:
      app: robutler
  endpoints:
  - port: metrics
    path: /metrics
```

## Debugging and Troubleshooting

### Debug Mode

Enable debug logging for troubleshooting:

```bash
# Environment variable
export ROBUTLER_LOG_LEVEL=DEBUG

# Or in configuration
ROBUTLER_LOG_LEVEL=DEBUG robutler serve
```

### Request Tracing

Enable request tracing to follow request flows:

```python
from robutler.monitoring import enable_tracing

# Enable distributed tracing
enable_tracing(
    service_name="robutler-agent",
    jaeger_endpoint="http://jaeger:14268/api/traces"
)
```

## Configuration Reference

Complete monitoring configuration example:

```yaml
monitoring:
  enabled: true
  
  metrics:
    enabled: true
    endpoint: "/metrics"
    collect_interval: 10  # seconds
    
  logging:
    level: "INFO"
    format: "json"
    output: "stdout"
    
  health_checks:
    enabled: true
    endpoint: "/health"
    detailed_endpoint: "/health/detailed"
    
  tracing:
    enabled: false
    service_name: "robutler"
    jaeger_endpoint: "http://localhost:14268/api/traces"
    
  alerts:
    enabled: true
    email:
      smtp_host: "smtp.gmail.com"
      smtp_port: 587
    webhooks:
      - url: "https://your-webhook.com"
        events: ["error", "performance"]
```

## Best Practices

1. **Set up proper alerting** for production deployments
2. **Monitor key metrics** like response time, error rate, and resource usage
3. **Use structured logging** for better debugging and analysis
4. **Implement health checks** for load balancer integration
5. **Enable tracing** for complex multi-agent workflows
6. **Regular monitoring review** to identify performance patterns

For more advanced monitoring setups and enterprise features, contact our support team. 