# OpenTelemetry Metrics Configuration

## Reducing Metrics Volume

The OpenTelemetry wrapper now includes several configuration options to control metrics volume and prevent exceeding ingestion rate limits.

### Environment Variables

#### OTEL_METRICS_ENABLED
- Default: `true`
- Set to `false` to completely disable metrics collection
- Example: `export OTEL_METRICS_ENABLED=false`

#### OTEL_METRICS_SAMPLING_RATE
- Default: `0.1` (10% sampling)
- Range: 0.0 to 1.0
- Controls the percentage of non-critical metrics that are recorded
- Critical metrics (errors, root spans, entrypoints) are always recorded
- Example: `export OTEL_METRICS_SAMPLING_RATE=0.05` (5% sampling)

#### OTEL_METRIC_EXPORT_INTERVAL_MS
- Default: `30000` (30 seconds)
- Controls how often metrics are exported to the backend
- Increase this value to reduce the frequency of metric exports
- Example: `export OTEL_METRIC_EXPORT_INTERVAL_MS=60000` (1 minute)

### Sampling Behavior

The metrics system implements intelligent sampling:

1. **Always Recorded:**
   - Error metrics
   - Root span metrics
   - Entrypoint metrics
   - Active task counts

2. **Sampled Metrics:**
   - Input/output size histograms
   - Print statement counts
   - Non-critical task durations

### Example Configuration

To drastically reduce metrics volume:

```bash
# Disable metrics entirely
export OTEL_METRICS_ENABLED=false

# Or use aggressive sampling with longer export intervals
export OTEL_METRICS_SAMPLING_RATE=0.01  # 1% sampling
export OTEL_METRIC_EXPORT_INTERVAL_MS=300000  # 5 minutes
```

### Monitoring Metrics Volume

To check if you're still hitting rate limits, monitor:
- 429 errors from your metrics backend
- The `active_tasks` metric to ensure it's not growing unbounded
- Your backend's ingestion rate metrics

### Best Practices

1. Start with the default 10% sampling rate
2. If you still hit rate limits, reduce to 5% or 1%
3. Increase export interval if sampling alone isn't sufficient
4. Consider disabling metrics for non-production environments
5. Always keep metrics enabled for production entrypoints and error tracking