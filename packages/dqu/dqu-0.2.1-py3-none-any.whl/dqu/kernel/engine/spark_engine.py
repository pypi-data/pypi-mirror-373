from functools import reduce
from typing import List, Dict, Any, Optional, Tuple, Callable, Union
from pyspark.sql import DataFrame
from pyspark.sql.functions import col, udf, struct
from pyspark.sql.types import *
from dqu.kernel.engine.base_engine import BaseEngine
from dqu.utils.time_utils import parse_duration_to_timedelta
import json
from datetime import datetime, timezone

class SparkEngine(BaseEngine):

    def run_dup_check(self, columns:List[str], evaluation: str="basic")-> Union[str, Tuple[str, DataFrame]]:
        """
        Check for duplicate rows based on specified columns.

        Args:
            columns: List of column names to check for duplicates.
            evaluation: "basic" returns JSON, "advanced" returns (JSON, DataFrame).

        Returns:
            JSON string (and DataFrame if advanced).
        """
        grouped = self.df.groupBy(columns).count().filter("count > 1")
        duplicates = self.df.join(grouped, on=columns, how='inner')
        total = self.df.count()
        failed = duplicates.count()
        result_dict = {
            "status": "Success" if failed == 0 else "Failed",
            "dqu_check_type": "duplicate_check",
            "dqu_total_count": total,
            "dqu_failed_count": failed,
            "dqu_passed_count": total - failed,
            "run_timestamp": datetime.now(timezone.utc).isoformat(),  # ISO UTC format
            "run_id": self.run_id
        }
        if evaluation == "advanced":
            return json.dumps(result_dict, indent=2), duplicates
        return json.dumps(result_dict, indent=2)

    def run_empty_check(self, columns: List[str], evaluation:str="basic")-> Union[str, Tuple[str, DataFrame]]:
        """
        Check for empty (null or blank) values in specified columns.

        Args:
            columns: List of column names to check for empties.
            evaluation: "basic" returns JSON, "advanced" returns (JSON, DataFrame).

        Returns:
            JSON string (and DataFrame if advanced).
        """
        conditions = [col(c).isNull() | (col(c) == '') for c in columns]
        combined = reduce(lambda a, b: a | b, conditions)
        empty_rows = self.df.filter(combined)
        total = self.df.count()
        failed = empty_rows.count()
        result_dict = {
            "status": "Success" if failed == 0 else "Failed",
            "dqu_check_type": "empty_check",
            "dqu_total_count": total,
            "dqu_failed_count": failed,
            "dqu_passed_count": total - failed,
            "run_timestamp": datetime.now(timezone.utc).isoformat(),
            "run_id": self.run_id
        }
        if evaluation == "advanced":
            return json.dumps(result_dict, indent=2), empty_rows
        return json.dumps(result_dict, indent=2)
    
    def run_unique_check(self, column:str, evaluation:str="basic")-> Union[str, Tuple[str, DataFrame]]:
        """
        Check for uniqueness in a specified column.

        Args:
            column: Column name to check for uniqueness.
            evaluation: "basic" returns JSON, "advanced" returns (JSON, DataFrame).

        Returns:
            JSON string (and DataFrame if advanced).
        """
        grouped = self.df.groupBy(column).count().filter("count > 1")
        non_unique = self.df.join(grouped, on=column, how='inner')
        total = self.df.count()
        failed = non_unique.count()
        result_dict = {
            "status": "Success" if failed == 0 else "Failed",
            "dqu_check_type": "unique_check",
            "dqu_total_count": total,
            "dqu_failed_count": failed,
            "dqu_passed_count": total - failed,
            "run_timestamp": datetime.now(timezone.utc).isoformat(),
            "run_id": self.run_id
        }
        if evaluation == "advanced":
            return json.dumps(result_dict, indent=2), non_unique
        return json.dumps(result_dict, indent=2)
    
    def run_dtype_check(self, column_types: Dict[str, str], evaluation:str="basic")-> Union[str, Tuple[str, Optional[DataFrame]]]:
        """
        Check if columns match expected data types.

        Args:
            column_types: Dict mapping column names to expected Spark dtypes (e.g., 'string', 'int').
            evaluation: "basic" returns JSON, "advanced" returns (JSON, DataFrame).

        Returns:
            JSON string (and DataFrame if advanced).
        """
        import json
        from datetime import datetime, timezone
        from pyspark.sql.types import (
            IntegerType, LongType, FloatType, DoubleType, StringType, BooleanType, TimestampType, DateType
        )
        from pyspark.sql.functions import col

        spark_type_map = {
            "int": IntegerType,
            "integer": IntegerType,
            "bigint": LongType,
            "long": LongType,
            "float": FloatType,
            "double": DoubleType,
            "str": StringType,
            "string": StringType,
            "bool": BooleanType,
            "boolean": BooleanType,
            "timestamp": TimestampType,
            "datetime": TimestampType,
            "date": DateType,
        }

        failed_df = None
        for col_name, expected_dtype in column_types.items():
            expected_dtype_lower = expected_dtype.lower()
            spark_type_cls = spark_type_map.get(expected_dtype_lower)
            if spark_type_cls is None:
                fail_col_df = self.df
            else:
                casted = self.df.withColumn(f"__cast_{col_name}", col(col_name).cast(spark_type_cls()))
                fail_col_df = casted.filter(
                    col(col_name).isNotNull() & col(f"__cast_{col_name}").isNull()
                ).drop(f"__cast_{col_name}")

            if failed_df is None:
                failed_df = fail_col_df
            else:
                failed_df = failed_df.unionByName(fail_col_df).dropDuplicates()

        total = self.df.count()
        failed = failed_df.count() if failed_df is not None else 0
        result_dict = {
            "status": "Success" if failed == 0 else "Failed",
            "dqu_check_type": "dtype_check",
            "dqu_total_count": total,
            "dqu_failed_count": failed,
            "dqu_passed_count": total - failed,
            "run_timestamp": datetime.now(timezone.utc).isoformat(),
            "run_id": self.run_id
        }

        if evaluation == "advanced":
            return json.dumps(result_dict, indent=2), failed_df
        return json.dumps(result_dict, indent=2)
    
    def run_stringformat_check(
        self, 
        column: str, 
        pattern: str, 
        evaluation: str = "basic"
    ) -> Union[str, Tuple[str, DataFrame]]:
        """
        Check if string values in a column match a regex pattern.

        Args:
            column: Column name to check.
            pattern: Regex pattern to match.
            evaluation: "basic" returns JSON, "advanced" returns (JSON, DataFrame).

        Returns:
            JSON string (and DataFrame if advanced).
        """
        import re
        regex_udf = (lambda value: not bool(re.match(pattern, str(value))) if value is not None else True)
        from pyspark.sql.functions import udf
        from pyspark.sql.types import BooleanType

        mismatch_udf = udf(regex_udf, BooleanType())
        mismatches = self.df.filter(mismatch_udf(col(column)))

        total = self.df.count()
        failed = mismatches.count()

        result_dict = {
            "status": "Success" if failed == 0 else "Failed",
            "dqu_check_type": "stringformat_check",
            "dqu_total_count": total,
            "dqu_failed_count": failed,
            "dqu_passed_count": total - failed,
            "run_timestamp": datetime.now(timezone.utc).isoformat(),
            "run_id": self.run_id
        }
        if evaluation == "advanced":
            return json.dumps(result_dict, indent=2), mismatches
        return json.dumps(result_dict, indent=2)
    
    def run_schemavalidation_check(
        self, 
        expected_schema: Dict[str, str]
    ) -> str:
        """
        Validate DataFrame schema against expected schema.

        Args:
            expected_schema: Dict mapping column names to expected Spark dtypes.

        Returns:
            JSON string with schema validation results.
        """
        df = self.df
        schema_fields = {f.name: f.dataType for f in df.schema.fields}

        missing_columns = [col for col in expected_schema if col not in schema_fields]
        mismatched_types = {}

        spark_type_mapping = {
            "int": IntegerType(),
            "float": FloatType(),
            "double": DoubleType(),
            "string": StringType(),
            "long": LongType(),
            "boolean": BooleanType(),
            "timestamp": TimestampType(),
            "date": DateType()
        }

        for col, expected_dtype in expected_schema.items():
            if col not in schema_fields:
                continue

            actual_type = schema_fields[col]
            expected_type = spark_type_mapping.get(expected_dtype.lower())

            if expected_type is None:
                mismatched_types[col] = {
                    "expected": f"(Unsupported expected type: {expected_dtype})",
                    "actual": actual_type.simpleString()
                }
                continue

            if not isinstance(actual_type, type(expected_type)):
                mismatched_types[col] = {
                    "expected": expected_type.simpleString(),
                    "actual": actual_type.simpleString()
                }

        status = "Success" if not missing_columns and not mismatched_types else "Failed"

        result_dict = {
            "status": status,
            "dqu_check_type": "schemavalidation_check",
            "missing_columns": missing_columns,
            "type_mismatches": mismatched_types,
            "dqu_total_count": df.count(),
            "dqu_failed_count": len(missing_columns) + len(mismatched_types),
            "dqu_passed_count": len(expected_schema) - len(missing_columns) - len(mismatched_types),
            "run_timestamp": datetime.now(timezone.utc).isoformat(),
            "run_id": self.run_id
        }
        return json.dumps(result_dict, indent=2)
    
    def run_range_check(
        self, 
        column: str, 
        min_val: Any, 
        max_val: Any, 
        evaluation: str = "basic"
    ) -> Union[str, Tuple[str, DataFrame]]:
        """
        Check if values in a column fall within a specified range.

        Args:
            column: Column name to check.
            min_val: Minimum allowed value.
            max_val: Maximum allowed value.
            evaluation: "basic" returns JSON, "advanced" returns (JSON, DataFrame).

        Returns:
            JSON string (and DataFrame if advanced).
        """
        df = self.df

        if column not in df.columns:
            raise ValueError(f"Column '{column}' not found in DataFrame.")

        invalid_df = df.filter((col(column) < min_val) | (col(column) > max_val))
        failed_count = invalid_df.count()
        total_count = df.count()
        passed_count = total_count - failed_count

        result_dict = {
            "status": "Success" if failed_count == 0 else "Failed",
            "dqu_check_type": "range_check",
            "column": column,
            "range": {"min": min_val, "max": max_val},
            "dqu_total_count": total_count,
            "dqu_failed_count": failed_count,
            "dqu_passed_count": passed_count,
            "run_timestamp": datetime.now(timezone.utc).isoformat(),
            "run_id": self.run_id
        }
        if evaluation == "advanced":
            return json.dumps(result_dict, indent=2), invalid_df
        return json.dumps(result_dict, indent=2)
    
    def run_categoricalvalues_check(
        self, 
        column: str, 
        allowed_values: List[Any], 
        evaluation: str = "basic"
    ) -> Union[str, Tuple[str, DataFrame]]:
        """
        Check if values in a column are within allowed categorical values.

        Args:
            column: Column name to check.
            allowed_values: List of allowed values.
            evaluation: "basic" returns JSON, "advanced" returns (JSON, DataFrame).

        Returns:
            JSON string (and DataFrame if advanced).
        """
        df = self.df

        if column not in df.columns:
            raise ValueError(f"Column '{column}' not found in DataFrame.")

        invalid_df = df.filter(~col(column).isin(allowed_values))
        failed_count = invalid_df.count()
        total_count = df.count()
        passed_count = total_count - failed_count

        result_dict = {
            "status": "Success" if failed_count == 0 else "Failed",
            "dqu_check_type": "categoricalvalues_check",
            "column": column,
            "allowed_values": allowed_values,
            "dqu_total_count": total_count,
            "dqu_failed_count": failed_count,
            "dqu_passed_count": passed_count,
            "run_timestamp": datetime.now(timezone.utc).isoformat(),
            "run_id": self.run_id
        }
        if evaluation == "advanced":
            return json.dumps(result_dict, indent=2), invalid_df
        return json.dumps(result_dict, indent=2)
    
    def run_statisticaldistribution_check(
        self, 
        column: str, 
        mode: str, 
        reference_stats: Optional[Dict[str, float]] = None, 
        tolerance: float = 0.05
    ) -> str:
        """
        Check statistical distribution of a column for drift or label balance.

        Args:
            column: Column name to check.
            mode: "feature_drift" or "label_balance".
            reference_stats: Reference statistics for drift check.
            tolerance: Allowed tolerance for drift.

        Returns:
            JSON string with statistical check results.
        """
        from pyspark.sql.functions import mean, stddev, col
        df = self.df

        if column not in df.columns:
            raise ValueError(f"Column '{column}' not found.")

        if mode == "feature_drift":
            stats = df.select(mean(col(column)).alias("mean"), stddev(col(column)).alias("std")).collect()[0]
            current_mean, current_std = stats["mean"], stats["std"]

            drift_mean = abs(current_mean - reference_stats["mean"])
            drift_std = abs(current_std - reference_stats["std"])
            passed = drift_mean <= tolerance and drift_std <= tolerance

            result_dict = {
                "status": "Success" if passed else "Failed",
                "dqu_check_type": "statisticaldistribution_check",
                "mode": "feature_drift",
                "column": column,
                "dqu_drift_mean": drift_mean,
                "dqu_drift_std": drift_std,
                "dqu_passed": passed,
                "run_timestamp": datetime.now(timezone.utc).isoformat(),
                "run_id": self.run_id
            }
            return json.dumps(result_dict, indent=2)

        elif mode == "label_balance":
            dist = df.groupBy(column).count()
            total = df.count()
            dist_dict = {row[column]: row["count"] / total for row in dist.collect()}
            max_class_ratio = max(dist_dict.values())
            passed = max_class_ratio <= 0.9

            result_dict = {
                "status": "Success" if passed else "Failed",
                "dqu_check_type": "statisticaldistribution_check",
                "mode": "label_balance",
                "column": column,
                "dqu_distribution": dist_dict,
                "dqu_passed": passed,
                "run_timestamp": datetime.now(timezone.utc).isoformat(),
                "run_id": self.run_id
            }
            return json.dumps(result_dict, indent=2)

        else:
            raise ValueError("Unsupported statistical check mode")

    def run_datafreshness_check(
        self, 
        column: str, 
        freshness_threshold: str
    ) -> str:
        """
        Check if the latest timestamp in a column is within the freshness threshold.

        Args:
            column: Column name to check (must be TimestampType).
            freshness_threshold: Freshness threshold as a duration string (e.g., '1d', '12h').

        Returns:
            JSON string with freshness check results.
        """
        from pyspark.sql.functions import max as spark_max, col
        from datetime import datetime
        df = self.df

        if column not in df.columns:
            raise ValueError(f"Column '{column}' not found.")

        spark_type = [f for f in df.schema.fields if f.name == column][0].dataType
        from pyspark.sql.types import TimestampType
        if not isinstance(spark_type, TimestampType):
            raise TypeError(f"Column '{column}' must be of TimestampType.")

        latest_timestamp = df.select(spark_max(col(column))).first()[0]
        freshness_cutoff = datetime.now() - parse_duration_to_timedelta(freshness_threshold)
        passed = latest_timestamp > freshness_cutoff

        result_dict = {
            "status": "Success" if passed else "Failed",
            "dqu_check_type": "datafreshness_check",
            "column": column,
            "latest_timestamp": str(latest_timestamp),
            "cutoff_timestamp": str(freshness_cutoff),
            "dqu_passed": passed,
            "run_timestamp": datetime.now(timezone.utc).isoformat(),
            "run_id": self.run_id
        }
        return json.dumps(result_dict, indent=2)
    
    def run_referential_integrity_check(
        self, 
        column: str, 
        reference_df: DataFrame, 
        reference_column: str, 
        evaluation: str = "basic"
    ) -> Union[str, Tuple[str, DataFrame]]:
        """
        Check referential integrity between a column and a reference DataFrame column.

        Args:
            column: Column in the main DataFrame.
            reference_df: Reference DataFrame.
            reference_column: Column in the reference DataFrame.
            evaluation: "basic" returns JSON, "advanced" returns (JSON, DataFrame).

        Returns:
            JSON string (and DataFrame if advanced).
        """
        from pyspark.sql.functions import col
        reference_keys = reference_df.select(reference_column).distinct()
        invalid_rows = self.df.join(reference_keys, self.df[column] == reference_keys[reference_column], "left_anti")
        total = self.df.count()
        failed = invalid_rows.count()
        result_dict = {
            "status": "Success" if failed == 0 else "Failed",
            "dqu_check_type": "referentialintegrity_check",
            "dqu_total_count": total,
            "dqu_failed_count": failed,
            "dqu_passed_count": total - failed,
            "run_timestamp": datetime.now(timezone.utc).isoformat(),
            "run_id": self.run_id
        }
        if evaluation == "advanced":
            return json.dumps(result_dict, indent=2), invalid_rows
        return json.dumps(result_dict, indent=2)
    
    def run_rowcount_check(
        self, 
        min_rows: Optional[int] = None, 
        max_rows: Optional[int] = None
    ) -> str:
        """
        Check if the number of rows is within the specified bounds.

        Args:
            min_rows: Minimum allowed number of rows.
            max_rows: Maximum allowed number of rows.

        Returns:
            JSON string with row count check results.
        """
        total = self.df.count()

        status = "Success"
        if (min_rows is not None and total < min_rows) or (max_rows is not None and total > max_rows):
            status = "Failed"

        result_dict = {
            "status": status,
            "dqu_check_type": "rowcount_check",
            "dqu_total_count": total,
            "min_required": min_rows,
            "max_allowed": max_rows,
            "run_timestamp": datetime.now(timezone.utc).isoformat(),
            "run_id": self.run_id
        }
        return json.dumps(result_dict, indent=2)

    def run_custom_check(
        self, 
        column: Optional[str], 
        func: Callable[[Any], bool], 
        evaluation: str = "basic"
    ) -> Union[str, Tuple[str, DataFrame]]:
        """
        Run a custom check using a user-provided function.

        Args:
            column: Column name to apply the function to. If None, applies to each row as a dict.
            func: Callable that returns True if value/row passes, False otherwise.
            evaluation: "basic" returns JSON, "advanced" returns (JSON, DataFrame).

        Returns:
            JSON string (and DataFrame if advanced).
        """
        total = self.df.count()

        if column:
            # column-level UDF
            spark_udf = udf(func, BooleanType())
            failed_df = self.df.filter(~spark_udf(col(column)))
            check = "custom_check_column"
        else:
            # row-level UDF: pack entire row into a struct, then as dict
            spark_udf = udf(
                lambda r: func(r.asDict()),
                BooleanType()
            )
            failed_df = self.df.filter(~spark_udf(struct(*self.df.columns)))
            check = "custom_check_row"

        failed = failed_df.count()

        result_dict = {
            "status": "Success" if failed == 0 else "Failed",
            "dqu_check_type": check,
            "column": column,
            "dqu_total_count": total,
            "dqu_failed_count": failed,
            "dqu_passed_count": total - failed,
            "run_timestamp": datetime.now(timezone.utc).isoformat(),
            "run_id": self.run_id,
        }

        if evaluation == "advanced":
            return json.dumps(result_dict, indent=2), failed_df

        return json.dumps(result_dict, indent=2)


