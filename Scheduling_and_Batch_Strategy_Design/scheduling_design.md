Part 1 – Cron Expression Answers
Cron Syntax Explanation
┌───────── minute (0-59)
│ ┌───────── hour (0-23)
│ │ ┌───────── day of month (1-31)
│ │ │ ┌───────── month (1-12)
│ │ │ │ ┌───────── day of week (0-6, Sun=0)
│ │ │ │ │
* * * * *


Each position defines when the job runs:
Minute
Hour
Day of month
Month
Day of week

Cron Expression Answers

| # | Requirement           | Cron Expression | Explanation                             |
| - | --------------------- | --------------- | --------------------------------------- |
| 1 | Daily at 2 AM         | `0 2 * * *`     | Runs at minute 0, hour 2, every day     |
| 2 | Hourly at :15         | `15 * * * *`    | Runs at minute 15 of every hour         |
| 3 | Monday 6 AM           | `0 6 * * 1`     | Runs at 6:00 AM every Monday            |
| 4 | 1st of month midnight | `0 0 1 * *`     | Runs at midnight on day 1 of each month |
| 5 | Every 15 min          | `*/15 * * * *`  | Runs every 15 minutes                   |
| 6 | Weekdays 8 AM         | `0 8 * * 1-5`   | Runs at 8 AM Monday–Friday              |


Part 2 – Pipeline Scheduling Design
Pipeline 1: Nightly Warehouse Refresh
Scheduling Strategy: Dependency-aware
Schedule/Trigger:
Trigger after PostgreSQL backup completes (event or sensor)
Must complete before 6 AM
Justification:
Backup completion time varies (around 1 AM), so fixed cron at 2 AM is risky.
Dependency-aware scheduling ensures refresh starts only when backup is done.

Failure handling:
Retry up to 3 times.
Safe to re-run if idempotent (overwrite partitions or full reload).

Pipeline 2: Hourly Clickstream Aggregation
Scheduling Strategy: Event-based
Schedule/Trigger:
Trigger when new hourly S3 file appears
Wait until file stable (after :10)

Justification:
Files arrive between :05 and :10 — cron at :00 risks partial data.
Event-based ensures file exists before processing.
Failure handling:
Retry on failure.
Idempotent by partitioning on hour.

Pipeline 3: Financial Close Pipeline
Scheduling Strategy: Dependency-aware (DAG)
Schedule/Trigger:
Cron: 0 0 1 * * (1st of month)
Steps chained in DAG:
Extract → Validate → Calculate → Report → Email

Justification:
Multi-step workflow with strict order.
Cannot run steps independently.
Failure handling:
If any step fails, stop downstream.
Safe re-run using partition-based logic (month partition).

Pipeline 4: Partner File Ingestion
Scheduling Strategy: Event-based
Schedule/Trigger:
Trigger when file appears on SFTP
Use file sensor or webhook

Justification:
Upload timing unpredictable.
Polling with cron wastes resources.
Failure handling:
Move file to processed folder after success.
Idempotent by tracking processed file names.

Pipeline 5: ML Feature Pipeline
Scheduling Strategy: Dependency-aware
Schedule/Trigger:
Trigger after Pipeline 1 completes successfully.

Justification:
Requires fresh warehouse data.
Cron at fixed time risks stale data.
Failure handling:
Retry automatically.
Rebuild features using overwrite strategy.

Pipeline 6: Data Quality Checks
Scheduling Strategy: Dependency-aware
Schedule/Trigger:
Runs AFTER each pipeline completes.
Justification:
Must validate output of every pipeline.
Time-based scheduling would miss failures.
Failure handling:
Send alert on failure.
Does not block upstream but flags issues.

Part 3 – Anti-Pattern Identification
Anti-Pattern 1
What's wrong:
Chaining pipelines using separate cron schedules.

Risk:
If Pipeline A runs late, B and C still execute and process incomplete data.

Fix:
Use dependency-aware DAG orchestration (Airflow, Prefect, etc.)
B depends on A, C depends on B.

Anti-Pattern 2
What's wrong:
Polling every 5 minutes for a weekly file.

Risk:
Wasted compute and unnecessary load.

Fix:
Use event-based trigger (SFTP sensor or webhook).

Anti-Pattern 3
What's wrong:
Warehouse refresh scheduled at midnight while backup runs 11 PM–1 AM.

Risk:
Reading inconsistent or locked data.

Fix:
Trigger refresh AFTER backup completes (dependency-aware scheduling).

Part 4 – Pipeline Dependency DAG
## Pipeline Dependency DAG

[Pipeline 1: Warehouse Refresh]
        |
        ├──→ [Pipeline 5: ML Features]
        |           |
        |           └──→ [ML Scoring Job]
        |
        └──→ [Pipeline 6: Data Quality Checks]

[Pipeline 2: Clickstream Aggregation]
        |
        └──→ [Pipeline 6: Data Quality Checks]

[Pipeline 3: Financial Close]
    (Extract) → (Validate) → (Calculate) → (Report) → (Email)
        |
        └──→ [Pipeline 6: Data Quality Checks]

[Pipeline 4: Partner Ingestion]
        |
        └──→ [Pipeline 6: Data Quality Checks]

Final Summary

This architecture:
Uses cron only where appropriate
Uses event-based triggers for unpredictable data arrival
Uses dependency-aware orchestration for multi-step workflows
Avoids time-based chaining anti-patterns
Ensures idempotency and safe re-runs
Provides clean DAG structure