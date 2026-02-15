File Format Selection for Data Platform Use Cases

Step 1: Scenario Analysis
Scenario 1: Streaming Clickstream Ingestion
Key Characteristics

Write pattern: High-volume streaming (millions/hour)
Read pattern: Exploratory, near real-time
Schema: May evolve
Performance: Fast writes + immediate query
Interoperability: Debuggable, human-readable
Cost concern: Secondary to ingestion speed

Format Evaluation
CSV
Pros:
Simple
Human-readable
Widely supported

Cons:
No schema evolution
Poor for nested event data
No efficient streaming semantics

JSON
Pros:
Schema flexible
Handles nested event data
Human-readable
Natural for event streams
Works well with streaming systems

Cons:
Larger storage footprint
Slower analytics queries
No column pruning

Parquet
Pros:
Excellent analytics performance
Column pruning + pushdown
Compression

Cons:
Not ideal for continuous streaming writes
Not human-readable
Schema evolution more controlled

ORC

Pros:
Strong compression
Good for analytics

Cons:
Not ideal for streaming ingestion
Less flexible than JSON
Not human-readable

✅ Selected Format: JSON
Primary Justification
Streaming + schema evolution + debugging requirements make JSON the best fit.
Trade-offs:
Larger storage
Slower analytical performance
Likely converted later to Parquet for analytics

Scenario 2: Daily Sales Analytics
Key Characteristics

Write pattern: Daily batch
Read pattern: Heavy analytics (aggregations)
Schema: Stable
Performance: Critical
Cost: Critical
Wide table: 50+ columns

Format Evaluation
CSV:
No column pruning
Large scan cost
Poor compression
→ Not suitable

JSON:
Flexible but inefficient for analytics
Large storage footprint
→ Not suitable

Parquet
Columnar
Column pruning
Predicate pushdown
Excellent compression
Optimized for analytical queries

ORC:
Similar to Parquet
Strong compression
Often optimized for Hive ecosystems

Selected Format: Parquet
Primary Justification
Analytics-heavy workload needing 5–10 columns out of 50+.
Column pruning dramatically reduces I/O.

Trade-offs
Not human-readable
Requires specialized tools

ORC would also work, but Parquet has broader ecosystem support.

Scenario 3: Data Exchange with External Partners
Key Characteristics

Write pattern: Batch export
Read pattern: External consumption
Schema: Stable
Interoperability: Critical
Human readability: Important
Volume: Moderate

Format Evaluation
CSV:

Universally supported
Human-readable
Easy to open in Excel
Simple structure

JSON:
Widel supported
Good for nested data
Slightly less spreadsheet-friendly

Parquet:
Not human-readable

Requires specialized tools
→ Poor interoperability

ORC
Even less widely supported outside Hadoop ecosystem

Selected Format: CSV
Primary Justification
Universal compatibility and simplicity.
Trade-offs
Larger storage
No compression
No schema enforcement
JSON could work if nested data required.

Scenario 4: Ad-Hoc Analyst Exploration
Key Characteristics
Write pattern: Small-medium files
Read pattern: Unpredictable exploration
Schema: Flexible
Human readability: Important
Quick iteration: Required
Format Evaluation
CSV:

Easy to inspect
Open in Excel
Simple structure

JSON
Flexible schema
Good for semi-structured exploration
Human-readable

Parquet
Fast for analytics
Not human-readable
Harder to inspect manually

ORC
Similar to Parquet
Less ideal for quick exploration
Selected Format: JSON
Primary Justification

Flexible schema + ability to inspect raw structure.
Trade-offs
Larger files
Slower analytical performance
If exploration matures into production analytics → convert to Parquet.

Scenario 5: Long-Term Archival Storage
Key Characteristics
Write pattern: Append-only
Read pattern: Rare analytical queries
Schema: Stable
Primary concern: Storage cost
Compression: Critical
Format Evaluation
CSV

Poor compression
Large storage footprint
→ Not ideal

JSON
Even larger than CSV
→ Not ideal

Parquet
Excellent compression

Columnar
Efficient for occasional analytics

ORC
Very strong compression
Optimized for storage + analytics

Selected Format: ORC
Primary Justification
Maximum compression and storage efficiency.

Trade-offs
Requires specialized tools
Not human readable
Parquet would also work; ORC may offer slightly better compression in some cases

Step 2: Decision Table

| Scenario              | Selected Format | Primary Justification        | Read Pattern   | Write Pattern | Schema   | Performance      | Interoperability | Trade-offs        |
| --------------------- | --------------- | ---------------------------- | -------------- | ------------- | -------- | ---------------- | ---------------- | ----------------- |
| Streaming Clickstream | JSON            | Streaming + schema evolution | Exploratory    | Continuous    | Evolving | Fast writes      | Good             | Large size        |
| Daily Sales Analytics | Parquet         | Analytical performance       | Aggregations   | Batch         | Stable   | Very high        | Moderate         | Not readable      |
| Data Exchange         | CSV             | Universal compatibility      | External use   | Batch export  | Stable   | Moderate         | Excellent        | No compression    |
| Ad-Hoc Exploration    | JSON            | Flexible + readable          | Exploratory    | Small files   | Flexible | Moderate         | Good             | Larger files      |
| Long-Term Archive     | ORC             | Maximum compression          | Rare analytics | Append-only   | Stable   | High when needed | Low              | Specialized tools |

Step 3: Detailed Justifications

Format: Streaming Clickstream
Selected Format: JSON
Read/Write Patterns
High-frequency streaming writes

Immediate querying
JSON handles streaming ingestion well.
Parquet/ORC are better for batch writes.

Schema Evolution
Events may add new fields
JSON handles dynamic schema easily.

Performance
Fast ingestion
Not optimized for analytics (acceptable initially)
Interoperability
Easy debugging
Log-friendly

Trade-offs
Larger storage
Will likely convert to Parquet later

Format: Daily Sales Analytics
Selected Format: Parquet
Read/Write Patterns

Batch writes

Heavy analytical reads
Parquet excels here.
Schema
Stable schema fits well

Performance
Column pruning
Predicate pushdown
Compression
Interoperability
Requires analytics tools

Trade-offs
Not human-readable

Format: Data Exchange
Selected Format: CSV
Read/Write Patterns

External consumption
Schema
Stable and simple

Performance
Moderate volumes acceptable
Interoperability
Universally supported

Trade-offs
Larger size
No schema enforcement

Format: Ad-Hoc Exploration
Selected Format: JSON
Read/Write Patterns

Unpredictable queries
Schema
Flexible structure ideal

Performance
Acceptable for small-medium datasets

Trade-offs
Not optimized for heavy analytics

Format: Long-Term Archive
Selected Format: ORC
Read/Write Patterns

Append-only
Rare analytical queries

Schema
Stable

Performance
Strong compression

Efficient scanning when needed

Trade-offs
Less interoperable

Step 4: Decision Framework
Format Selection Decision Tree

What is the primary access pattern?
Analytical queries → Parquet, ORC
Exploratory / flexible → JSON
External sharing → CSV

What is the write pattern?
Streaming → JSON
Batch → Parquet, ORC
Append-only → Parquet, ORC

Is schema evolution needed?
Yes → JSON, Parquet
No → CSV, Parquet, ORC

What are interoperability requirements?
Universal → CSV, JSON

Specialized tools OK → Parquet, ORC

What is the primary concern?
Storage cost → ORC, Parquet
Query performance → Parquet
Human readability → CSV, JSON

Takeaway:
JSON is best for streaming + flexibility.
Parquet dominates analytical workloads.
CSV wins for interoperability.
ORC is excellent for compressed archival storage.
Real-world systems often use multiple formats across stages.