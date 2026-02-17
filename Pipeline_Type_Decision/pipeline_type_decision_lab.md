Pipeline Type Decision Lab

Fintech Startup – Data Platform Architecture

Data Flow 1: Transaction Fraud Detection
Pipeline Decision
Pipeline Type: Streaming
Architecture: Hybrid (Streaming ETL + ML serving)
Latency Target: Sub-second
Target System: Real-time model + secure event store (no raw PCI storage)

Justification
1. Why this pipeline type?
Fraud detection requires sub-second decisions
High volume: 500K/hour → spikes to 2M/hour
Business impact is immediate financial loss
Therefore: Streaming is mandatory
Batch is not acceptable.

2. Why this architecture?
PCI-DSS requires raw card data to be tokenized immediately
Raw card data must NOT be stored
Transformations must happen before persistence
This triggers Streaming ETL:
Tokenize card data
Enrich transaction
Send to fraud model
Store only masked data

3. Data Flow Description

Payment Gateway
→ Streaming ingestion (Kafka/Kinesis)
→ Real-time tokenization + validation
→ Feature engineering layer
→ Fraud ML model (real-time scoring)
→ Store masked transaction in secure event store

Failure Strategy
What fails?
Model service outage
Tokenization service failure
Message broker backlog

Recovery Plan:
Buffer events in Kafka with retention
Dead-letter queue for malformed events
Auto-scaling model service

Idempotency:
Use transaction_id as unique key
Ensure duplicate events don’t re-trigger fraud action

Trade-offs
Chose Streaming over Batch because fraud must be real-time.
Risk: High infrastructure complexity
Mitigation: Auto-scaling + monitoring + circuit breakers

Data Flow 2: Daily Financial Reporting
Pipeline Decision

Pipeline Type: Batch
Architecture: ETL
Latency Target: Daily
Target System: Data Warehouse

Justification
1. Why this pipeline type?
Nightly financial calculations
Must match to the penny
No need for real-time
Regulatory reporting → deterministic
Batch is correct.

2. Why ETL?
Calculations must be auditable and controlled
Complex interest + fee logic
Transform before loading ensures:
Validation
Reconciliation
Audit logs
Warehouse should only store verified results.

3. Data Flow Description

Core Banking (PostgreSQL)
→ Nightly extract
→ Deterministic transformation engine
→ Validation + reconciliation
→ Load to warehouse
→ CFO Dashboard

Failure Strategy
What fails?
Extract failure
Calculation mismatch
Partial load

Recovery Plan:
Re-run full batch (idempotent design)
Checkpointing + audit logs
Reconciliation reports

Idempotency:
Use batch_date partition
Overwrite partition safely

Trade-offs
Chose ETL over ELT for compliance control.
Risk: Longer processing window
Mitigation: Parallelized batch jobs

Data Flow 3: Customer 360 Profile
Pipeline Decision
Pipeline Type: Hybrid
Architecture: Hybrid (ETL + ELT)
Latency Target: Near real-time (minutes) + weekly batch enrichment
Target System: Data Lake + Warehouse

Justification
1. Why Hybrid pipeline?
Mixed sources (API + Kafka + DB)
Some data real-time (app events)
Some data periodic (CRM updates)
Marketing needs freshness but not sub-second
Hybrid is optimal.

2. Why Hybrid architecture?
GDPR compliance → PII must be controlled
Consent tracking required
Raw behavioral data preserved in lake
Aggregations in warehouse

Pre-load:
Consent validation
PII tagging
Post-load:
SQL joins
Profile aggregation

3. Data Flow Description

CRM + Kafka + Support DB
→ Ingestion layer
→ PII validation + consent check (ETL)
→ Raw storage in Data Lake
→ ELT transformations in Warehouse
→ Customer 360 table
→ Marketing / Product dashboards

Failure Strategy
What fails?
Consent mismatch
Event schema change
Join failures

Recovery Plan:
Schema validation
Rebuild profiles from raw lake data
Versioned transformations

Idempotency:
Customer_id-based upserts
Recomputable profiles

Trade-offs
Chose Hybrid over pure ELT due to GDPR.
Risk: Complexity of orchestration
Mitigation: Clear data contracts + orchestration tool

Data Flow 4: Application Logs
Pipeline Decision
Pipeline Type: Streaming
Architecture: ELT
Latency Target: Near real-time (seconds)
Target System: Log analytics system + Data Lake

Justification
1. Why Streaming?
SRE needs instant alerts
10M events/day
Delayed logs = slow incident response
Streaming required.

2. Why ELT?
Logs are exploratory
Minimal compliance
Transformations are filtering + indexing
Warehouse/log engine can scale
Load raw logs first → transform for dashboards.

3. Data Flow Description

Microservices
→ Fluentd
→ Streaming ingestion
→ Log analytics platform
→ Alert engine + dashboards

Failure Strategy
What fails?
Log ingestion delay
Indexing failure
Alerting misfire

Recovery Plan:
Buffer logs
Replay from broker
Redundant alert channels

Idempotency:
Trace ID used as deduplication key
Trade-offs
Chose ELT for flexibility
Risk: Storage cost of raw logs
Mitigation: Log retention policies

Data Flow 5: Partner Data Ingestion
Pipeline Decision
Pipeline Type: Batch
Architecture: ETL
Latency Target: Weekly
Target System: Data Warehouse

Justification
1. Why Batch?
Weekly SFTP file
50K rows
Quarterly reporting
No real-time need

2. Why ETL?
Data quality validation required
Partner NDA — strict access control
Schema validation before warehouse load
Transform before load.

3. Data Flow Description

Partner SFTP
→ Secure batch ingestion
→ Validation + schema checks
→ Transform + clean
→ Load to warehouse
→ BI reports

Failure Strategy
What fails?
Corrupted file
Missing file
Schema mismatch

Recovery Plan:
File validation step
Notify partner
Retry mechanism

Idempotency:
File versioning + checksum validation


Summary Architecture Table

| Data Flow              | Pipeline Type | Architecture | Latency          | Target            | Key Risk        |
| ---------------------- | ------------- | ------------ | ---------------- | ----------------- | --------------- |
| 1. Fraud Detection     | Streaming     | Hybrid       | Sub-second       | ML + Secure Store | System overload |
| 2. Financial Reporting | Batch         | ETL          | Daily            | Warehouse         | Audit failure   |
| 3. Customer 360        | Hybrid        | Hybrid       | Minutes + Weekly | Lake + Warehouse  | GDPR breach     |
| 4. Application Logs    | Streaming     | ELT          | Seconds          | Log system        | Log loss        |
| 5. Partner Data        | Batch         | ETL          | Weekly           | Warehouse         | Bad data load   |


Unified Platform Architecture

[Payment Gateway] → Streaming ETL → Fraud Model
[Core Banking]    → Batch ETL → Warehouse → CFO Dashboard
[CRM + App + DB]  → Hybrid ETL/ELT → Lake + Warehouse → Marketing
[Microservices]   → Streaming ELT → Log Analytics → SRE Alerts
[Partner SFTP]    → Batch ETL → Warehouse → BI Reports


Reflection Questions
1. Which data flow was hardest to decide? Why?

Customer 360 was hardest because it required balancing GDPR compliance with marketing flexibility and multiple source types. It required both real-time and batch components.

2. Where did compliance most influence your architecture?

Fraud Detection (PCI-DSS) and HR-style PII handling strongly forced ETL decisions. Compliance requirements often override performance preferences.

3. If you could use only ONE pipeline type (batch or streaming), which would you choose?

Streaming. Fintech companies rely heavily on real-time risk detection and operational visibility. Batch alone would introduce unacceptable business risk.

Final Architect Insight
This startup needs:
Real-time streaming core
Batch financial backbone
Data lake for recomputability
Warehouse for analytics
Strong compliance-first ETL gates
This is a modern hybrid fintech architecture.