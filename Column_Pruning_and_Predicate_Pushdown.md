Step 1: Column Pruning:
Column pruning is an optimization where the query engine reads only the columns required by a query instead of reading the entire table

What it means in practice

If a table has 20 columns but a query selects only 3 columns, the engine reads only those 3 columns from disk.

This reduces:
Disk I/O
Memory usage
CPU usage
Query execution time

Concrete Example
Table:

orders(
  order_id,
  customer_id,
  order_date,
  region,
  product_id,
  amount,
  discount,
  tax,
  total_amount
)

Query:

SELECT order_id, amount
FROM orders;

The query needs only:
order_id
amount
The remaining 7 columns are unnecessary for this query.

Why columnar formats enable it:
Columnar formats such as Apache Parquet store data column by column, not row by row.
Columnar storage structure

Instead of storing data like:
Row1: 1,101,2024-01-01,East,500,10
Row2: 2,102,2024-01-02,West,300,5


It stores data as:

order_id:   [1,2]
customer_id:[101,102]
order_date: [...]
region:     [...]
amount:     [500,300]

Each column is physically stored separately.
How this enables selective reading:
Because columns are separate:
The engine can directly access only the required columns.
It does not need to scan unused columns.

So for:

SELECT order_id, amount FROM orders;
Only 2 column files are read.

Why row-based formats cannot

Row-based formats (like CSV) store data row by row:

1,101,2024-01-01,East,500,10
2,102,2024-01-02,West,300,5

To extract order_id and amount:
The entire row must be read.
All columns must be parsed.
Unneeded columns are discarded after reading.
I/O Implication

Even if the query needs 2 columns:
All 9 columns are read from disk.
Entire dataset is scanned.

This increases:
Disk I/O
Parsing overhead
Memory consumption

Example Scenario Analysis

Table schema has:

How many columns are in the table?
→ 9
Query needs:
How many columns does the query need?
→ 2
With columnar format:
How many columns are read?
→ 2
With row-based format:
How many columns are read?
→ 9
I/O savings with columnar
(9 - 2) / 9 = 78% reduction in column data read
Columnar format avoids reading 7 unnecessary columns.

Step 2: Predicate Pushdown
What predicate pushdown is
Define predicate pushdown

Predicate pushdown is an optimization where filtering conditions (WHERE clauses) are applied as early as possible during data scanning, instead of filtering after loading all data into memory.

What it means in practice
Instead of:
Reading entire dataset
Then filtering rows

The engine:
Uses metadata
Skips irrelevant data blocks
Reads only relevant portions

Concrete Example
Query:

SELECT order_id, amount
FROM orders
WHERE order_date = '2024-03-01';

Predicate:
order_date = '2024-03-01'

How Parquet metadata helps
Apache Parquet stores metadata per row group:
Min value
Max value
Row count
Null count

Example metadata for order_date:

| Row Group | Min Date   | Max Date   |
| --------- | ---------- | ---------- |
| RG1       | 2024-01-01 | 2024-01-31 |
| RG2       | 2024-02-01 | 2024-02-28 |
| RG3       | 2024-03-01 | 2024-03-31 |

If query is:
WHERE order_date = '2024-03-01'

Engine behavior:

Skip RG1
Skip RG2
Read RG3 only

Why it reduces data scanned
Without pushdown:
Read ALL row groups → Filter in memory
With pushdown:
Check metadata → Skip irrelevant row groups → Read only matching row groups
This reduces:
Disk I/O
Memory usage
Processing time

Example Scenario Analysis

What predicate is being pushed down?
→ order_date = '2024-03-01'

How does Parquet metadata help?
→ Uses min/max statistics to eliminate row groups.

What data can be skipped?
→ Row groups whose date range does not include 2024-03-01.

How does this reduce I/O?
→ Only relevant row groups are read from disk.

Step 3: Query Scenario Analysis
Given Query
SELECT region, SUM(amount)
FROM sales
WHERE order_date = '2024-03-01'
GROUP BY region;

Explain this code
Filters data by order_date
Groups by region
Calculates total amount per region

Column Analysis

Assume table columns:

order_id
customer_id
order_date
region
product_id
amount
discount


Which columns does the query need?

order_date (for filtering)
region (for grouping)
amount (for aggregation)

Which columns are read from disk (Parquet)?

→ order_date
→ region
→ amount

Which columns are skipped?

→ order_id
→ customer_id
→ product_id
→ discount

How pushdown helps

Predicate pushed down:

order_date = '2024-03-01'


Parquet uses:

Row group metadata
Min/max values

Which row groups can be skipped?
→ Any row group where the date range does not contain 2024-03-01.

How much data is filtered before reading?
If only 1% matches:
→ 99% of row groups can be skipped.

How Parquet optimizes this

Step 1: Read metadata from file footer
Step 2: Apply predicate pushdown
Step 3: Identify matching row groups
Step 4: Apply column pruning (read only 3 columns)
Step 5: Perform aggregation on filtered dataset

Query Optimization Breakdown:
| Step | Action             | Data Read                | Benefit               |
| ---- | ------------------ | ------------------------ | --------------------- |
| 1    | Predicate pushdown | Only matching row groups | Skips irrelevant data |
| 2    | Column pruning     | Only required columns    | Reduces I/O           |
| 3    | Data reading       | Filtered + pruned        | Efficient disk access |
| 4    | Processing         | Small dataset            | Faster aggregation    |

Comparison to Row-Based (CSV):
| Aspect         | Row-Based (CSV) | Columnar (Parquet)       |
| -------------- | --------------- | ------------------------ |
| Columns read   | All columns     | Only required columns    |
| Rows scanned   | All rows        | Only relevant row groups |
| I/O operations | High            | Low                      |
| Memory usage   | High            | Low                      |
| Query speed    | Slower          | Faster                   |

Step 4: Optimization Summary
Why Parquet + Column Pruning + Pushdown Work Together

Predicate pushdown reduces rows
Column pruning reduces columns
Together they minimize total data scanned

All rows × All columns
We get:

Filtered rows × Required columns

Why this matters at scale

Example:
Table size: 1 billion rows

20 columns
100 GB total size

Query needs:
2 columns
1% of rows

Without optimization (CSV)
Reads entire 100 GB
With column pruning

Reads:
2 / 20 = 10%
→ 10 GB

With predicate pushdown (1%)
10 GB × 1% = 100 MB

Final result
100 GB → 100 MB
1000× less data scanned

Optimization Summary Table:
| Optimization       | What It Does                | Benefit                  | When It Helps      |
| ------------------ | --------------------------- | ------------------------ | ------------------ |
| Column pruning     | Reads only required columns | Reduces I/O              | Wide tables        |
| Predicate pushdown | Skips irrelevant row groups | Reduces data scanned     | Selective filters  |
| Combined effect    | Reduces rows + columns      | Massive performance gain | Large datasets     |
| Scale impact       | Minimizes compute cost      | Faster queries           | Big data workloads |

Takeaways:
Columnar storage physically separates columns.
Column pruning reduces column-level I/O.
Predicate pushdown reduces row-level I/O.
Combined optimization dramatically reduces scanned data.
This is why columnar formats like Parquet dominate analytics workloads.