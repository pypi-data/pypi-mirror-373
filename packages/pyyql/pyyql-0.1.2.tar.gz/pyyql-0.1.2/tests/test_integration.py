import unittest
import os
import sys
from pyspark.sql import Row
import pyspark.sql.functions as F
from pyspark.sql.types import *

# Set up PySpark environment
os.environ["PYSPARK_PYTHON"] = sys.executable
os.environ["PYSPARK_DRIVER_PYTHON"] = sys.executable

# Import project modules
from samplesparksession import SampleSparkSession

from pyyql.yql import YQL

# Initialize Spark session
spark = SampleSparkSession().new_spark_session()
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

print(ROOT_DIR)

class TestIntegration(unittest.TestCase):
    """Integration tests for the complete PYYql system."""
    
    @classmethod
    def setUpClass(cls):
        """Set up integration test data."""
        cls.hr_yaml_path = ROOT_DIR + "/resources/suit_1/HR_view.yaml"
        cls.csv_data_path = ROOT_DIR + "/resources/suit_1/"
        
        # Load or create test data
        cls.hr_dataframes = cls._setup_test_data()
    
    @classmethod
    def _setup_test_data(cls):
        """Set up comprehensive test data."""
        # Create realistic test data
        emp_data = [
            Row(emp_id=1, emp_name="John Smith", emp_joining_year=2020, manager_id="MGR001"),
            Row(emp_id=2, emp_name="Jane Doe", emp_joining_year=2019, manager_id="MGR001"),
            Row(emp_id=3, emp_name="Bob Wilson", emp_joining_year=2021, manager_id="MGR002"),
            Row(emp_id=4, emp_name="Alice Johnson", emp_joining_year=2018, manager_id=None),  # CEO
            Row(emp_id=5, emp_name="Charlie Brown", emp_joining_year=2022, manager_id="MGR002"),
        ]
        
        mgr_data = [
            Row(manager_id="MGR001", manager_name="Sarah Wilson", manager_start_year=2017, department_id="DEPT001"),
            Row(manager_id="MGR002", manager_name="Mike Davis", manager_start_year=2016, department_id="DEPT002"),
            Row(manager_id="MGR003", manager_name="Lisa Garcia", manager_start_year=2018, department_id="DEPT003"),
        ]
        
        dept_data = [
            Row(department_id="DEPT001", department_name="Engineering", status=1),
            Row(department_id="DEPT002", department_name="Sales", status=1),
            Row(department_id="DEPT003", department_name="Marketing", status=0),  # Inactive
            Row(department_id="DEPT004", department_name="HR", status=1),
        ]
        
        return {
            "employee": spark.createDataFrame(emp_data),
            "manager": spark.createDataFrame(mgr_data),
            "department": spark.createDataFrame(dept_data)
        }
    
    def test_end_to_end_pipeline(self):
        """Test complete end-to-end pipeline execution."""
        print("\n" + "="*60)
        print("END-TO-END INTEGRATION TEST")
        print("="*60)
        
        # Initialize YQL with debug mode
        yql = YQL(
            yaml_path=self.hr_yaml_path,
            df_named_dict=self.hr_dataframes,
            debug=True
        )
        
        # Show execution plan
        print("\n1. EXECUTION PLAN:")
        execution_plan = yql.get_execution_plan()
        for step in execution_plan:
            print(f"   Step {step['step']}: {step['operation']} - {step['description']}")
        
        # Show query explanation
        print("\n2. QUERY EXPLANATION:")
        print(f"   {yql.explain_query()}")
        
        # Execute pipeline
        print("\n3. EXECUTING PIPELINE:")
        try:
            result_df, lineage_metadata = yql.run_with_lineage()
            
            print(f"   ✓ Execution successful!")
            print(f"   ✓ Result has {result_df.count()} rows and {len(result_df.columns)} columns")
            
            # Show results
            print("\n4. RESULTS:")
            result_df.show(20, truncate=False)
            
            # Show performance stats
            perf_stats = yql.get_performance_stats()
            print(f"\n5. PERFORMANCE:")
            print(f"   Execution time: {perf_stats.get('execution_time_seconds', 'unknown')}s")
            print(f"   Input tables: {perf_stats.get('input_tables', 'unknown')}")
            print(f"   Output columns: {perf_stats.get('output_columns', 'unknown')}")
            
            # Show lineage information
            print(f"\n6. LINEAGE:")
            print(f"   Source tables: {list(lineage_metadata.get('source_tables', {}).keys())}")
            print(f"   Transformations: {len(lineage_metadata.get('transformations', []))}")
            print(f"   Column lineage: {len(lineage_metadata.get('column_lineage', {}))}")
            
            return result_df
            
        except Exception as e:
            print(f"   ✗ Execution failed: {e}")
            raise
    
    def test_performance_benchmarking(self):
        """Test performance with different data sizes."""
        print("\n" + "="*60)
        print("PERFORMANCE BENCHMARKING")
        print("="*60)
        
        # Test with current data size
        yql = YQL(self.hr_yaml_path, self.hr_dataframes, debug=False)
        
        import time
        start_time = time.time()
        result_df = yql.run()
        execution_time = time.time() - start_time
        
        print(f"Data size: {sum(df.count() for df in self.hr_dataframes.values())} total rows")
        print(f"Execution time: {execution_time:.3f}s")
        print(f"Result size: {result_df.count()} rows")
        print(f"Throughput: {result_df.count() / execution_time:.1f} rows/second")




if __name__ == "__main__":
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test classes
    test_suite.addTest(unittest.makeSuite(TestIntegration))
    
    # Run tests with detailed output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Print summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    if result.failures:
        print("\nFAILURES:")
        for test, traceback in result.failures:
            print(f"  {test}: {traceback}")
    
    if result.errors:
        print("\nERRORs:")
        for test, traceback in result.errors:
            print(f"  {test}: {traceback}")
    
    success_rate = ((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun) * 100
    print(f"\nSuccess rate: {success_rate:.1f}%")