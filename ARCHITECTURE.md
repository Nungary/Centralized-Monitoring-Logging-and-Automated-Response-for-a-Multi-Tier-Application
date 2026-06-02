# Architecture & Design Decisions

## System Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                         Internet Users                               │
│                    (HTTP Requests from Kenya)                        │
└────────────────────────┬────────────────────────────────────────────┘
                         │
                         ▼
              ┌──────────────────────┐
              │  Application Load    │
              │     Balancer         │
              │   (Port 80, 8080)    │
              │  + Health Checks     │
              └──────┬───────┬───────┘
                     │       │
        ┌────────────┘       └────────────┐
        ▼                                 ▼
┌───────────────────┐           ┌──────────────────┐
│   Web Tier (EC2)  │           │  App Tier (ECS)  │
│                   │           │                  │
│  ┌─────────────┐  │           │  ┌────────────┐  │
│  │ Instance 1  │  │           │  │  Task 1    │  │
│  │ Apache      │  │           │  │  httpd     │  │
│  │ CW Agent    │  │           │  │  + X-Ray   │  │
│  └─────────────┘  │           │  └────────────┘  │
│                   │           │                  │
│  ┌─────────────┐  │           │  ┌────────────┐  │
│  │ Instance 2  │  │           │  │  Task 2    │  │
│  │ Apache      │  │           │  │  httpd     │  │
│  │ CW Agent    │  │           │  │  + X-Ray   │  │
│  └─────────────┘  │           │  └────────────┘  │
└────────┬──────────┘           └────────┬─────────┘
         │                               │
         └───────────┬───────────────────┘
                     ▼
              ┌──────────────┐
              │  Data Tier   │
              │  RDS MySQL   │
              │              │
              │  Enhanced    │
              │  Monitoring  │
              │  (60s)       │
              └──────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│                    Observability & Automation Layer                  │
├─────────────────────────────────────────────────────────────────────┤
│                                                                       │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐          │
│  │  CloudWatch  │───▶│   Kinesis    │───▶│      S3      │          │
│  │     Logs     │    │  Firehose    │    │  (GZIP logs) │          │
│  └──────────────┘    └──────────────┘    └──────────────┘          │
│                                                                       │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐          │
│  │  CloudWatch  │───▶│    Alarms    │───▶│    Lambda    │          │
│  │   Metrics    │    │   (3 total)  │    │  Functions   │          │
│  └──────────────┘    └──────────────┘    └──────┬───────┘          │
│                                                   │                  │
│                                                   ▼                  │
│                                           ┌──────────────┐          │
│                                           │     SNS      │          │
│                                           │ Notifications│          │
│                                           └──────────────┘          │
│                                                                       │
│  ┌──────────────┐    ┌──────────────┐                               │
│  │    X-Ray     │───▶│  Service Map │                               │
│  │   Traces     │    │  (Latency)   │                               │
│  └──────────────┘    └──────────────┘                               │
│                                                                       │
│  ┌──────────────────────────────────────────────────────┐           │
│  │         CloudWatch Dashboard (4 Widgets)             │           │
│  │  ALB | ECS | RDS | Alarms                            │           │
│  └──────────────────────────────────────────────────────┘           │
│                                                                       │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Design Decisions

### 1. Multi-Tier Architecture

**Decision**: Separate web, application, and data tiers

**Rationale**:
- **Scalability**: Each tier can scale independently
- **Security**: Defense in depth with multiple security groups
- **Maintainability**: Changes to one tier don't affect others
- **Observability**: Clear separation makes monitoring easier

**Trade-offs**:
- Increased complexity vs. monolithic design
- More network hops (minimal latency impact)

---

### 2. Default VPC Usage

**Decision**: Use default VPC instead of creating custom VPC

**Rationale**:
- **Speed**: Faster deployment for capstone demonstration
- **Simplicity**: Pre-configured routing and internet gateway
- **Cost**: No NAT Gateway charges for private subnets
- **Security**: Still maintained through security groups

**Trade-offs**:
- Less control over IP addressing
- Shared with other default resources
- **Production Note**: Custom VPC recommended for production

---

### 3. ECS Fargate vs EC2 for App Tier

**Decision**: Use ECS Fargate instead of EC2 for application tier

**Rationale**:
- **Serverless**: No server management overhead
- **Scaling**: Built-in auto-scaling capabilities
- **Cost**: Pay only for running tasks
- **Patching**: AWS manages underlying infrastructure
- **X-Ray Integration**: Native support for X-Ray daemon sidecar

**Trade-offs**:
- Slightly higher cost per vCPU/GB vs. EC2
- Less control over underlying OS
- Cold start considerations (minimal for this workload)

---

### 4. CloudWatch Agent on EC2

**Decision**: Install CloudWatch Agent for custom metrics and logs

**Rationale**:
- **Custom Metrics**: Collect memory and disk metrics (not available by default)
- **Log Collection**: Stream Apache logs to CloudWatch
- **Unified Monitoring**: All metrics in one place
- **Automation**: Enables metric-based alarms and auto-remediation

**Configuration**:
- Namespace: `Capstone7/WebTier`
- Metrics: CPU_IDLE, MEM_USED, DISK_USED
- Logs: Apache access_log, error_log

---

### 5. RDS Enhanced Monitoring (60-second granularity)

**Decision**: Enable enhanced monitoring at 60-second intervals

**Rationale**:
- **Balance**: 60s provides good visibility without excessive cost
- **OS Metrics**: Access to memory, CPU, and process-level data
- **Troubleshooting**: Helps correlate app issues with DB performance
- **Compliance**: Meets observability requirements

**Trade-offs**:
- Cost: ~$0.02/hour vs. free standard monitoring
- **Alternative**: 1-second granularity available but 60x more expensive

---

### 6. Kinesis Firehose for Log Centralization

**Decision**: Use Kinesis Firehose instead of direct S3 logging

**Rationale**:
- **Buffering**: Batches logs before writing to S3 (cost optimization)
- **Transformation**: Can transform/filter logs before storage
- **Compression**: Built-in GZIP compression (reduces S3 costs by ~70%)
- **Partitioning**: Automatic date-based partitioning
- **Scalability**: Handles high-throughput log streams

**Configuration**:
- Buffer: 5 MB or 300 seconds (whichever comes first)
- Compression: GZIP
- Prefix: `logs/year=YYYY/month=MM/day=DD/`

**Trade-offs**:
- Slight delay (up to 5 minutes) vs. real-time
- Additional service to manage

---

### 7. Lambda for Automated Remediation

**Decision**: Use Lambda functions triggered by CloudWatch Alarms

**Rationale**:
- **Event-Driven**: Responds immediately to alarm state changes
- **Serverless**: No infrastructure to manage
- **Cost**: Pay only for execution time
- **Flexibility**: Can perform any remediation action (restart, tag, notify)
- **Integration**: Native CloudWatch Alarm integration

**Functions**:
1. **Restart ECS Task**: Stops unhealthy task (ECS auto-restarts)
2. **Notify On-Call**: Formats detailed alert messages
3. **Tag EC2**: Marks instances for investigation

---

### 8. Three CloudWatch Alarms Strategy

**Decision**: Create 3 specific alarms instead of many generic ones

**Rationale**:
- **Focus**: Cover critical failure modes (CPU, errors, 5xx)
- **Alert Fatigue**: Avoid overwhelming operations team
- **Actionable**: Each alarm has clear remediation path
- **Cost**: Alarms are free for first 10, minimal cost after

**Alarm Design**:
| Alarm | Threshold | Evaluation | Rationale |
|-------|-----------|------------|-----------|
| ECS CPU > 80% | 80% | 5 minutes | Prevents task crashes |
| ALB 5xx > 5 | 5 errors | 5 minutes | Detects backend failures |
| ErrorCount > 10 | 10 errors | 5 minutes | Catches app-level issues |

---

### 9. X-Ray Daemon as ECS Sidecar

**Decision**: Deploy X-Ray daemon as sidecar container in ECS task

**Rationale**:
- **Distributed Tracing**: Track requests across services
- **Latency Analysis**: Identify slow components
- **Service Map**: Visualize application architecture
- **Best Practice**: Sidecar pattern for shared functionality

**Configuration**:
- Container: `public.ecr.aws/xray/aws-xray-daemon:latest`
- Port: 2000/udp
- Resources: 128 CPU, 256 MB memory

**Limitation**: Application needs X-Ray SDK instrumentation for full tracing (httpd container doesn't have this, so traces are limited)

---

### 10. CloudWatch Dashboard Design

**Decision**: Single dashboard with 4 widgets covering all tiers

**Rationale**:
- **Single Pane of Glass**: Operations team sees everything at once
- **Correlation**: Easy to spot cross-tier issues
- **Simplicity**: Not overwhelming with too many metrics
- **Actionable**: Shows metrics that matter for troubleshooting

**Widget Selection**:
1. **ALB**: RequestCount, 5XX errors (user-facing health)
2. **ECS**: CPU, Memory (app tier health)
3. **RDS**: Connections, Latency (database health)
4. **Alarms**: All alarm states (incident awareness)

---

## Security Architecture

### Network Security
- **ALB**: Public-facing, accepts HTTP from internet
- **EC2/ECS**: Private, accepts traffic only from ALB
- **RDS**: Private, accepts MySQL only from EC2/ECS
- **No SSH**: Instances managed via Systems Manager Session Manager

### IAM Security
- **Least Privilege**: Each role has minimum required permissions
- **Service Principals**: Roles trust only specific AWS services
- **No Hardcoded Credentials**: All access via IAM roles

### Data Security
- **Encryption in Transit**: HTTPS for ALB (can be enabled)
- **Encryption at Rest**: S3 logs can use SSE-S3
- **Log Retention**: CloudWatch logs retained indefinitely (can be adjusted)

---

## Cost Optimization

### Strategies Implemented
1. **GZIP Compression**: Reduces S3 storage by ~70%
2. **Firehose Buffering**: Reduces S3 PUT requests
3. **60s Monitoring**: Balance between visibility and cost
4. **t2/t3 Instances**: Burstable instances for variable workloads
5. **Single-AZ RDS**: No Multi-AZ for non-production

### Monthly Cost Breakdown
- **Compute**: ~$32 (EC2 + ECS)
- **Database**: ~$15 (RDS)
- **Networking**: ~$20 (ALB)
- **Monitoring**: ~$10 (CloudWatch)
- **Storage**: ~$1 (S3 logs)
- **Total**: ~$78/month

---

## Scalability Considerations

### Horizontal Scaling
- **EC2**: Add more instances to target group
- **ECS**: Increase desired task count (auto-scaling possible)
- **RDS**: Read replicas for read-heavy workloads

### Vertical Scaling
- **EC2**: Change instance type (requires restart)
- **ECS**: Adjust task CPU/memory (requires new task definition)
- **RDS**: Change instance class (brief downtime)

### Auto-Scaling (Not Implemented)
- **ECS**: Target tracking on CPU/memory
- **EC2**: Auto Scaling Group with CloudWatch metrics
- **RDS**: Aurora Serverless for automatic scaling

---

## High Availability

### Current Setup
- **ALB**: Distributes across 3 availability zones
- **EC2**: 2 instances in different AZs
- **ECS**: 2 tasks (can be in different AZs)
- **RDS**: Single-AZ (cost optimization)

### Production Recommendations
- **RDS**: Enable Multi-AZ for automatic failover
- **EC2**: Auto Scaling Group with min 2 instances
- **ECS**: Service auto-scaling based on CPU/memory
- **Route 53**: Health checks and failover routing

---

## Monitoring Strategy

### Three Pillars of Observability

#### 1. Metrics (CloudWatch Metrics)
- **System**: CPU, memory, disk, network
- **Application**: Request count, latency, errors
- **Business**: Custom metrics (if needed)

#### 2. Logs (CloudWatch Logs)
- **Application**: Apache access/error logs
- **Container**: ECS stdout/stderr
- **Database**: RDS error, slow query, general logs
- **Centralized**: Kinesis Firehose → S3

#### 3. Traces (X-Ray)
- **Distributed**: Track requests across services
- **Latency**: Identify slow components
- **Errors**: Pinpoint failure points

---

## Incident Response Workflow

```
1. Issue Occurs (e.g., High CPU)
         ↓
2. CloudWatch Alarm Triggers
         ↓
3. Lambda Function Executes
         ↓
4. Remediation Action (e.g., Restart Task)
         ↓
5. SNS Notification Sent
         ↓
6. Dashboard Shows Incident
         ↓
7. On-Call Engineer Reviews
         ↓
8. Root Cause Analysis (Logs Insights)
```

---

## Future Enhancements

### Short-term
- [ ] Enable HTTPS on ALB with ACM certificate
- [ ] Implement ECS auto-scaling
- [ ] Add CloudWatch Contributor Insights
- [ ] Create CloudWatch Synthetics for endpoint monitoring

### Medium-term
- [ ] Migrate to custom VPC with private subnets
- [ ] Implement AWS WAF on ALB
- [ ] Add CloudWatch Application Insights
- [ ] Create CloudWatch Anomaly Detection

### Long-term
- [ ] Implement AWS Observability Accelerator
- [ ] Add OpenTelemetry instrumentation
- [ ] Integrate with third-party APM (Datadog, New Relic)
- [ ] Implement chaos engineering for resilience testing

---

**Architecture Status**: ✅ Production-ready for observability demonstration
