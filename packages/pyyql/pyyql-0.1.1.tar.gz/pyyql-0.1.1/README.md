# PYYql - Declarative PySpark SQL Engine

[![Python Version](https://img.shields.io/badge/python-3.7%2B-blue.svg)](https://www.python.org/downloads/)
[![PySpark Version](https://img.shields.io/badge/pyspark-3.0%2B-orange.svg)](https://spark.apache.org/downloads.html)
[![PyPI version](https://badge.fury.io/py/pyyql.svg)](https://badge.fury.io/py/pyyql)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

**Transform complex PySpark SQL operations into simple, debuggable YAML configurations with complete data lineage tracking**

## What is PYYql?

PYYql (Python YAML Query Language) is a declarative engine that converts YAML configurations into PySpark DataFrame operations. It makes complex SQL transformations readable, maintainable, and debuggable while preserving complete data lineage.

**Before PYYql (Complex PySpark):**
```python
result = df1.alias("emp") \
    .join(df2.alias("mgr"), F.col("emp.manager_id") == F.col("mgr.manager_id"), "left") \
    .join(df3.alias("dept"), F.col("mgr.department_id") == F.col("dept.department_id"), "left") \
    .filter((F.col("dept.status") == 1) & (F.col("emp.emp_id").isNotNull())) \
    .select(
        F.col("emp.emp_id").alias("employee_id"),
        F.col("emp.emp_name").alias("employee_name"), 
        F.col("mgr.manager_name").alias("manager_name"),
        F.col("dept.department_name").alias("department_name")
    ) \
    .orderBy("department_name", "employee_name")
```

**After PYYql (Clean YAML):**
```yaml
# hr_report.yaml - Employee hierarchy report with departments

# Define table aliases and map to actual DataFrame names
dependencies:
  emp: { table_name: employee, type: source }    # Employee master data
  mgr: { table_name: manager, type: source }     # Manager information  
  dept: { table_name: department, type: source } # Department details

# Define how tables should be joined (LEFT joins by default)
join_conditions:
  - ("emp", "mgr", "emp.manager_id", "mgr.manager_id")     # Employee to Manager
  - ("mgr", "dept", "mgr.department_id", "dept.department_id") # Manager to Department

# Apply business rules and data quality filters
filter_condition:
  - "dept.status == 1"           # Only active departments
  - "emp.emp_id IS NOT NULL"     # Data quality: no null employee IDs

# Select columns and provide business-friendly names
select:
  emp.emp_id: employee_id         # Employee identifier
  emp.emp_name: employee_name     # Employee full name
  mgr.manager_name: manager_name  # Direct manager name
  dept.department_name: department_name # Department name

# Sort results for consistent reporting
sort_condition:
  - "(dept.department_name, asc)"  # First by department
  - "(emp.emp_name, asc)"          # Then by employee name
```

## Quick Start

### Installation

```bash
pip install pyyql
```

### Prerequisites
- Python 3.7+
- PySpark 3.0+
- PyYAML (automatically installed)

### Your First PYYql Query

**1. Create your data transformation YAML (`customer_orders.yaml`):**

```yaml
# customer_orders.yaml - Customer order analysis report
constructed_table_name: customer_order_report  # Output table name

# Map business-friendly aliases to actual DataFrame keys
dependencies:
  customers: { table_name: customer_data, type: source }  # Customer master data
  orders: { table_name: order_data, type: source }        # Order transaction data

# Join customers with their orders
join_conditions:
  - ("customers", "orders", "customers.customer_id", "orders.customer_id")

# Select relevant columns with business-friendly names
select:
  customers.customer_name: customer_name  # Customer full name
  customers.email: email                  # Contact email
  orders.order_total: amount             # Order value
  orders.order_date: date                # When order was placed

# Apply business filters
filter_condition:
  - "orders.order_total > 100"  # High-value orders only

# Sort by most recent orders first
sort_condition:
  - "(orders.order_date, desc)"
```

**2. Execute with Python:**

```python
from pyspark.sql import SparkSession
from pyyql import YQL

# Initialize Spark
spark = SparkSession.builder.appName("PYYql Demo").getOrCreate()

# Load your data (CSV, Parquet, Database, etc.)
customers_df = spark.read.csv("customers.csv", header=True, inferSchema=True)
orders_df = spark.read.csv("orders.csv", header=True, inferSchema=True)

# Map table names to DataFrames
df_dict = {
    "customer_data": customers_df,
    "order_data": orders_df
}

# Execute the transformation
yql = YQL(yaml_path="customer_orders.yaml", df_named_dict=df_dict, debug=True)
result_df = yql.run()

# Show results
result_df.show()
result_df.write.mode("overwrite").parquet("output/customer_orders")
```

## Step-by-Step Tutorial

### Step 1: Understanding the Data Model

Let's work with a realistic HR dataset:

```
employee.csv        manager.csv         department.csv
+--------+---------+  +------------+----+  +-----------+----------+
|emp_id  |emp_name |  |manager_id  |... |  |dept_id    |dept_name |
+--------+---------+  +------------+----+  +-----------+----------+  
|1       |John Doe |  |MGR001      |... |  |DEPT001    |Engineering|
|2       |Jane     |  |MGR002      |... |  |DEPT002    |Sales     |
+--------+---------+  +------------+----+  +-----------+----------+
```

### Step 2: Define Your YAML Configuration

Create `hr_analysis.yaml`:

```yaml
# HR Analysis Report Configuration
constructed_table_name: hr_employee_report

# Define your data sources
dependencies:
  emp:
    table_name: employee    # Must match key in your df_dict
    type: source
    source: hr_database
  mgr:
    table_name: manager
    type: source  
    source: hr_database
  dept:
    table_name: department
    type: source
    source: hr_database

# Define relationships between tables
join_conditions:
  # Format: (left_table, right_table, left_join_key, right_join_key)
  - ("emp", "mgr", "emp.manager_id", "mgr.manager_id")
  - ("mgr", "dept", "mgr.department_id", "dept.department_id")

# Optional: Specify join type (default: left)
join_type: "left"

# Filter the data (WHERE clause)
filter_condition:
  - "dept.status == 1"                    # Only active departments
  - "emp.emp_joining_year >= 2020"        # Recent hires only
  - "emp.emp_id IS NOT NULL"              # Data quality check

# Select and rename columns
select:
  emp.emp_id: employee_id
  emp.emp_name: employee_name
  emp.emp_joining_year: joining_year
  mgr.manager_name: manager_name
  dept.department_name: department
  dept.status: dept_status

# Sort the results
sort_condition:
  - "(dept.department_name, asc)"
  - "(emp.emp_name, asc)"

# Optional: Remove duplicates
distinct: false

# Optional: Limit results
limit: null
```

### Step 3: Load Your Data

```python
from pyspark.sql import SparkSession
from pyyql import YQL
import pyspark.sql.functions as F

# Initialize Spark
spark = SparkSession.builder \
    .appName("HR Analysis") \
    .config("spark.sql.adaptive.enabled", "false") \
    .getOrCreate()

# Method 1: Load from CSV files
employee_df = spark.read.csv("data/employee.csv", header=True, inferSchema=True)
manager_df = spark.read.csv("data/manager.csv", header=True, inferSchema=True)  
department_df = spark.read.csv("data/department.csv", header=True, inferSchema=True)

# Method 2: Load from database
# employee_df = spark.read.jdbc(url=db_url, table="employee", properties=db_props)

# Method 3: Create sample data for testing
from pyspark.sql import Row

employee_df = spark.createDataFrame([
    Row(emp_id=1, emp_name="John Doe", emp_joining_year=2020, manager_id="MGR001"),
    Row(emp_id=2, emp_name="Jane Smith", emp_joining_year=2021, manager_id="MGR002"),
    Row(emp_id=3, emp_name="Bob Wilson", emp_joining_year=2019, manager_id="MGR001"),
])

manager_df = spark.createDataFrame([
    Row(manager_id="MGR001", manager_name="Sarah Wilson", department_id="DEPT001"),
    Row(manager_id="MGR002", manager_name="Mike Davis", department_id="DEPT002"),
])

department_df = spark.createDataFrame([
    Row(department_id="DEPT001", department_name="Engineering", status=1),
    Row(department_id="DEPT002", department_name="Sales", status=1),
    Row(department_id="DEPT003", department_name="Marketing", status=0),  # Inactive
])

# Create the DataFrame dictionary (keys must match YAML dependencies)
df_dict = {
    "employee": employee_df,      # matches table_name in YAML
    "manager": manager_df,
    "department": department_df
}
```

### Step 4: Execute the Transformation

```python
# Create YQL instance
yql = YQL(
    yaml_path="hr_analysis.yaml",
    df_named_dict=df_dict,
    debug=True,                    # Enable detailed logging
    validate_schema=True           # Validate schemas before execution
)

# Option 1: Simple execution
result_df = yql.run()
result_df.show(20, truncate=False)

# Option 2: Execution with lineage tracking
result_df, lineage_metadata = yql.run_with_lineage()
print(f"Query ID: {lineage_metadata['query_id']}")
print(f"Source tables: {list(lineage_metadata['source_tables'].keys())}")

# Option 3: Dry run (validate without executing)
validation_result = yql.dry_run()
if validation_result['status'] == 'valid':
    print("Configuration is valid")
    for step in validation_result['execution_plan']:
        print(f"Step {step['step']}: {step['operation']}")
else:
    print(f"Configuration error: {validation_result['error']}")
```

### Step 5: Understanding the Results

```python
# Show execution plan
execution_plan = yql.get_execution_plan()
for step in execution_plan:
    print(f"Step {step['step']}: {step['operation']} - {step['description']}")

# Get human-readable explanation
explanation = yql.explain_query()
print(f"Query explanation: {explanation}")

# Get performance statistics
stats = yql.get_performance_stats()
print(f"Execution time: {stats.get('execution_time_seconds', 'N/A')}s")
print(f"Output rows: {stats.get('output_rows', 'N/A')}")

# Export detailed lineage report
report_path = yql.export_lineage_report("hr_analysis_lineage.md")
print(f"Lineage report saved to: {report_path}")
```

## Advanced Examples

### Example 1: Sales Analytics with Aggregations

```yaml
# sales_summary.yaml - Monthly sales performance by region and product
constructed_table_name: monthly_sales_summary

# Define data sources
dependencies:
  sales: { table_name: sales_data, type: source }      # Sales transaction data
  products: { table_name: product_catalog, type: source } # Product master data
  regions: { table_name: sales_regions, type: source }    # Regional information

# Join sales with product and region details
join_conditions:
  - ("sales", "products", "sales.product_id", "products.product_id")
  - ("sales", "regions", "sales.region_id", "regions.region_id")

# Filter for current year active products only
filter_condition:
  - "sales.sale_date >= '2024-01-01'"  # Current year only
  - "sales.amount > 0"                 # Valid positive sales
  - "products.category != 'DISCONTINUED'" # Active products only

# Group sales by region and product category
group_condition:
  - "regions.region_name"    # Sales region
  - "products.category"      # Product category

# Calculate sales metrics
aggregations:
  sales.amount:
    - "SUM(amount)"    # Total sales revenue
    - "AVG(amount)"    # Average sale value
  sales.sale_id:
    - "COUNT(*)"       # Number of transactions

# Filter aggregated results - only high-performing segments
having_condition:
  - "SUM(sales.amount) > 10000"  # Regions with >10K revenue

# Select and rename aggregated columns
select:
  regions.region_name: region           # Sales region name
  products.category: product_category   # Product category
  sales.amount: total_sales            # Total revenue (SUM)
  sales.amount: avg_sale_amount        # Average sale value
  sales.sale_id: number_of_sales       # Transaction count

# Sort by highest revenue regions first
sort_condition:
  - "(total_sales, desc)"
```

### Example 2: Customer Segmentation Pipeline

```yaml
# customer_segmentation.yaml - Customer lifetime value analysis
constructed_table_name: customer_segments

# Define customer transaction data sources
dependencies:
  customers: { table_name: customer_base, type: source }    # Customer master
  orders: { table_name: order_history, type: source }       # Order history
  payments: { table_name: payment_data, type: source }      # Payment transactions

# Chain joins: customers -> orders -> payments
join_conditions:
  - ("customers", "orders", "customers.customer_id", "orders.customer_id")
  - ("orders", "payments", "orders.order_id", "payments.order_id")

# Filter for active customers with successful payments
filter_condition:
  - "customers.status == 'ACTIVE'"           # Active customers only
  - "payments.payment_status == 'COMPLETED'" # Successful payments only
  - "orders.order_date >= '2023-01-01'"      # Recent orders (last year)

# Group by customer to calculate metrics
group_condition:
  - "customers.customer_id"    # Individual customer analysis
  - "customers.customer_tier"  # Existing customer tier/segment

# Calculate customer lifetime value metrics
aggregations:
  payments.amount:
    - "SUM(amount)"    # Total customer spend
    - "COUNT(*)"       # Number of orders
  orders.order_date:
    - "MAX(order_date)" # Last order date

# Select customer metrics with business names
select:
  customers.customer_id: customer_id        # Customer identifier
  customers.customer_name: customer_name    # Customer name
  customers.customer_tier: tier             # Current tier/segment
  payments.amount: total_spent             # Lifetime value
  payments.amount: order_count             # Purchase frequency
  orders.order_date: last_order_date       # Recency

# Sort by highest value customers first
sort_condition:
  - "(total_spent, desc)"

# Limit to top customers for analysis
limit: 1000
```

### Example 3: Data Quality and Validation

```yaml
# data_quality_check.yaml - Customer data validation and cleansing
constructed_table_name: data_quality_report

# Source data that needs validation
dependencies:
  raw_data: { table_name: raw_customer_data, type: source } # Raw customer input

# Apply data quality rules and filters
filter_condition:
  - "raw_data.email IS NOT NULL"           # Email is required
  - "raw_data.phone != ''"                 # Phone cannot be empty
  - "raw_data.created_date >= '2024-01-01'" # Recent registrations only
  - "raw_data.age BETWEEN 18 AND 120"      # Reasonable age range

# Select clean data with standardized column names
select:
  raw_data.customer_id: id               # Unique identifier
  raw_data.email: email_address          # Contact email
  raw_data.phone: phone_number           # Phone number
  raw_data.created_date: registration_date # Account creation date
  raw_data.age: customer_age             # Customer age

# Remove duplicate records
distinct: true

# Sort by most recent registrations
sort_condition:
  - "(registration_date, desc)"
```