-- Query 1: ECS Error Spike Detection
-- Detects error spikes in ECS application logs
-- Use with log group: /ecs/capstone-7-app

fields @timestamp, @message
| filter @message like /ERROR/ or @message like /error/ or @message like /Error/
| stats count() as error_count by bin(5m)
| sort error_count desc

---

-- Query 2: Top Error Messages
-- Shows the most common error messages
-- Use with log group: /ecs/capstone-7-app

fields @timestamp, @message
| filter @message like /ERROR/
| stats count() as count by @message
| sort count desc
| limit 20

---

-- Query 3: Request Latency Analysis
-- Analyzes HTTP request patterns and status codes
-- Use with log group: /ecs/capstone-7-app

fields @timestamp, @message
| filter @message like /GET/ or @message like /POST/
| parse @message /(?<method>\w+)\s+(?<path>\/\S+)\s+(?<status>\d+)/
| stats count() as requests, avg(status) as avg_status by path
| sort requests desc
