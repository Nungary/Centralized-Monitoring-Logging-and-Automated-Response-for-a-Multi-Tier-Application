# Observability-as-a-Service Capstone Project
---

## 📋 Project Overview

Production-grade observability system for a 3-tier AWS application with centralized monitoring, logging, and automated incident response.

**Architecture**: Web Tier (EC2) → App Tier (ECS Fargate) → Data Tier (RDS MySQL)


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

## ✅ Requirements Completed

| # | Requirement | Status |
|---|-------------|--------|
| 1 | Centralized Log & Metric Collection | ✅ Complete |
| 2 | Auditing & Analysis (Logs Insights + X-Ray) | ✅ Complete |
| 3 | Automated Monitoring & Event Management | ✅ Complete |
| 4 | Dashboards & Advanced Review | ✅ Complete |

---

## 🚀 Deployed Resources Summary

### Infrastructure
- **VPC**: (default VPC, 3 subnets)
- **Security Groups**: 4 groups (ALB, Web, ECS, RDS)
- **ALB**: `capstone-7-alb` with 2 target groups
- **EC2**: 2 instances with CloudWatch Agent
- **ECS**: Fargate cluster with 2 tasks + X-Ray daemon
- **RDS**: MySQL with enhanced monitoring (60s)

### Observability
- **CloudWatch Alarms**: 3 alarms (ECS CPU, ALB 5xx, ErrorCount)
- **Lambda Functions**: 3 automation functions
- **Kinesis Firehose**: Log centralization to S3
- **CloudWatch Dashboard**: 4 widgets (ALB, ECS, RDS, Alarms)
- **Log Groups**: `/ecs/capstone-7-app`, EC2 access/error logs


### 1. Infrastructure Components

**Security Groups**
- 4 security groups with proper ingress/egress rules
- ALB allows HTTP from internet
- Web/ECS tiers accept traffic from ALB only
- RDS accepts MySQL from Web and ECS tiers
  
<img width="1919" height="953" alt="Screenshot 2026-05-29 180237" src="https://github.com/user-attachments/assets/8026a031-230d-49d0-8721-dbb26c760671" />

**EC2 Instances**
![EC2 Instances](./screenshots/02-ec2-instances.png)
- 2 running instances: `capstone-7-web-1`, `capstone-7-web-2`
- CloudWatch Agent installed and running
- IAM role attached for CloudWatch permissions
  <img width="1919" height="956" alt="Screenshot 2026-05-29 182828" src="https://github.com/user-attachments/assets/9b3d641d-4137-44aa-8413-23ffa846671c" />


**Application Load Balancer**
- DNS name for public access
- Listeners on port 80 (web) and 8080 (ECS)
- Active and provisioning state
  
<img width="1919" height="962" alt="Screenshot 2026-05-29 182447" src="https://github.com/user-attachments/assets/e7f25914-bc1b-4c0f-9c4e-02aa93ca4a68" />

**Target Groups**
![Target Groups]
- Web target group: 2 healthy EC2 instances
- ECS target group: 2 healthy IP targets
  
<img width="1919" height="961" alt="Screenshot 2026-05-29 182903" src="https://github.com/user-attachments/assets/bdfda2c1-fff1-4589-b202-e75824f64774" />

**ECS Cluster & Service**
![ECS Cluster]
- Fargate cluster with active service
- 2 running tasks
- Service auto-scaling configured
- 
  <img width="1919" height="962" alt="Screenshot 2026-05-29 191644" src="https://github.com/user-attachments/assets/87b68b19-df41-4220-bba3-08bc7a35bdab" />


**ECS Task Definition**
- Container: httpd (application)
- Sidecar: X-Ray daemon for tracing
- CloudWatch Logs integration
  <img width="1919" height="957" alt="Screenshot 2026-05-29 184155" src="https://github.com/user-attachments/assets/ca796fb9-f73c-4801-ba5d-5968a04281af" />


**RDS Database**
- MySQL 8.4.8, db.t3.micro
- Multi-AZ disabled (cost optimization)
- Enhanced monitoring enabled
<img width="1919" height="958" alt="image" src="https://github.com/user-attachments/assets/2d0aa840-7c3b-4fad-9e5f-ce5af08535c7" />

---

### 2. Monitoring & Logging

**CloudWatch Dashboard**
- Widget 1: ALB RequestCount and 5XX errors
- Widget 2: ECS CPU and Memory utilization
- Widget 3: RDS connections and latency
- Widget 4: Alarm status (all OK)
  <img width="1919" height="848" alt="Screenshot 2026-05-29 202008" src="https://github.com/user-attachments/assets/99d12e62-7ead-4ba3-9fcb-a4ab7fc395ef" />


**CloudWatch Alarms**
- `capstone-7-ecs-high-cpu`: ECS CPU > 80%
- `capstone-7-alb-high-5xx`: ALB 5xx > 5
- `capstone-7-error-count-high`: Errors > 10 in 5min
  <img width="1919" height="956" alt="Screenshot 2026-05-29 192102" src="https://github.com/user-attachments/assets/2cd74e09-99b6-4353-a994-4038dc30e7b7" />


**CloudWatch Log Groups**
![Log Groups](./screenshots/10-log-groups.png)
- `/ecs/capstone-7-app`: ECS container logs
- `/aws/ec2/capstone-7/web/access`: Apache access logs
- `/aws/ec2/capstone-7/web/error`: Apache error logs
  <img width="1919" height="955" alt="image" src="https://github.com/user-attachments/assets/3a7d6081-0801-4fc9-9594-95d3ca24c405" />


**CloudWatch Logs Insights**
- Saved query: ECS Error Spike Detection
- Saved query: Top Error Messages
- Saved query: Request Latency Analysis
  <img width="1919" height="963" alt="Screenshot 2026-05-29 201207" src="https://github.com/user-attachments/assets/abefc546-eb1f-45f6-8654-3924d71978a1" />


**Kinesis Firehose**
- Delivery stream: `capstone-7-logs-stream`
- Destination: S3 bucket with GZIP compression
- Buffering: 5MB or 300 seconds
  <img width="1919" height="966" alt="Screenshot 2026-05-29 192326" src="https://github.com/user-attachments/assets/6f9954e5-38e8-4a9d-a9e2-ced7c36678ed" />


**S3 Centralized Logs**
![S3 Bucket](./screenshots/13-s3-logs.png)
- Bucket: `capstone-7-logs-430287290736`
- Partitioned by date: `logs/year=YYYY/month=MM/day=DD/`

**RDS Enhanced Monitoring**
![RDS Monitoring](./screenshots/14-rds-enhanced-monitoring.png)
- OS-level metrics: Free Memory, Active Memory, CPU
- 60-second granularity
- Monitoring role: `rds-monitoring-role`

**RDS Log Exports**
![RDS Logs](./screenshots/15-rds-log-exports.png)
- Error log: Enabled
- Slow query log: Enabled
- General log: Enabled
- Audit log: Enabled

---

### 3. Automation & Testing

**Lambda Functions**
![Lambda](./screenshots/16-lambda-functions.png)
- `capstone-7-restart-ecs-task`: Auto-restart failing tasks
- `capstone-7-notify-oncall`: Format alarm notifications
- `capstone-7-tag-ec2-investigate`: Tag instances for review

**Lambda Execution Logs**
![Lambda Logs](./screenshots/17-lambda-execution.png)
- CloudWatch logs showing successful task restart
- SNS notification sent
- Execution time and memory usage

**ECS Service Events**
![ECS Events](./screenshots/18-ecs-service-events.png)
- Task stopped by Lambda automation
- New task started automatically
- Service reached steady state

**SNS Email Notification**
![SNS](./screenshots/19-sns-notification.png)
- Email subscription confirmed
- Alarm notification received
- Detailed alert information

---

### 4. Application Testing

**Web Server Response (EC2)**
![Web 1](./screenshots/20-web-server-1.png)
![Web 2](./screenshots/21-web-server-2.png)
- Both EC2 instances serving traffic
- Load balanced by ALB
- Apache web server running

**ECS Application Response**
![ECS App](./screenshots/22-ecs-app-response.png)
- ECS service accessible on port 8080
- Container responding to requests

---

## 🧪 Testing Results

### Test 1: Lambda Auto-Remediation
```bash
aws lambda invoke --function-name capstone-7-restart-ecs-task --payload '{}' response.json
```
**Result**: ✅ Task restarted, SNS sent, logs captured

### Test 2: Metrics Collection
**Result**: ✅ EC2 custom metrics, ECS metrics, RDS enhanced monitoring all working

### Test 3: Log Centralization
**Result**: ✅ Logs flowing to CloudWatch → Firehose → S3 with GZIP compression

### Test 4: Dashboard
**Result**: ✅ All 4 widgets displaying real-time metrics

**📁 See [TESTING.md](./TESTING.md) for detailed test procedures**

---

## 📂 Supporting Documentation

- **[ARCHITECTURE.md](./ARCHITECTURE.md)** - Detailed architecture diagram and design decisions
- **[lambda/](./lambda/)** - Lambda function source code
  - `restart-ecs-task.py`
  - `notify-oncall.py`
  - `tag-ec2-investigate.py`
- **[configs/](./configs/)** - Configuration files
  - `cloudwatch-agent-config.json`
  - `ecs-task-definition.json`
  - `logs-insights-queries.sql`

---

## 🏆 Key Achievements

✅ **Multi-tier monitoring** across EC2, ECS, and RDS  
✅ **Centralized logging** with Kinesis Firehose → S3  
✅ **Automated incident response** via Lambda  
✅ **Real-time dashboards** for operations  
✅ **Cost-optimized** architecture (GZIP, appropriate sizing)

---

## 🧹 Cleanup

Cleanup done for all resource deletion to avoid ongoing charges.

---

