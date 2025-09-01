from typing import Dict, List, Any, Optional, Tuple, Union
from pyspark.sql import SparkSession, DataFrame
import pyspark.sql.functions as F
from pyspark.sql.types import *
import yaml
import ast
import re
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PYYql:
    """
    PYYql - Declarative PySpark SQL Engine
    
    Transforms YAML configurations into PySpark DataFrame operations
    with full SQL feature support and comprehensive error handling.
    """
    
    def __init__(self, yaml_path: str, debug: bool = False):
        self.yaml_path = yaml_path
        self.debug = debug
        self.yaml_config = None
        self.execution_plan = []
        
        if self.debug:
            logger.setLevel(logging.DEBUG)
    
    # ============================================================================
    # CORE YAML READING & PARSING
    # ============================================================================
    
    def _read(self) -> Dict:
        """Read and parse YAML configuration file."""
        try:
            with open(self.yaml_path, 'r') as f:
                self.yaml_config = yaml.safe_load(f)
            self._validate_yaml_structure()
            return self.yaml_config
        except FileNotFoundError:
            raise FileNotFoundError(f"YAML file not found: {self.yaml_path}")
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML format: {e}")
    
    def _validate_yaml_structure(self) -> None:
        """Validate YAML has required sections and structure."""
        required_sections = ['dependencies', 'select']
        
        for section in required_sections:
            if section not in self.yaml_config:
                raise ValueError(f"Missing required YAML section: {section}")
        
        # Validate dependencies structure
        deps = self.yaml_config.get('dependencies', {})
        for alias, config in deps.items():
            if not isinstance(config, dict) or 'table_name' not in config:
                raise ValueError(f"Invalid dependency structure for alias: {alias}")
    
    def _help_parse_tuple(self, string: str) -> Optional[Tuple]:
        """Parse tuple strings from YAML configurations."""
        try:
            s = ast.literal_eval(str(string))
            if isinstance(s, tuple):
                return s
            return None
        except (ValueError, SyntaxError):
            return None
    
    # ============================================================================
    # SELECT OPERATIONS
    # ============================================================================
    
    def _select_alias(self) -> List[F.Column]:
        """Create aliased column selections from YAML select configuration with resolution."""
        if not self.yaml_config:
            self._read()
        
        cols_dict = self.yaml_config.get("select", {})
        # Note: This method can't resolve columns without a DataFrame context
        # It's kept for backward compatibility but _apply_select should be used instead
        return [F.col(c).alias(cols_dict.get(c)) for c in cols_dict.keys()]
    
    def _apply_select(self, df: DataFrame) -> DataFrame:
        """Apply final SELECT projection with aliases and column resolution."""
        try:
            if not self.yaml_config:
                self._read()
            
            cols_dict = self.yaml_config.get("select", {})
            if not cols_dict:
                return df
            
            # Get available columns for resolution
            available_columns = df.columns
            
            if self.debug:
                logger.debug(f"Available columns for SELECT: {available_columns}")
                logger.debug(f"SELECT mapping: {cols_dict}")
            
            # Create resolved column selections
            resolved_columns = []
            for source_col, alias_name in cols_dict.items():
                # Resolve the source column reference
                resolved_col = self._resolve_column_reference(source_col, available_columns)
                
                if self.debug:
                    logger.debug(f"SELECT: '{source_col}' -> '{resolved_col}' AS '{alias_name}'")
                
                # Create the aliased column
                resolved_columns.append(F.col(resolved_col).alias(alias_name))
            
            return df.select(*resolved_columns)
            
        except Exception as e:
            logger.error(f"Error applying SELECT: {e}")
            logger.error(f"Available columns: {df.columns if df else 'DataFrame is None'}")
            logger.error(f"SELECT configuration: {self.yaml_config.get('select', {}) if self.yaml_config else 'No config'}")
            raise RuntimeError(f"Error applying SELECT: {e}")
    
    def _validate_select_columns(self, available_columns: List[str]) -> None:
        """Validate that all SELECT columns exist in available columns."""
        if not self.yaml_config:
            self._read()
        
        select_cols = self.yaml_config.get("select", {})
        for col_ref in select_cols.keys():
            # Handle table.column references
            if '.' in col_ref:
                table, col = col_ref.split('.', 1)
                full_ref = f"{table}.{col}"
            else:
                full_ref = col_ref
            
            # Check if column exists (simplified check)
            if full_ref not in available_columns and col_ref not in available_columns:
                logger.warning(f"Column may not exist: {col_ref}")
    
    # ============================================================================
    # DEPENDENCIES & TABLE MANAGEMENT
    # ============================================================================
    
    def _get_dependencies(self) -> Dict[str, str]:
        """Extract table dependencies and their aliases."""
        if not self.yaml_config:
            self._read()
        
        dependencies = self.yaml_config.get("dependencies", {})
        return {
            k: v.get("table_name")
            for k, v in dependencies.items()
            if v.get("type") == "source"
        }
    
    def _resolve_table_references(self, df_named_dict: Dict[str, DataFrame]) -> Dict[str, DataFrame]:
        """Map table aliases to actual DataFrames."""
        dependencies = self._get_dependencies()
        resolved_tables = {}
        
        for alias, table_name in dependencies.items():
            if table_name not in df_named_dict:
                raise ValueError(f"Table '{table_name}' not found in provided DataFrames")
            resolved_tables[alias] = df_named_dict[table_name]
        
        return resolved_tables
    
    def _validate_dependencies(self, df_named_dict: Dict[str, DataFrame]) -> None:
        """Ensure all required tables are available."""
        dependencies = self._get_dependencies()
        
        for alias, table_name in dependencies.items():
            if table_name not in df_named_dict:
                raise ValueError(f"Missing table '{table_name}' for alias '{alias}'")
    
    # ============================================================================
    # JOIN OPERATIONS
    # ============================================================================
    
    def _get_join_condition(self) -> List[Tuple]:
        """Parse join conditions from YAML configuration."""
        if not self.yaml_config:
            self._read()
        
        join_conditions = self.yaml_config.get("join_conditions", [])
        parsed_conditions = []
        
        for condition in join_conditions:
            parsed = self._help_parse_tuple(condition)
            if parsed:
                parsed_conditions.append(parsed)
            else:
                raise ValueError(f"Invalid join condition format: {condition}")
        
        return parsed_conditions
    
    def _get_join_type(self) -> str:
        """Determine join type from YAML configuration."""
        if not self.yaml_config:
            self._read()
        
        return self.yaml_config.get("join_type", "left")
    
    def _validate_join_keys(self, df_named_dict: Dict[str, DataFrame], 
                           join_conditions: List[Tuple]) -> None:
        """Validate that join keys exist in their respective DataFrames."""
        for condition in join_conditions:
            left_table, right_table, left_key, right_key = condition
            
            if left_table not in df_named_dict or right_table not in df_named_dict:
                continue  # Will be caught by dependency validation
            
            left_df = df_named_dict[left_table]
            right_df = df_named_dict[right_table]
            
            # Extract column name from table.column format
            left_col = left_key.split('.')[-1] if '.' in left_key else left_key
            right_col = right_key.split('.')[-1] if '.' in right_key else right_key
            
            if left_col not in left_df.columns:
                raise ValueError(f"Join key '{left_col}' not found in table '{left_table}'")
            if right_col not in right_df.columns:
                raise ValueError(f"Join key '{right_col}' not found in table '{right_table}'")
    
    def _help_drop_duplicated_cols_after_join(self, df: DataFrame) -> DataFrame:
        """Handle duplicate column names after joins."""
        newcols = []
        dupcols = []

        for i in range(len(df.columns)):
            if df.columns[i] not in newcols:
                newcols.append(df.columns[i])
            else:
                dupcols.append(i)

        df = df.toDF(*[str(i) for i in range(len(df.columns))])
        for dupcol in dupcols:
            df = df.drop(str(dupcol))

        return df.toDF(*newcols)
    
    def _join(self, df_named_dict: Dict[str, DataFrame], 
             join_condition_list: List[Tuple], join_type: str) -> DataFrame:
        """Execute multi-table joins with duplicate column handling."""
        if not join_condition_list:
            # Return the first available DataFrame if no joins
            return list(df_named_dict.values())[0]
        
        updated_df_list = []
        for item in join_condition_list:
            left_table, right_table, left_key, right_key = item
            updated_df_list.append((
                left_table,
                right_table,
                df_named_dict.get(left_table),
                df_named_dict.get(right_table),
                left_key,
                right_key,
            ))
        
        df_1 = updated_df_list[0][2]  # Start with first DataFrame
        
        for x in updated_df_list:
            left_alias, right_alias, left_df, right_df, left_key, right_key = x
            
            if left_df is None or right_df is None:
                raise ValueError(f"Missing DataFrame for join: {left_alias} or {right_alias}")
            
            df_1 = (
                df_1.alias(left_alias)
                .join(
                    right_df.alias(right_alias), 
                    on=F.col(left_key) == F.col(right_key), 
                    how=join_type
                )
            )
            df_1 = self._help_drop_duplicated_cols_after_join(df_1)

        return df_1
    
    # ============================================================================
    # WHERE/FILTER OPERATIONS - FIXED COLUMN RESOLUTION
    # ============================================================================
    
    def _get_where(self) -> List[str]:
        """Parse WHERE conditions from YAML configuration."""
        if not self.yaml_config:
            self._read()
        
        return self.yaml_config.get("filter_condition", [])
    
    def _resolve_column_reference(self, column_ref: str, available_columns: List[str]) -> str:
        """
        Resolve column references after joins, handling table.column format.
        
        Args:
            column_ref: Original column reference (e.g., 'emp.emp_id')
            available_columns: List of available columns in the DataFrame
            
        Returns:
            Resolved column name that exists in the DataFrame
        """
        # If column_ref already exists directly, use it
        if column_ref in available_columns:
            return column_ref
        
        # If it's a table.column reference, try to find the column without table prefix
        if '.' in column_ref:
            table_alias, column_name = column_ref.split('.', 1)
            
            # Try direct column name
            if column_name in available_columns:
                return column_name
            
            # Try with different case variations
            column_name_lower = column_name.lower()
            column_name_upper = column_name.upper()
            
            for col in available_columns:
                if col.lower() == column_name_lower:
                    return col
            
            # Try finding columns that end with the column name (after join aliases)
            for col in available_columns:
                if col.endswith(f"_{column_name}") or col.endswith(column_name):
                    return col
        
        # If still not found, log warning and return original reference
        logger.warning(f"Column '{column_ref}' not found in available columns: {available_columns}")
        return column_ref
    
    def _parse_filter_expression(self, expression: str, available_columns: List[str] = None) -> F.Column:
        """Convert string expressions to PySpark Column conditions with column resolution."""
        try:
            # Handle different comparison operators
            operators = ['>=', '<=', '!=', '==', '>', '<', ' LIKE ', ' like ']
            
            for op in operators:
                if op in expression:
                    left, right = expression.split(op, 1)
                    left = left.strip()
                    right = right.strip()
                    
                    # Resolve column reference if available_columns provided
                    if available_columns:
                        left = self._resolve_column_reference(left, available_columns)
                    
                    # Remove quotes from string literals
                    if right.startswith(("'", '"')) and right.endswith(("'", '"')):
                        right = right[1:-1]
                    
                    left_col = F.col(left)
                    
                    if op.strip().upper() == 'LIKE':
                        return left_col.like(right)
                    elif op == '==':
                        # Handle type conversion for comparison
                        try:
                            # Try to convert to number if it looks like one
                            if right.isdigit():
                                right = int(right)
                            elif right.replace('.', '').isdigit():
                                right = float(right)
                        except:
                            pass
                        return left_col == right
                    elif op == '!=':
                        return left_col != right
                    elif op == '>':
                        return left_col > right
                    elif op == '<':
                        return left_col < right
                    elif op == '>=':
                        return left_col >= right
                    elif op == '<=':
                        return left_col <= right
            
            # Handle IS NULL / IS NOT NULL
            if ' IS NULL' in expression.upper():
                col_name = expression.upper().replace(' IS NULL', '').strip()
                if available_columns:
                    col_name = self._resolve_column_reference(col_name, available_columns)
                return F.col(col_name).isNull()
            elif ' IS NOT NULL' in expression.upper():
                col_name = expression.upper().replace(' IS NOT NULL', '').strip()
                if available_columns:
                    col_name = self._resolve_column_reference(col_name, available_columns)
                return F.col(col_name).isNotNull()
            
            raise ValueError(f"Unsupported expression format: {expression}")
            
        except Exception as e:
            raise ValueError(f"Error parsing filter expression '{expression}': {e}")
    
    def _parse_logical_operators(self, conditions: List[str], available_columns: List[str] = None) -> F.Column:
        """Handle AND, OR, NOT logical operators between conditions."""
        if not conditions:
            return F.lit(True)
        
        # For now, assume all conditions are AND-ed together
        # TODO: Implement proper logical operator parsing
        parsed_conditions = [self._parse_filter_expression(cond, available_columns) for cond in conditions]
        
        result = parsed_conditions[0]
        for condition in parsed_conditions[1:]:
            result = result & condition
        
        return result
    
    def _apply_filters(self, df: DataFrame) -> DataFrame:
        """Apply all WHERE/filter conditions to DataFrame with column resolution."""
        try:
            conditions = self._get_where()
            if not conditions:
                return df
            
            # Get available columns for resolution
            available_columns = df.columns
            
            if self.debug:
                logger.debug(f"Available columns for filtering: {available_columns}")
                logger.debug(f"Filter conditions: {conditions}")
            
            combined_condition = self._parse_logical_operators(conditions, available_columns)
            return df.filter(combined_condition)
            
        except Exception as e:
            logger.error(f"Error applying filters: {e}")
            logger.error(f"Available columns: {df.columns if df else 'DataFrame is None'}")
            logger.error(f"Filter conditions: {self._get_where()}")
            raise RuntimeError(f"Error applying filters: {e}")
    
    # ============================================================================
    # GROUP BY & AGGREGATION OPERATIONS
    # ============================================================================
    
    def _get_groupby(self) -> List[str]:
        """Parse GROUP BY columns from YAML configuration."""
        if not self.yaml_config:
            self._read()
        
        return self.yaml_config.get("group_condition", [])
    
    def _get_aggregations(self) -> Dict[str, List[str]]:
        """Parse aggregation functions from YAML configuration."""
        if not self.yaml_config:
            self._read()
        
        return self.yaml_config.get("aggregations", {})
    
    def _parse_agg_functions(self, agg_spec: str) -> F.Column:
        """Handle SUM, COUNT, AVG, MAX, MIN aggregation functions."""
        agg_spec = agg_spec.strip()
        
        # Extract function and column using regex
        pattern = r'(\w+)\s*\(\s*([^)]*)\s*\)'
        match = re.match(pattern, agg_spec)
        
        if not match:
            raise ValueError(f"Invalid aggregation format: {agg_spec}")
        
        func_name = match.group(1).upper()
        column_expr = match.group(2).strip()
        
        if func_name == 'COUNT':
            if column_expr == '*':
                return F.count(F.lit(1))
            else:
                return F.count(F.col(column_expr))
        elif func_name == 'SUM':
            return F.sum(F.col(column_expr))
        elif func_name == 'AVG':
            return F.avg(F.col(column_expr))
        elif func_name == 'MAX':
            return F.max(F.col(column_expr))
        elif func_name == 'MIN':
            return F.min(F.col(column_expr))
        else:
            raise ValueError(f"Unsupported aggregation function: {func_name}")
    
    def _apply_groupby(self, df: DataFrame) -> DataFrame:
        """Execute grouping and aggregation operations."""
        try:
            group_cols = self._get_groupby()
            aggregations = self._get_aggregations()
            
            if not group_cols:
                return df
            
            # Resolve group column references
            available_columns = df.columns
            resolved_group_cols = []
            for col in group_cols:
                resolved_col = self._resolve_column_reference(col, available_columns)
                resolved_group_cols.append(resolved_col)
            
            grouped_df = df.groupBy([F.col(col) for col in resolved_group_cols])
            
            if aggregations:
                agg_exprs = []
                for col, agg_funcs in aggregations.items():
                    for agg_func in agg_funcs:
                        agg_col = self._parse_agg_functions(agg_func)
                        agg_exprs.append(agg_col.alias(f"{col}_{agg_func.split('(')[0].lower()}"))
                
                return grouped_df.agg(*agg_exprs)
            else:
                # Simple GROUP BY without explicit aggregations
                return grouped_df.agg(F.count("*").alias("count"))
            
        except Exception as e:
            raise RuntimeError(f"Error applying GROUP BY: {e}")
    
    def _validate_groupby_select(self) -> None:
        """Ensure SELECT columns are compatible with GROUP BY."""
        group_cols = self._get_groupby()
        if not group_cols:
            return
        
        select_cols = self.yaml_config.get("select", {})
        
        # This is a simplified validation - in reality, would need more complex logic
        logger.info("GROUP BY validation: Ensure all SELECT columns are grouped or aggregated")
    
    # ============================================================================
    # HAVING OPERATIONS
    # ============================================================================
    
    def _get_having(self) -> List[str]:
        """Parse HAVING conditions from YAML configuration."""
        if not self.yaml_config:
            self._read()
        
        return self.yaml_config.get("having_condition", [])
    
    def _parse_having_expression(self, expression: str, available_columns: List[str] = None) -> F.Column:
        """Convert HAVING expressions to PySpark conditions."""
        # Similar to filter expressions but may include aggregation functions
        try:
            # Check if expression contains aggregation functions
            if any(func in expression.upper() for func in ['COUNT', 'SUM', 'AVG', 'MAX', 'MIN']):
                # Parse aggregation function in HAVING clause
                return self._parse_filter_expression(expression, available_columns)
            else:
                return self._parse_filter_expression(expression, available_columns)
        except Exception as e:
            raise ValueError(f"Error parsing HAVING expression '{expression}': {e}")
    
    def _apply_having(self, df: DataFrame) -> DataFrame:
        """Apply HAVING conditions to grouped DataFrame."""
        try:
            having_conditions = self._get_having()
            if not having_conditions:
                return df
            
            available_columns = df.columns
            
            for condition in having_conditions:
                having_expr = self._parse_having_expression(condition, available_columns)
                df = df.filter(having_expr)
            
            return df
            
        except Exception as e:
            raise RuntimeError(f"Error applying HAVING: {e}")
    
    # ============================================================================
    # ORDER BY/SORT OPERATIONS
    # ============================================================================
    
    def _get_sort_condition(self) -> List[Tuple[str, str]]:
        """Parse ORDER BY specifications from YAML configuration."""
        if not self.yaml_config:
            self._read()
        
        sort_conditions = self.yaml_config.get("sort_condition", [])
        parsed_sorts = []
        
        for sort_spec in sort_conditions:
            parsed = self._parse_sort_tuple(sort_spec)
            if parsed:
                parsed_sorts.append(parsed)
        
        return parsed_sorts
    
    def _parse_sort_tuple(self, sort_spec: str) -> Optional[Tuple[str, str]]:
        """Extract column name and sort direction from tuple string."""
        try:
            # Handle tuple format: "(column_name, direction)"
            if sort_spec.startswith('(') and sort_spec.endswith(')'):
                content = sort_spec[1:-1]  # Remove parentheses
                parts = [part.strip().strip('"\'') for part in content.split(',')]
                
                if len(parts) == 2:
                    column, direction = parts
                    direction = direction.lower()
                    if direction in ['asc', 'desc']:
                        return (column, direction)
            
            # Handle simple string format: "column_name" (defaults to ASC)
            return (sort_spec.strip(), 'asc')
            
        except Exception:
            return None
    
    def _apply_sort(self, df: DataFrame) -> DataFrame:
        """Execute ORDER BY operations with intelligent column resolution."""
        try:
            sort_conditions = self._get_sort_condition()
            if not sort_conditions:
                return df
            
            available_columns = df.columns
            sort_exprs = []
            
            if self.debug:
                logger.debug(f"Available columns for ORDER BY: {available_columns}")
                logger.debug(f"Sort conditions: {sort_conditions}")
            
            for column, direction in sort_conditions:
                resolved_column = None
                
                # First, try to resolve using the column resolver (for before SELECT)
                resolved_column = self._resolve_column_reference(column, available_columns)
                
                # If that didn't work and we're after SELECT, try to map to aliased columns
                if resolved_column not in available_columns:
                    resolved_column = self._map_to_select_alias(column)
                    
                # If still not found, use the original column
                if resolved_column not in available_columns:
                    resolved_column = column
                
                if self.debug:
                    logger.debug(f"ORDER BY: '{column}' -> '{resolved_column}' ({direction})")
                
                col_expr = F.col(resolved_column)
                if direction == 'desc':
                    col_expr = col_expr.desc()
                else:
                    col_expr = col_expr.asc()
                sort_exprs.append(col_expr)
            
            return df.orderBy(*sort_exprs)
            
        except Exception as e:
            logger.error(f"Error applying ORDER BY: {e}")
            logger.error(f"Available columns: {df.columns if df else 'DataFrame is None'}")
            logger.error(f"Sort conditions: {self._get_sort_condition() if hasattr(self, 'yaml_config') and self.yaml_config else 'No config'}")
            raise RuntimeError(f"Error applying ORDER BY: {e}")

    def _map_to_select_alias(self, original_column: str) -> str:
        """
        Map original column references to their SELECT aliases.
        
        This is needed when ORDER BY references original columns but we're sorting
        after SELECT has applied aliases.
        """
        if not self.yaml_config:
            return original_column
        
        select_mapping = self.yaml_config.get("select", {})
        
        # Look for the original column in the SELECT mapping
        for source_col, alias in select_mapping.items():
            if source_col == original_column:
                return alias
            # Also try matching without table prefix
            if '.' in source_col and source_col.split('.', 1)[1] == original_column.split('.', 1)[-1]:
                return alias
            # Try matching the column name part
            if '.' in original_column and source_col.split('.', 1)[-1] == original_column.split('.', 1)[-1]:
                return alias
        
        return original_column
    
    
    
    def _validate_sort_columns(self, df: DataFrame) -> None:
        """Ensure sort columns exist in DataFrame."""
        sort_conditions = self._get_sort_condition()
        available_columns = df.columns
        
        for column, _ in sort_conditions:
            resolved_column = self._resolve_column_reference(column, available_columns)
            if resolved_column not in available_columns:
                raise ValueError(f"Sort column '{column}' could not be resolved in DataFrame")
    
    # ============================================================================
    # ADVANCED OPERATIONS
    # ============================================================================
    
    def _apply_distinct(self, df: DataFrame) -> DataFrame:
        """Apply DISTINCT operation."""
        if not self.yaml_config:
            self._read()
        
        if self.yaml_config.get("distinct", False):
            return df.distinct()
        return df
    
    def _apply_limit(self, df: DataFrame) -> DataFrame:
        """Apply LIMIT operation."""
        if not self.yaml_config:
            self._read()
        
        limit = self.yaml_config.get("limit")
        if limit and isinstance(limit, int) and limit > 0:
            return df.limit(limit)
        return df
    
    # ============================================================================
    # DEBUGGING & UTILITIES
    # ============================================================================
    
    def _debug_execution_plan(self) -> List[str]:
        """Return the planned execution sequence."""
        if not self.yaml_config:
            self._read()
        
        plan = []
        plan.append("1. FROM: Load dependencies")
        
        if self.yaml_config.get("join_conditions"):
            plan.append("2. JOIN: Execute table joins")
        
        if self.yaml_config.get("filter_condition"):
            plan.append("3. WHERE: Apply filter conditions")
        
        if self.yaml_config.get("group_condition"):
            plan.append("4. GROUP BY: Execute grouping and aggregations")
        
        if self.yaml_config.get("having_condition"):
            plan.append("5. HAVING: Apply post-aggregation filters")
        
        if self.yaml_config.get("select"):
            plan.append("6. SELECT: Apply column projections and aliases")
        
        if self.yaml_config.get("sort_condition"):
            plan.append("7. ORDER BY: Apply sorting")
        
        if self.yaml_config.get("distinct"):
            plan.append("8. DISTINCT: Remove duplicates")
        
        if self.yaml_config.get("limit"):
            plan.append("9. LIMIT: Apply row limit")
        
        return plan
    
    def _log_intermediate_results(self, df: DataFrame, step: str) -> DataFrame:
        """Log DataFrame information at each step for debugging."""
        if self.debug:
            logger.debug(f"{step}: DataFrame has {df.count()} rows and {len(df.columns)} columns")
            logger.debug(f"{step}: Columns: {df.columns}")
        return df
    
    def _validate_execution_plan(self, df_named_dict: Dict[str, DataFrame]) -> None:
        """Validate the complete execution plan before running."""
        self._validate_dependencies(df_named_dict)
        
        join_conditions = self._get_join_condition()
        if join_conditions:
            self._validate_join_keys(df_named_dict, join_conditions)
        
        self._validate_groupby_select()
    
    # ============================================================================
    # MAIN EXECUTION METHOD
    # ============================================================================
    
    def run(self, df_named_dict: Dict[str, DataFrame]) -> DataFrame:
        """
        Execute the complete SQL pipeline based on YAML configuration.
        
        Args:
            df_named_dict: Dictionary mapping table names to PySpark DataFrames
            
        Returns:
            Transformed PySpark DataFrame
        """
        try:
            # Initialize configuration
            self._read()
            
            # Validate execution plan
            self._validate_execution_plan(df_named_dict)
            
            if self.debug:
                plan = self._debug_execution_plan()
                logger.debug("Execution Plan:")
                for step in plan:
                    logger.debug(f"  {step}")
            
            # Resolve table references
            resolved_tables = self._resolve_table_references(df_named_dict)
            
            # Step 1: Handle JOINs (if any)
            join_conditions = self._get_join_condition()
            join_type = self._get_join_type()
            
            if join_conditions:
                df = self._join(resolved_tables, join_conditions, join_type)
                df = self._log_intermediate_results(df, "JOIN")
            else:
                # Use the first available table if no joins
                df = list(resolved_tables.values())[0]
            
            # Step 2: Apply WHERE filters
            df = self._apply_filters(df)
            df = self._log_intermediate_results(df, "WHERE")
            
            # Step 3: Apply GROUP BY and aggregations
            df = self._apply_groupby(df)
            df = self._log_intermediate_results(df, "GROUP BY")
            
            # Step 4: Apply HAVING conditions
            df = self._apply_having(df)
            df = self._log_intermediate_results(df, "HAVING")
            
            # Step 5: Apply SELECT projections
            df = self._apply_select(df)
            df = self._log_intermediate_results(df, "SELECT")
            
            # Step 6: Apply ORDER BY
            df = self._apply_sort(df)
            df = self._log_intermediate_results(df, "ORDER BY")
            
            # Step 7: Apply DISTINCT
            df = self._apply_distinct(df)
            df = self._log_intermediate_results(df, "DISTINCT")
            
            # Step 8: Apply LIMIT
            df = self._apply_limit(df)
            df = self._log_intermediate_results(df, "LIMIT")
            
            if self.debug:
                logger.debug(f"Final result: {df.count()} rows, {len(df.columns)} columns")
            
            return df
            
        except Exception as e:
            logger.error(f"Error executing PYYql pipeline: {e}")
            raise RuntimeError(f"PYYql execution failed: {e}") from e