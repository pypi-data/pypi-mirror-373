from pyspark.sql import SparkSession
from pyyql import YQL
import pyspark.sql.functions as F

# Initialize Spark
spark = SparkSession.builder \
    .appName("HR Analysis") \
    .config("spark.sql.adaptive.enabled", "false") \
    .getOrCreate()


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