from dqu.base import BaseDQCheck
from dqu.kernel.engine_runner import EngineRunner
from dqu.utils.config_validator import ConfigValidator
from dqu.utils.exceptions import ColumnNotFoundException
from collections.abc import Callable

class DquCustomCheck(BaseDQCheck):
    """
    Custom Check Rule:
    Apply an arbitrary Python callable (for Pandas) or UDF (for Spark)
    against a single column. Emits summary and, optionally, the failing rows.
    """

    def run(self, evaluation="basic"):
        # 1) Validate config
        cfg = ConfigValidator.validate(self.config, self.expected_config())
        column = self.config.get("column")
        func = self.config.get("func")

        df     = self.qdf.get_df()
        engine = self.qdf.get_engine()
        if engine not in {"ray", "flink"}:
            if column is not None and column not in df.columns:
                raise ColumnNotFoundException(column)

        # Pass columns for flink, else None
        columns_arg = self.qdf.columns if engine in {"flink"} else None
        runner = EngineRunner(df, engine, run_id=self.run_id, columns=columns_arg)
        return runner.run_custom_check(column, func, evaluation=evaluation)

    @classmethod
    def expected_config(cls):
        return {
            "column": (str,      False),   # e.g. "age" or "name" # optional; if missing or None → row-level
            "func"  : (Callable, True)    # Python callable (Pandas) or UDF (Spark)
        }
