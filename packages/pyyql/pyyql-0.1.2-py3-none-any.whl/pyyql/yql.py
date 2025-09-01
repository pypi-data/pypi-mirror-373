from pyspark.sql import SparkSession, DataFrame
import pyspark.sql.functions as F
from typing import Dict, List, Optional, Any
import logging
import time
from datetime import datetime

from pyyql.pyyql import PYYql

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class YQL:
    """
    YQL - YAML Query Language
    
    High-level interface for executing YAML-based data transformations
    using PySpark DataFrames with comprehensive validation, debugging,
    and performance monitoring capabilities.
    """
    
    def __init__(self, yaml_path: str, df_named_dict: Dict[str, DataFrame], 
                 debug: bool = False, validate_schema: bool = True):
        """
        Initialize YQL executor.
        
        Args:
            yaml_path: Path to YAML configuration file
            df_named_dict: Dictionary mapping table names to PySpark DataFrames
            debug: Enable debug logging and intermediate results
            validate_schema: Perform schema validation before execution
        """
        self.yaml_path = yaml_path
        self.df_named_dict = df_named_dict
        self.debug = debug
        self.validate_schema = validate_schema
        self.execution_stats = {}
        
        # Initialize PYYql engine
        self.pyyql_engine = PYYql(yaml_path=yaml_path, debug=debug)
        
        if debug:
            logger.setLevel(logging.DEBUG)
            logger.debug(f"YQL initialized with {len(df_named_dict)} DataFrames")
    
    # ============================================================================
    # MAIN EXECUTION INTERFACE
    # ============================================================================
    
    def run(self) -> DataFrame:
        """
        Execute the complete YAML-defined transformation pipeline.
        
        Returns:
            Transformed PySpark DataFrame
            
        Raises:
            RuntimeError: If execution fails
            ValueError: If validation fails
        """
        start_time = time.time()
        
        try:
            logger.info(f"Starting YQL execution for: {self.yaml_path}")
            
            # Step 1: Validate inputs
            if self.validate_schema:
                self._validate_input()
            
            # Step 2: Execute transformation pipeline
            result_df = self.pyyql_engine.run(self.df_named_dict)
            
            # Step 3: Collect execution statistics
            execution_time = time.time() - start_time
            self._collect_execution_stats(result_df, execution_time)
            
            logger.info(f"YQL execution completed successfully in {execution_time:.2f}s")
            
            if self.debug:
                self._log_execution_summary(result_df)
            
            return result_df
            
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"YQL execution failed after {execution_time:.2f}s: {e}")
            raise RuntimeError(f"YQL execution failed: {e}") from e
    
    def run_with_lineage(self) -> tuple[DataFrame, Dict[str, Any]]:
        """
        Execute transformation and return both result and lineage metadata.
        
        Returns:
            Tuple of (result_dataframe, lineage_metadata)
        """
        result_df = self.run()
        lineage_metadata = self._generate_lineage_metadata(result_df)
        return result_df, lineage_metadata
    
    def dry_run(self) -> Dict[str, Any]:
        """
        Validate configuration and return execution plan without running.
        
        Returns:
            Dictionary containing execution plan and validation results
        """
        try:
            logger.info("Performing dry run validation...")
            
            # Validate inputs
            self._validate_input()
            
            # Get execution plan
            execution_plan = self.get_execution_plan()
            
            # Perform schema validation
            schema_validation = self._validate_schema_compatibility()
            
            return {
                "status": "valid",
                "execution_plan": execution_plan,
                "schema_validation": schema_validation,
                "estimated_operations": len(execution_plan),
                "input_tables": list(self.df_named_dict.keys()),
                "yaml_path": self.yaml_path
            }
            
        except Exception as e:
            return {
                "status": "invalid",
                "error": str(e),
                "yaml_path": self.yaml_path
            }
    
    # ============================================================================
    # VALIDATION METHODS
    # ============================================================================
    
    def _validate_input(self) -> None:
        """Comprehensive validation of inputs and configuration."""
        logger.debug("Validating YQL inputs...")
        
        # Validate YAML path
        if not self.yaml_path or not isinstance(self.yaml_path, str):
            raise ValueError("yaml_path must be a non-empty string")
        
        # Validate DataFrame dictionary
        if not self.df_named_dict or not isinstance(self.df_named_dict, dict):
            raise ValueError("df_named_dict must be a non-empty dictionary")
        
        # Validate all values are DataFrames
        for name, df in self.df_named_dict.items():
            if not isinstance(df, DataFrame):
                raise ValueError(f"'{name}' must be a PySpark DataFrame, got {type(df)}")
        
        # Validate DataFrame schemas are not empty
        for name, df in self.df_named_dict.items():
            if not df.columns:
                raise ValueError(f"DataFrame '{name}' has no columns")
        
        logger.debug("Input validation completed successfully")
    
    def _validate_schema_compatibility(self) -> Dict[str, Any]:
        """Validate schema compatibility for joins and operations."""
        validation_results = {
            "join_compatibility": True,
            "column_conflicts": [],
            "missing_columns": [],
            "warnings": []
        }
        
        try:
            # Get join conditions from YAML
            join_conditions = self.pyyql_engine._get_join_condition()
            
            for condition in join_conditions:
                left_table, right_table, left_key, right_key = condition
                
                # Check if tables exist
                left_df = self.df_named_dict.get(left_table)
                right_df = self.df_named_dict.get(right_table)
                
                if not left_df or not right_df:
                    validation_results["missing_columns"].append({
                        "condition": condition,
                        "error": f"Missing table: {left_table if not left_df else right_table}"
                    })
                    validation_results["join_compatibility"] = False
                    continue
                
                # Extract column names
                left_col = left_key.split('.')[-1] if '.' in left_key else left_key
                right_col = right_key.split('.')[-1] if '.' in right_key else right_key
                
                # Check column existence
                if left_col not in left_df.columns:
                    validation_results["missing_columns"].append({
                        "table": left_table,
                        "column": left_col,
                        "available_columns": left_df.columns
                    })
                    validation_results["join_compatibility"] = False
                
                if right_col not in right_df.columns:
                    validation_results["missing_columns"].append({
                        "table": right_table,
                        "column": right_col,
                        "available_columns": right_df.columns
                    })
                    validation_results["join_compatibility"] = False
                
                # Check data type compatibility
                if (left_col in left_df.columns and right_col in right_df.columns):
                    left_type = dict(left_df.dtypes)[left_col]
                    right_type = dict(right_df.dtypes)[right_col]
                    
                    if left_type != right_type:
                        validation_results["warnings"].append({
                            "type": "data_type_mismatch",
                            "left_table": left_table,
                            "left_column": left_col,
                            "left_type": left_type,
                            "right_table": right_table,
                            "right_column": right_col,
                            "right_type": right_type
                        })
        
        except Exception as e:
            validation_results["join_compatibility"] = False
            validation_results["validation_error"] = str(e)
        
        return validation_results
    
    # ============================================================================
    # EXECUTION PLAN & DEBUGGING
    # ============================================================================
    
    def get_execution_plan(self) -> List[Dict[str, Any]]:
        """
        Return detailed execution plan with operation sequence.
        
        Returns:
            List of operation dictionaries with details
        """
        try:
            # Read configuration
            config = self.pyyql_engine._read()
            
            plan = []
            step = 1
            
            # Step 1: FROM clause (dependencies)
            dependencies = config.get('dependencies', {})
            if dependencies:
                plan.append({
                    "step": step,
                    "operation": "FROM",
                    "description": "Load and alias source tables",
                    "details": {
                        "tables": list(dependencies.keys()),
                        "table_mappings": {k: v.get('table_name') for k, v in dependencies.items()}
                    }
                })
                step += 1
            
            # Step 2: JOIN operations
            join_conditions = config.get('join_conditions', [])
            if join_conditions:
                plan.append({
                    "step": step,
                    "operation": "JOIN",
                    "description": f"Execute {len(join_conditions)} join operations",
                    "details": {
                        "join_type": config.get('join_type', 'left'),
                        "conditions": join_conditions,
                        "estimated_complexity": "O(n*m)" if len(join_conditions) > 2 else "O(n+m)"
                    }
                })
                step += 1
            
            # Step 3: WHERE clause
            filter_conditions = config.get('filter_condition', [])
            if filter_conditions:
                plan.append({
                    "step": step,
                    "operation": "WHERE",
                    "description": f"Apply {len(filter_conditions)} filter conditions",
                    "details": {
                        "conditions": filter_conditions,
                        "estimated_selectivity": "unknown"  # Could be estimated
                    }
                })
                step += 1
            
            # Step 4: GROUP BY
            group_conditions = config.get('group_condition', [])
            aggregations = config.get('aggregations', {})
            if group_conditions:
                plan.append({
                    "step": step,
                    "operation": "GROUP BY",
                    "description": f"Group by {len(group_conditions)} columns with aggregations",
                    "details": {
                        "group_columns": group_conditions,
                        "aggregations": aggregations,
                        "estimated_complexity": "O(n log n)"
                    }
                })
                step += 1
            
            # Step 5: HAVING clause
            having_conditions = config.get('having_condition', [])
            if having_conditions:
                plan.append({
                    "step": step,
                    "operation": "HAVING",
                    "description": f"Apply {len(having_conditions)} post-aggregation filters",
                    "details": {
                        "conditions": having_conditions
                    }
                })
                step += 1
            
            # Step 6: SELECT clause
            select_columns = config.get('select', {})
            if select_columns:
                plan.append({
                    "step": step,
                    "operation": "SELECT",
                    "description": f"Project {len(select_columns)} columns with aliases",
                    "details": {
                        "column_mappings": select_columns,
                        "output_columns": list(select_columns.values())
                    }
                })
                step += 1
            
            # Step 7: ORDER BY
            sort_conditions = config.get('sort_condition', [])
            if sort_conditions:
                plan.append({
                    "step": step,
                    "operation": "ORDER BY",
                    "description": f"Sort by {len(sort_conditions)} columns",
                    "details": {
                        "sort_specifications": sort_conditions,
                        "estimated_complexity": "O(n log n)"
                    }
                })
                step += 1
            
            # Step 8: DISTINCT
            if config.get('distinct', False):
                plan.append({
                    "step": step,
                    "operation": "DISTINCT",
                    "description": "Remove duplicate rows",
                    "details": {
                        "estimated_complexity": "O(n)"
                    }
                })
                step += 1
            
            # Step 9: LIMIT
            limit = config.get('limit')
            if limit:
                plan.append({
                    "step": step,
                    "operation": "LIMIT",
                    "description": f"Limit output to {limit} rows",
                    "details": {
                        "row_limit": limit
                    }
                })
                step += 1
            
            return plan
            
        except Exception as e:
            logger.error(f"Error generating execution plan: {e}")
            return [{"error": f"Failed to generate execution plan: {e}"}]
    
    def explain_query(self) -> str:
        """
        Generate human-readable explanation of the YAML query.
        
        Returns:
            String explanation of what the query does
        """
        try:
            config = self.pyyql_engine._read()
            explanation_parts = []
            
            # Describe the data sources
            dependencies = config.get('dependencies', {})
            if dependencies:
                table_names = [v.get('table_name', k) for k, v in dependencies.items()]
                explanation_parts.append(f"This query processes data from {len(table_names)} table(s): {', '.join(table_names)}")
            
            # Describe joins
            join_conditions = config.get('join_conditions', [])
            if join_conditions:
                join_type = config.get('join_type', 'left')
                explanation_parts.append(f"It performs {len(join_conditions)} {join_type} join(s) to combine the tables")
            
            # Describe filters
            filter_conditions = config.get('filter_condition', [])
            if filter_conditions:
                explanation_parts.append(f"Data is filtered using {len(filter_conditions)} condition(s)")
            
            # Describe grouping
            group_conditions = config.get('group_condition', [])
            if group_conditions:
                explanation_parts.append(f"Results are grouped by: {', '.join(group_conditions)}")
            
            # Describe aggregations
            aggregations = config.get('aggregations', {})
            if aggregations:
                agg_count = sum(len(funcs) for funcs in aggregations.values())
                explanation_parts.append(f"With {agg_count} aggregation function(s) applied")
            
            # Describe output
            select_columns = config.get('select', {})
            if select_columns:
                explanation_parts.append(f"The final output contains {len(select_columns)} column(s)")
            
            # Describe sorting
            sort_conditions = config.get('sort_condition', [])
            if sort_conditions:
                explanation_parts.append(f"Results are sorted by {len(sort_conditions)} column(s)")
            
            # Describe limits
            if config.get('distinct'):
                explanation_parts.append("Duplicate rows are removed")
            
            limit = config.get('limit')
            if limit:
                explanation_parts.append(f"Output is limited to {limit} rows")
            
            return ". ".join(explanation_parts) + "."
            
        except Exception as e:
            return f"Error generating query explanation: {e}"
    
    # ============================================================================
    # PERFORMANCE & STATISTICS
    # ============================================================================
    
    def _collect_execution_stats(self, result_df: DataFrame, execution_time: float) -> None:
        """Collect execution statistics for performance monitoring."""
        try:
            self.execution_stats = {
                "execution_time_seconds": execution_time,
                "timestamp": datetime.now().isoformat(),
                "yaml_path": self.yaml_path,
                "input_tables": len(self.df_named_dict),
                "output_columns": len(result_df.columns),
                "output_column_names": result_df.columns
            }
            
            # Try to get row count (may be expensive for large datasets)
            if self.debug:
                try:
                    self.execution_stats["output_rows"] = result_df.count()
                except Exception:
                    self.execution_stats["output_rows"] = "not_computed"
            
        except Exception as e:
            logger.warning(f"Failed to collect execution statistics: {e}")
    
    def _log_execution_summary(self, result_df: DataFrame) -> None:
        """Log detailed execution summary for debugging."""
        logger.debug("=== YQL Execution Summary ===")
        logger.debug(f"YAML Configuration: {self.yaml_path}")
        logger.debug(f"Input Tables: {list(self.df_named_dict.keys())}")
        logger.debug(f"Output Columns: {result_df.columns}")
        logger.debug(f"Execution Time: {self.execution_stats.get('execution_time_seconds', 'unknown'):.3f}s")
        
        if "output_rows" in self.execution_stats:
            logger.debug(f"Output Rows: {self.execution_stats['output_rows']}")
        
        logger.debug("=" * 30)
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """
        Get performance statistics from the last execution.
        
        Returns:
            Dictionary containing performance metrics
        """
        return self.execution_stats.copy() if self.execution_stats else {}
    
    # ============================================================================
    # LINEAGE & METADATA TRACKING
    # ============================================================================
    
    def _generate_lineage_metadata(self, result_df: DataFrame) -> Dict[str, Any]:
        """
        Generate column-level lineage metadata.
        
        Args:
            result_df: The result DataFrame
            
        Returns:
            Dictionary containing lineage information
        """
        try:
            config = self.pyyql_engine._read()
            
            lineage_metadata = {
                "query_id": f"{self.yaml_path}_{int(time.time())}",
                "execution_timestamp": datetime.now().isoformat(),
                "source_tables": {},
                "column_lineage": {},
                "transformations": [],
                "business_rules": {}
            }
            
            # Collect source table metadata
            dependencies = config.get('dependencies', {})
            for alias, table_config in dependencies.items():
                table_name = table_config.get('table_name')
                if table_name in self.df_named_dict:
                    source_df = self.df_named_dict[table_name]
                    lineage_metadata["source_tables"][alias] = {
                        "table_name": table_name,
                        "columns": source_df.columns,
                        "schema": [{"name": name, "type": dtype} for name, dtype in source_df.dtypes]
                    }
            
            # Generate column lineage
            select_mappings = config.get('select', {})
            for source_col, target_col in select_mappings.items():
                lineage_metadata["column_lineage"][target_col] = {
                    "source_column": source_col,
                    "transformation_type": "alias" if source_col.split('.')[-1] != target_col else "direct",
                    "source_table": source_col.split('.')[0] if '.' in source_col else "unknown"
                }
            
            # Document transformations
            transformations = []
            
            if config.get('join_conditions'):
                transformations.append({
                    "type": "join",
                    "description": f"{len(config['join_conditions'])} table join(s)",
                    "details": config['join_conditions']
                })
            
            if config.get('filter_condition'):
                transformations.append({
                    "type": "filter",
                    "description": "Data filtering",
                    "details": config['filter_condition']
                })
            
            if config.get('group_condition'):
                transformations.append({
                    "type": "aggregation",
                    "description": "Grouping and aggregation",
                    "details": {
                        "group_by": config['group_condition'],
                        "aggregations": config.get('aggregations', {})
                    }
                })
            
            lineage_metadata["transformations"] = transformations
            
            # Extract business rules (from comments or specific sections)
            constructed_table_name = config.get('constructed_table_name')
            if constructed_table_name:
                lineage_metadata["business_rules"]["output_table"] = constructed_table_name
            
            return lineage_metadata
            
        except Exception as e:
            logger.warning(f"Failed to generate lineage metadata: {e}")
            return {"error": str(e)}
    
    def export_lineage_report(self, output_path: str = None) -> str:
        """
        Export detailed lineage report to file.
        
        Args:
            output_path: Optional path for output file
            
        Returns:
            Path to generated report file
        """
        try:
            # Execute query to get lineage
            result_df, lineage_metadata = self.run_with_lineage()
            
            # Generate report content
            report_lines = [
                "# YQL Data Lineage Report",
                f"**Generated:** {datetime.now().isoformat()}",
                f"**YAML Configuration:** {self.yaml_path}",
                "",
                "## Query Explanation",
                self.explain_query(),
                "",
                "## Execution Plan"
            ]
            
            execution_plan = self.get_execution_plan()
            for step in execution_plan:
                report_lines.append(f"**Step {step.get('step', '?')}:** {step.get('operation', 'Unknown')} - {step.get('description', 'No description')}")
            
            report_lines.extend([
                "",
                "## Column Lineage",
                "| Output Column | Source Column | Source Table | Transformation |",
                "|---------------|---------------|--------------|----------------|"
            ])
            
            column_lineage = lineage_metadata.get("column_lineage", {})
            for target_col, lineage_info in column_lineage.items():
                source_col = lineage_info.get("source_column", "unknown")
                source_table = lineage_info.get("source_table", "unknown")
                transformation = lineage_info.get("transformation_type", "unknown")
                report_lines.append(f"| {target_col} | {source_col} | {source_table} | {transformation} |")
            
            # Write to file
            if not output_path:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_path = f"yql_lineage_report_{timestamp}.md"
            
            with open(output_path, 'w') as f:
                f.write('\n'.join(report_lines))
            
            logger.info(f"Lineage report exported to: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Failed to export lineage report: {e}")
            raise RuntimeError(f"Lineage report export failed: {e}") from e
    
    # ============================================================================
    # UTILITY METHODS
    # ============================================================================
    
    def get_supported_operations(self) -> List[str]:
        """Return list of supported SQL operations."""
        return [
            "SELECT with column aliasing",
            "FROM with table dependencies",
            "JOIN (LEFT, RIGHT, INNER, OUTER)",
            "WHERE with filter conditions",
            "GROUP BY with aggregations (SUM, COUNT, AVG, MAX, MIN)",
            "HAVING with post-aggregation filters",
            "ORDER BY with ASC/DESC",
            "DISTINCT",
            "LIMIT",
            "Expression parsing (comparison operators)",
            "Column-level lineage tracking",
            "Schema validation"
        ]
    
    def get_yaml_schema_example(self) -> Dict[str, Any]:
        """Return example YAML schema structure."""
        return {
            "constructed_table_name": "example_result",
            "dependencies": {
                "table1": {
                    "table_name": "actual_table_1",
                    "type": "source",
                    "source": "data_source"
                },
                "table2": {
                    "table_name": "actual_table_2", 
                    "type": "source",
                    "source": "data_source"
                }
            },
            "join_conditions": [
                "(\"table1\", \"table2\", \"table1.id\", \"table2.foreign_id\")"
            ],
            "join_type": "left",
            "filter_condition": [
                "table1.status == 'active'",
                "table2.amount > 100"
            ],
            "group_condition": [
                "table1.category"
            ],
            "aggregations": {
                "table2.amount": ["SUM(amount)", "COUNT(*)"]
            },
            "having_condition": [
                "SUM(table2.amount) > 1000"
            ],
            "select": {
                "table1.category": "category_name",
                "table2.amount": "total_amount"
            },
            "sort_condition": [
                "(total_amount, desc)"
            ],
            "distinct": True,
            "limit": 100
        }
    
    def __repr__(self) -> str:
        """String representation of YQL instance."""
        return f"YQL(yaml_path='{self.yaml_path}', tables={list(self.df_named_dict.keys())}, debug={self.debug})"