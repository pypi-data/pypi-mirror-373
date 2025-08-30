import numpy as np
import pandas
import pandas as pd
import re
import json
from typing import List, Dict, Any, Optional, Tuple, Callable, Union
from dqu.kernel.engine.base_engine import BaseEngine
from dqu.utils.time_utils import parse_duration_to_timedelta
from datetime import datetime, timezone
from pandas.api.types import (
    is_integer, is_float, is_string_dtype,
    is_bool, is_datetime64_any_dtype,
    is_timedelta64_dtype, is_categorical_dtype
)


class PandasEngine(BaseEngine):

    def run_dup_check(
        self, 
        columns: List[str], 
        evaluation: str = "basic"
    ) -> Union[str, Tuple[str, pd.DataFrame]]:
        """
        Check for duplicate rows based on specified columns.

        Args:
            columns: List of column names to check for duplicates.
            evaluation: "basic" returns JSON, "advanced" returns (JSON, DataFrame).

        Returns:
            JSON string (and DataFrame if advanced).
        """

        duplicates = self.df[self.df.duplicated(subset=columns, keep=False)]
        total = self.df.shape[0]
        failed = duplicates.shape[0]
        result_dict = {
            "status": "Success" if failed == 0 else "Failed",
            "dqu_check_type": "duplicate_check",
            "dqu_total_count": total,
            "dqu_failed_count": failed,
            "dqu_passed_count": total - failed,
            "run_timestamp": datetime.now(timezone.utc).isoformat(),
            "run_id": self.run_id
        }
        if evaluation == "advanced":
            return json.dumps(result_dict, indent=2), duplicates
        return json.dumps(result_dict, indent=2)

    def run_empty_check(
        self, 
        columns: List[str], 
        evaluation: str = "basic"
    ) -> Union[str, Tuple[str, pd.DataFrame]]:
        """
        Check for empty (null or blank) values in specified columns.

        Args:
            columns: List of column names to check for empties.
            evaluation: "basic" returns JSON, "advanced" returns (JSON, DataFrame).

        Returns:
            JSON string (and DataFrame if advanced).
        """
        empty_rows = self.df[self.df[columns].isnull().any(axis=1) | (self.df[columns] == '').any(axis=1)]
        total = self.df.shape[0]
        failed = empty_rows.shape[0]
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

    def run_unique_check(
        self,
        columns: List[str],
        evaluation: str = "basic"
    ) -> Union[str, Tuple[str, pd.DataFrame]]:
        """
        Check for uniqueness in specified columns.

        Args:
            columns: List of column names to check for uniqueness.
            evaluation: "basic" returns JSON, "advanced" returns (JSON, DataFrame).

        Returns:
            JSON string (and DataFrame if advanced).
        """
        duplicates = self.df[self.df.duplicated(subset=columns, keep=False)]
        total = self.df.shape[0]
        failed = duplicates.shape[0]
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
            return json.dumps(result_dict, indent=2), duplicates
        return json.dumps(result_dict, indent=2)
    
    def run_dtype_check(
        self, 
        column_types: Dict[str, str], 
        evaluation: str = "basic"
    ) -> Union[str, Tuple[str, pd.DataFrame]]:
        """
        Check if columns match expected data types.

        Args:
            column_types: Dict mapping column names to expected dtypes.
            evaluation: "basic" returns JSON, "advanced" returns (JSON, DataFrame).

        Returns:
            JSON string (and DataFrame if advanced).
        """
        import numpy as np
        import pandas as pd
        from datetime import datetime, timezone
        import json

        failed_mask = pd.Series([False] * len(self.df), index=self.df.index)
        for col, expected_dtype in column_types.items():
            try:
                # This will raise if dtype is invalid
                np.dtype(expected_dtype)
            except Exception:
                raise ValueError(f"Invalid dtype: {expected_dtype}")
            try:
                if "int" in expected_dtype or "float" in expected_dtype:
                    converted = pd.to_numeric(self.df[col], errors="coerce")
                    fail_col = converted.isna() & ~self.df[col].isna()
                elif "datetime" in expected_dtype:
                    converted = pd.to_datetime(self.df[col], errors="coerce")
                    fail_col = converted.isna() & ~self.df[col].isna()
                elif expected_dtype in ("bool", "boolean"):
                    fail_col = ~self.df[col].isin([True, False, np.nan])
                elif expected_dtype in ("str", "string", "object"):
                    fail_col = ~self.df[col].map(lambda x: isinstance(x, str) or pd.isna(x))
                else:
                    converted = self.df[col].astype(expected_dtype, errors="ignore")
                    fail_col = converted.apply(lambda x: not isinstance(x, type(converted.iloc[0])) and not pd.isna(x))
            except Exception:
                fail_col = pd.Series([True] * len(self.df), index=self.df.index)
            failed_mask |= fail_col

        failed_df = self.df[failed_mask]
        total = len(self.df)
        failed = len(failed_df)

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
    ) -> Union[str, Tuple[str, pd.DataFrame]]:
        """
        Check if string values in a column match a regex pattern.

        Args:
            column: Column name to check.
            pattern: Regex pattern to match.
            evaluation: "basic" returns JSON, "advanced" returns (JSON, DataFrame).

        Returns:
            JSON string (and DataFrame if advanced).
        """
        mask = ~self.df[column].astype(str).str.match(pattern)
        failed_rows = self.df[mask]
        total = self.df.shape[0]
        failed = failed_rows.shape[0]
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
            return json.dumps(result_dict, indent=2), failed_rows
        return json.dumps(result_dict, indent=2)
    
    def run_schemavalidation_check(
        self, 
        expected_schema: Dict[str, Any]
    ) -> str:
        """
        Validate DataFrame schema against expected schema.

        Args:
            expected_schema: Dict mapping column names to expected dtypes.

        Returns:
            JSON string with schema validation results.
        """
        df = self.df
        missing_columns = [col for col in expected_schema if col not in df.columns]
        mismatched_types = {}

        for col, expected_dtype in expected_schema.items():
            if col not in df.columns:
                continue
            actual_dtype = df[col].dtype

            # Normalize types to string
            if isinstance(expected_dtype, type):
                expected_dtype = np.dtype(expected_dtype)
            else:
                expected_dtype = np.dtype(expected_dtype)

            if actual_dtype != expected_dtype:
                mismatched_types[col] = {
                    "expected": str(expected_dtype),
                    "actual": str(actual_dtype)
                }

        status = "Success" if not missing_columns and not mismatched_types else "Failed"

        result_dict = {
            "status": status,
            "dqu_check_type": "schemavalidation_check",
            "missing_columns": missing_columns,
            "type_mismatches": mismatched_types,
            "dqu_total_count": df.shape[0],
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
    ) -> Union[str, Tuple[str, pd.DataFrame]]:
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

        # Identify rows outside range
        mask = ~df[column].between(min_val, max_val)
        failed_count = mask.sum()
        total_count = len(df)
        passed_count = total_count - failed_count

        result_dict = {
            "status": "Success" if failed_count == 0 else "Failed",
            "dqu_check_type": "range_check",
            "column": column,
            "range": {"min": min_val, "max": max_val},
            "dqu_total_count": total_count,
            "dqu_failed_count": int(failed_count),
            "dqu_passed_count": int(passed_count),
            "run_timestamp": datetime.now(timezone.utc).isoformat(),
            "run_id": self.run_id
        }
        if evaluation == "advanced":
            return json.dumps(result_dict, indent=2), df[mask]
        return json.dumps(result_dict, indent=2)
    
    def run_categoricalvalues_check(
        self, 
        column: str, 
        allowed_values: List[Any], 
        evaluation: str = "basic"
    ) -> Union[str, Tuple[str, pd.DataFrame]]:
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

        mask = ~df[column].isin(allowed_values)
        failed_count = mask.sum()
        total_count = len(df)
        passed_count = total_count - failed_count

        result_dict = {
            "status": "Success" if failed_count == 0 else "Failed",
            "dqu_check_type": "categoricalvalues_check",
            "column": column,
            "allowed_values": allowed_values,
            "dqu_total_count": total_count,
            "dqu_failed_count": int(failed_count),
            "dqu_passed_count": int(passed_count),
            "run_timestamp": datetime.now(timezone.utc).isoformat(),
            "run_id": self.run_id
        }
        if evaluation == "advanced":
            return json.dumps(result_dict, indent=2), df[mask]
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
        import numpy as np
        df = self.df

        if column not in df.columns:
            raise ValueError(f"Column '{column}' not found.")

        if mode == "feature_drift":
            current_mean = df[column].mean()
            current_std = df[column].std()

            drift_mean = abs(current_mean - reference_stats["mean"])
            drift_std = abs(current_std - reference_stats["std"])

            passed = drift_mean <= tolerance and drift_std <= tolerance

            result_dict = {
                "status": "Success" if bool(passed) else "Failed",
                "dqu_check_type": "statisticaldistribution_check",
                "mode": "feature_drift",
                "column": column,
                "dqu_drift_mean": float(drift_mean),
                "dqu_drift_std": float(drift_std),
                "dqu_passed": bool(passed),
                "run_timestamp": datetime.now(timezone.utc).isoformat(),
                "run_id": self.run_id
            }
            return json.dumps(result_dict, indent=2)

        elif mode == "label_balance":
            counts = df[column].value_counts(normalize=True).to_dict()
            max_class_ratio = max(counts.values())
            imbalance_threshold = 0.9  # configurable if needed
            passed = max_class_ratio <= imbalance_threshold

            result_dict = {
                "status": "Success" if bool(passed) else "Failed",
                "dqu_check_type": "statisticaldistribution_check",
                "mode": "label_balance",
                "column": column,
                "dqu_distribution": counts,
                "dqu_passed": bool(passed),
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
            column: Column name to check (must be datetime type).
            freshness_threshold: Freshness threshold as a duration string (e.g., '1d', '12h', '15m').

        Returns:
            JSON string with freshness check results.
        """
        import pandas as pd
        df = self.df

        if column not in df.columns:
            raise ValueError(f"Column '{column}' not found.")

        if not pd.api.types.is_datetime64_any_dtype(df[column]):
            raise TypeError(f"Column '{column}' must be of datetime type.")

        latest_timestamp = df[column].max()
        freshness_cutoff = pd.Timestamp.now() - parse_duration_to_timedelta(freshness_threshold)
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
        reference_df: pd.DataFrame, 
        reference_column: str, 
        evaluation: str = "basic"
    ) -> Union[str, Tuple[str, pd.DataFrame]]:
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
        invalid_rows = self.df[~self.df[column].isin(reference_df[reference_column])]
        total = self.df.shape[0]
        failed = invalid_rows.shape[0]
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
        total = self.df.shape[0]

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
        expression: Callable[[Any], bool], 
        evaluation: str = "basic"
    ) -> Union[str, Tuple[str, pd.DataFrame]]:
        """
        Run a custom check using a user-provided function.

        Args:
            column: Column name to apply the function to. If None, applies to each row as a dict.
            expression: Callable that returns True if value/row passes, False otherwise.
            evaluation: "basic" returns JSON, "advanced" returns (JSON, DataFrame).

        Returns:
            JSON string (and DataFrame if advanced).
        """
        total = self.df.shape[0]

        if callable(expression):
            func = expression
        else:
            raise ValueError("`expression` must be a callable or a string representing a lambda.")
        
        if column:
            mask = ~self.df[column].apply(func)
            check = "custom_check_column"
        else:
            mask = ~self.df.apply(lambda row: func(row.to_dict()), axis=1)
            check = "custom_check_row"

        failed_df = self.df[mask]
        failed_count = failed_df.shape[0]

        result_dict = {
            "status": "Success" if failed_count == 0 else "Failed",
            "dqu_check_type": check,
            "column": column,
            "dqu_total_count": total,
            "dqu_failed_count": failed_count,
            "dqu_passed_count": total - failed_count,
            "run_timestamp": datetime.now(timezone.utc).isoformat(),
            "run_id": self.run_id
        }

        if evaluation == "advanced":
            return json.dumps(result_dict, indent=2), failed_df
        return json.dumps(result_dict, indent=2)

