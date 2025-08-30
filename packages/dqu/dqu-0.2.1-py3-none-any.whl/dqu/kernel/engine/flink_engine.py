from typing import List, Dict, Any, Optional, Tuple, Callable, Union
from pyflink.datastream import DataStream
from pyflink.common.typeinfo import Types
from pyflink.datastream.functions import RuntimeContext, ProcessFunction
from pyflink.datastream.state import ValueStateDescriptor
from dqu.kernel.engine.base_engine import BaseEngine
from dqu.utils.time_utils import parse_duration_to_timedelta
import json
from datetime import datetime, timezone, datetime as dt
import re
from collections import Counter

class FlinkEngine(BaseEngine):
    def __init__(self, df, columns=None, run_id=None):
        if columns is None:
            raise ValueError("FlinkEngine requires a non-None 'columns' argument for DataStream input.")
        self.df = df
        self.columns = columns
        self.run_id = run_id

    def _collect(self, columns: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        selected_columns = columns or self.columns
        raw_data = list(self.df.execute_and_collect())

        if not raw_data:
            return []
        # Create an index map from column name to index in full self.columns
        col_index_map = {col: idx for idx, col in enumerate(self.columns)}

        try:
            return [
                {col: row[col_index_map[col]] for col in selected_columns}
                for row in raw_data
            ]
        except Exception as e:
            raise ValueError(f"Error extracting selected columns from row: {e}")


    def _count(self) -> int:
        return len(self._collect())

    def run_dup_check(
        self,
        columns: List[str],
        evaluation: str = "basic"
    ) -> Union[str, Tuple[str, List[Dict[str, Any]]]]:
        for col in columns:
            if col not in self.columns:
                raise KeyError(f"Column '{col}' not found in dataset.")
        all_rows = list(self.df.execute_and_collect())
        # Convert all rows to dicts for selected columns
        all_dicts = [{self.columns[i]: row[i] for i in range(len(self.columns))} for row in all_rows]
        # Only keep selected columns for duplicate key calculation
        key_counts = Counter(tuple(row[col] for col in columns) for row in all_dicts)
        dup_keys = {k for k, v in key_counts.items() if v > 1}
        failed_dicts = [row for row in all_dicts if tuple(row[col] for col in columns) in dup_keys]
        result = {
            "status": "Success" if not failed_dicts else "Failed",
            "dqu_check_type": "duplicate_check",
            "dqu_total_count": len(all_dicts),
            "dqu_failed_count": len(failed_dicts),
            "dqu_passed_count": len(all_dicts) - len(failed_dicts),
            "run_timestamp": datetime.now(timezone.utc).isoformat(),
            "run_id": self.run_id
        }
        if evaluation == "advanced":
            return json.dumps(result, indent=2), failed_dicts
        return json.dumps(result, indent=2)

    def run_empty_check(
        self,
        columns: List[str],
        evaluation: str = "basic"
    ) -> Union[str, Tuple[str, List[Dict[str, Any]]]]:
        for col in columns:
            if col not in self.columns:
                raise KeyError(f"Column '{col}' not found in dataset.")
        all_rows = list(self.df.execute_and_collect())
        all_dicts = [{self.columns[i]: row[i] for i in range(len(self.columns))} for row in all_rows]
        failed_dicts = [
            row for row in all_dicts
            if any(row.get(col) in (None, '') for col in columns)
        ]
        result = {
            "status": "Success" if not failed_dicts else "Failed",
            "dqu_check_type": "empty_check",
            "dqu_total_count": len(all_dicts),
            "dqu_failed_count": len(failed_dicts),
            "dqu_passed_count": len(all_dicts) - len(failed_dicts),
            "run_timestamp": datetime.now(timezone.utc).isoformat(),
            "run_id": self.run_id
        }
        if evaluation == "advanced":
            return json.dumps(result, indent=2), failed_dicts
        return json.dumps(result, indent=2)

    def run_unique_check(
        self,
        columns: List[str],
        evaluation: str = "basic"
    ) -> Union[str, Tuple[str, List[Dict[str, Any]]]]:
        for col in columns:
            if col not in self.columns:
                raise KeyError(f"Column '{col}' not found in dataset.")
        all_rows = list(self.df.execute_and_collect())
        all_dicts = [{self.columns[i]: row[i] for i in range(len(self.columns))} for row in all_rows]
        key_counts = Counter(tuple(row[col] for col in columns) for row in all_dicts)
        dup_keys = {k for k, v in key_counts.items() if v > 1}
        failed_dicts = [row for row in all_dicts if tuple(row[col] for col in columns) in dup_keys]
        result = {
            "status": "Success" if not failed_dicts else "Failed",
            "dqu_check_type": "unique_check",
            "dqu_total_count": len(all_dicts),
            "dqu_failed_count": len(failed_dicts),
            "dqu_passed_count": len(all_dicts) - len(failed_dicts),
            "run_timestamp": datetime.now(timezone.utc).isoformat(),
            "run_id": self.run_id
        }
        if evaluation == "advanced":
            return json.dumps(result, indent=2), failed_dicts
        return json.dumps(result, indent=2)

    def run_dtype_check(self, column_types: Dict[str, str], evaluation: str = "basic") -> Union[str, Tuple[str, List[Dict[str, Any]]]]:
        type_map = {
            'int': int, 'integer': int,
            'float': float, 'double': float,
            'str': str, 'string': str,
            'bool': bool, 'boolean': bool,
        }

        for col, expected in column_types.items():
            if expected.lower() not in type_map:
                raise ValueError(f"Unsupported data type '{expected}' for column '{col}'")

        collected = self._collect()
        failed = []
        for row in collected:
            for col, expected in column_types.items():
                expected_type = type_map[expected.lower()]
                if col in row and row[col] is not None:
                    try:
                        expected_type(row[col])
                    except (ValueError, TypeError):
                        failed.append(row)
                        break
        return self._build_result("dtype_check", collected, failed, evaluation)


    def run_schemavalidation_check(
        self,
        expected_schema: Dict[str, Any]) -> str:
        import json
        from datetime import datetime, timezone

        # Flink DataStream does not have schema info, so infer from first row
        collected = self._collect()
        if not collected:
            actual_schema = {}
        else:
            first_row = collected[0]
            actual_schema = {col: type(val).__name__ for col, val in first_row.items()}

        missing_columns = [col for col in expected_schema if col not in actual_schema]
        mismatched_types = {}

        for col, expected_dtype in expected_schema.items():
            if col in actual_schema:
                if str(expected_dtype).lower() != actual_schema[col].lower():
                    mismatched_types[col] = {
                        "expected": str(expected_dtype),
                        "actual": actual_schema[col]
                    }

        status = "Success" if not missing_columns and not mismatched_types else "Failed"
        result_dict = {
            "status": status,
            "dqu_check_type": "schemavalidation_check",
            "missing_columns": missing_columns,
            "type_mismatches": mismatched_types,
            "dqu_total_count": len(collected),
            "dqu_failed_count": len(missing_columns) + len(mismatched_types),
            "dqu_passed_count": len(expected_schema) - len(missing_columns) - len(mismatched_types),
            "run_timestamp": datetime.now(timezone.utc).isoformat(),
            "run_id": self.run_id,
        }
        return json.dumps(result_dict, indent=2)
    
    def run_stringformat_check(
        self,
        column: str,
        pattern: str,
        evaluation: str = "basic"
    ) -> Union[str, Tuple[str, List[Dict[str, Any]]]]:
        import re
        regex = re.compile(pattern)
        if column not in self.columns:
            raise KeyError(f"Column '{column}' not found in dataset.")
        collected = self._collect([column])
        failed = [row for row in collected if not regex.fullmatch(str(row[column]) or '')]
        result = {
            "status": "Success" if not failed else "Failed",
            "dqu_check_type": "stringformat_check",
            "dqu_total_count": len(collected),
            "dqu_failed_count": len(failed),
            "dqu_passed_count": len(collected) - len(failed),
            "run_timestamp": datetime.now(timezone.utc).isoformat(),
            "run_id": self.run_id
        }
        if evaluation == "advanced":
            return json.dumps(result, indent=2), failed
        return json.dumps(result, indent=2)

    def run_range_check(
        self,
        column: str,
        min_val: float,
        max_val: float,
        evaluation: str = "basic"
    ) -> Union[str, Tuple[str, List[Dict[str, Any]]]]:
        if column not in self.columns:
            raise KeyError(f"Column '{column}' not found in dataset.")

        col_idx = self.columns.index(column)
        all_rows = list(self.df.execute_and_collect())
        total = len(all_rows)
        failed_rows = [row for row in all_rows if row[col_idx] < min_val or row[col_idx] > max_val]
        all_dicts = [{self.columns[i]: row[i] for i in range(len(self.columns))} for row in all_rows]
        failed_dicts = [{self.columns[i]: row[i] for i in range(len(self.columns))} for row in failed_rows]

        result = {
            "status": "Success" if not failed_rows else "Failed",
            "dqu_check_type": "range_check",
             "column": column,
             "range": {
                 "min": min_val,
                 "max": max_val
                 },
            "dqu_total_count": len(all_dicts),
            "dqu_failed_count": len(failed_dicts),
            "dqu_passed_count": len(all_dicts) - len(failed_dicts),
            "run_timestamp": datetime.now(timezone.utc).isoformat(),
            "run_id": self.run_id
        }
        if evaluation == "advanced":
            return json.dumps(result, indent=2), failed_dicts
        return json.dumps(result, indent=2)

    def run_categoricalvalues_check(
        self,
        column: str,
        allowed_values: List[Any],
        evaluation: str = "basic"
    ) -> Union[str, Tuple[str, List[Dict[str, Any]]]]:
        if column not in self.columns:
            raise KeyError(f"Column '{column}' not found in dataset.")
        allowed_set = set(allowed_values)
        collected = self._collect()
        failed = [row for row in collected if row.get(column) not in allowed_set]
        result = {
            "status": "Success" if not failed else "Failed",
            "dqu_check_type": "categoricalvalues_check",
            "allowed_values": allowed_values,
            "dqu_total_count": len(collected),
            "dqu_failed_count": len(failed),
            "dqu_passed_count": len(collected) - len(failed),
            "run_timestamp": datetime.now(timezone.utc).isoformat(),
            "run_id": self.run_id
        }
        if evaluation == "advanced":
            return json.dumps(result, indent=2), failed
        return json.dumps(result, indent=2)

    def run_rowcount_check(self, min_rows: Optional[int] = None, max_rows: Optional[int] = None) -> str:
        total = self._count()
        status = "Success"
        if (min_rows is not None and total < min_rows) or (max_rows is not None and total > max_rows):
            status = "Failed"
        result = {
            "status": status,
            "dqu_check_type": "rowcount_check",
            "dqu_total_count": total,
            "min_required": min_rows,
            "max_allowed": max_rows,
            "run_timestamp": datetime.now(timezone.utc).isoformat(),
            "run_id": self.run_id
        }
        return json.dumps(result, indent=2)

    def run_datafreshness_check(self, column: str, freshness_threshold: str) -> str:
        if column not in self.columns:
            raise KeyError(f"Column '{column}' not found in dataset.")

        collected = self._collect([column])
        timestamps = []
        for row in collected:
            raw_ts = row.get(column)
            if raw_ts is None:
                continue
            if isinstance(raw_ts, str):
                raise TypeError(
                    f"Invalid string timestamp in column '{column}': '{raw_ts}'. Only numeric milliseconds are allowed."
                )
            if not isinstance(raw_ts, (int, float)):
                raise TypeError(
                    f"Invalid timestamp type in column '{column}': {type(raw_ts)}. Expected int/float in epoch milliseconds."
                )
            try:
                parsed = dt.fromtimestamp(raw_ts / 1000, tz=timezone.utc)
                if parsed.year < 2000:
                    raise TypeError(
                        f"Unrealistic timestamp in column '{column}': {raw_ts}"
                    )
                timestamps.append(parsed)
            except (ValueError, OverflowError, OSError) as e:
                raise TypeError(
                    f"Invalid timestamp value in column '{column}': {raw_ts}"
                ) from e
        if not timestamps:
            raise ValueError(f"No valid timestamp values found in column '{column}'.")

        # Validate freshness threshold
        if not isinstance(freshness_threshold, str) or not re.fullmatch(r"^\d+[dhm]$", freshness_threshold):
            raise ValueError(
                f"Invalid freshness threshold '{freshness_threshold}'. Use formats like '2d', '3h', or '60m'."
            )

        latest_ts = max(timestamps)
        cutoff_ts = dt.now(tz=timezone.utc) - parse_duration_to_timedelta(freshness_threshold)
        passed = latest_ts > cutoff_ts

        result = {
            "status": "Success" if passed else "Failed",
            "dqu_check_type": "datafreshness_check",
            "column": column,
            "latest_timestamp": latest_ts.isoformat(),
            "cutoff_timestamp": cutoff_ts.isoformat(),
            "dqu_passed": passed,
            "run_timestamp": datetime.now(timezone.utc).isoformat(),
            "run_id": self.run_id
        }
        return json.dumps(result, indent=2)

    def run_custom_check(
        self,
        column: Optional[str],
        func: Callable[[Any], bool],
        evaluation: str = "basic"
    ) -> Union[str, Tuple[str, List[Dict[str, Any]]]]:
        """
        Flink-compatible custom check function.

        Args:
            column: Column name to apply the function to. If None, applies to each row as a dict.
            func: Callable that returns True if value/row passes, False otherwise.
            evaluation: "basic" or "advanced".

        Returns:
            JSON result string, and optionally the list of failed rows.
        """

        if column and column not in self.columns:
            raise KeyError(f"Column '{column}' not found in dataset.")

        all_rows = list(self.df.execute_and_collect())

        if column:
            col_index = self.columns.index(column)
            failed_rows = [dict(zip(self.columns, row)) for row in all_rows if not func(row[col_index])]
            check = "custom_check_column"
        else:
            failed_rows = [dict(zip(self.columns, row)) for row in all_rows if not func(dict(zip(self.columns, row)))]
            check = "custom_check_row"

        total_count = len(all_rows)
        failed_count = len(failed_rows)
        passed_count = total_count - failed_count

        result = {
            "status": "Success" if failed_count == 0 else "Failed",
            "dqu_check_type": check,
            "column": column,
            "dqu_total_count": total_count,
            "dqu_failed_count": failed_count,
            "dqu_passed_count": passed_count,
            "run_timestamp": datetime.now(timezone.utc).isoformat(),
            "run_id": self.run_id
        }

        if evaluation == "advanced":
            return json.dumps(result, indent=2), failed_rows
        return json.dumps(result, indent=2)



    def run_statisticaldistribution_check(
        self,
        column: str,
        mode: str,
        reference_stats: Optional[Dict[str, float]] = None,
        tolerance: float = 0.05
    ) -> str:
        import numpy as np
        from datetime import datetime, timezone
        import json

        if column not in self.columns:
            raise KeyError(f"Column '{column}' not found in dataset.")

        collected = self._collect([column])
        values = [row[column] for row in collected if row.get(column) is not None]

        if not values:
            raise ValueError(f"No valid values found for column '{column}'.")

        if mode == "feature_drift":
            if reference_stats is None:
                raise ValueError("reference_stats must be provided for feature_drift mode.")

            current_mean = float(np.mean(values))
            current_std = float(np.std(values))

            drift_mean = abs(current_mean - reference_stats.get("mean", 0.0))
            drift_std = abs(current_std - reference_stats.get("std", 0.0))

            passed = (drift_mean <= tolerance) and (drift_std <= tolerance)

            result_dict = {
                "status": "Success" if passed else "Failed",
                "dqu_check_type": "statisticaldistribution_check",
                "mode": "feature_drift",
                "column": column,
                "dqu_drift_mean": drift_mean,
                "dqu_drift_std": drift_std,
                "dqu_passed": bool(passed),
                "run_timestamp": datetime.now(timezone.utc).isoformat(),
                "run_id": self.run_id,
            }
            return json.dumps(result_dict, indent=2)
        else:
            raise ValueError("Only 'feature_drift' mode is supported for FlinkEngine statisticaldistribution_check.")

    def _build_result(self, check_type: str, total_rows: List[Dict[str, Any]], failed_rows: List[Dict[str, Any]], evaluation: str,
                      **extra_fields) -> Union[str, Tuple[str, List[Dict[str, Any]]]]:
        
        result = {
            "status": "Success" if not failed_rows else "Failed",
            "dqu_check_type": check_type,
            "dqu_total_count": len(total_rows),
            "dqu_failed_count": len(failed_rows),
            "dqu_passed_count": len(total_rows) - len(failed_rows),
            "run_timestamp": datetime.now(timezone.utc).isoformat(),
            "run_id": self.run_id
        }
        result.update(extra_fields)
        if evaluation == "advanced":
            return json.dumps(result, indent=2), failed_rows
        return json.dumps(result, indent=2)

    def run_referential_integrity_check(
        self,
        column: str,
        reference_df,
        reference_column: str,
        evaluation: str = "basic",
        reference_columns: Optional[List[str]] = None
    ) -> Union[str, Tuple[str, List[Dict[str, Any]]]]:
        """
        Flink-based referential integrity check between a column in the main dataset and reference dataset.

        Args:
            column: Column in the main dataset to validate.
            reference_df: Reference Flink DataStream.
            reference_column: Column in the reference dataset.
            evaluation: "basic" for JSON only, "advanced" for JSON + failed rows.
            reference_columns: List of column names in the reference_df (must include reference_column).

        Returns:
            JSON string (and failed rows list if advanced).
        """
        if column not in self.columns:
            raise KeyError(f"Column '{column}' not found in dataset.")

        if reference_columns:
            if reference_column not in reference_columns:
                raise KeyError(f"Reference column '{reference_column}' not found in reference dataset.")
            ref_idx = reference_columns.index(reference_column)
        else:
            ref_idx = 0  # Default to first column if no schema provided

        reference_data = list(reference_df.execute_and_collect())
        reference_values = {row[ref_idx] for row in reference_data if row is not None}
        main_data_full = self._collect(self.columns)
        failed_rows = [
            row for row in main_data_full if row[column] not in reference_values
        ]

        total = len(main_data_full)
        failed_count = len(failed_rows)
        passed_count = total - failed_count

        result = {
            "status": "Success" if failed_count == 0 else "Failed",
            "dqu_check_type": "referentialintegrity_check",
            "dqu_total_count": total,
            "dqu_failed_count": failed_count,
            "dqu_passed_count": passed_count,
            "run_timestamp": datetime.now(timezone.utc).isoformat(),
            "run_id": self.run_id
        }

        if evaluation == "advanced":
            return json.dumps(result, indent=2), failed_rows
        return json.dumps(result, indent=2)



    def run_schemavalidation_check(
        self,
        expected_schema: Dict[str, Any]
    ) -> str:
        import json
        from datetime import datetime, timezone
        collected = self._collect()
        if not collected:
            actual_schema = {}
        else:
            first_row = collected[0]
            actual_schema = {col: type(val).__name__ for col, val in first_row.items()}

        missing_columns = [col for col in expected_schema if col not in actual_schema]
        mismatched_types = {}

        for col, expected_dtype in expected_schema.items():
            if col in actual_schema:
                if str(expected_dtype).lower() != actual_schema[col].lower():
                    mismatched_types[col] = {
                        "expected": str(expected_dtype),
                        "actual": actual_schema[col]
                    }

        status = "Success" if not missing_columns and not mismatched_types else "Failed"

        result_dict = {
            "status": status,
            "dqu_check_type": "schemavalidation_check",
            "missing_columns": missing_columns,
            "type_mismatches": mismatched_types,
            "dqu_total_count": len(collected),
            "dqu_failed_count": len(missing_columns) + len(mismatched_types),
            "dqu_passed_count": len(expected_schema) - len(missing_columns) - len(mismatched_types),
            "run_timestamp": datetime.now(timezone.utc).isoformat(),
            "run_id": self.run_id,
        }

        return json.dumps(result_dict, indent=2)

