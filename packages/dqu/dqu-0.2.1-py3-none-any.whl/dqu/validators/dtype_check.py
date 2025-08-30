from dqu.base import BaseDQCheck
from dqu.kernel.engine_runner import EngineRunner
from dqu.utils.exceptions import ColumnNotFoundException
from dqu.utils.config_validator import ConfigValidator

class DquDtypeCheck(BaseDQCheck):
    """
    Data Type Match Check Rule:
    Ensures that the specified column(s) match the expected data types.
    Supports both Pandas and Spark DataFrames.
    
    Configuration example:
    {
        "columns": {
            "age": "int",
            "name": "string"
        }
    }
    """

    def run(self, evaluation="basic"):
        ConfigValidator.validate(self.config, self.expected_config())
        column_types = self.config.get("columns")
        if not column_types or not isinstance(column_types, dict):
            raise ValueError("'columns' must be a dictionary of column: expected_dtype pairs.")

        df = self.qdf.get_df()
        engine = self.qdf.get_engine()
        if engine not in {"ray", "flink"}:
            for column in column_types.keys():
                if column not in df.columns:
                    raise ColumnNotFoundException(column)

        # Pass columns for flink, else None
        columns_arg = self.qdf.columns if engine in {"flink"} else None
        runner = EngineRunner(df, engine, run_id=self.run_id, columns=columns_arg)
        return runner.run_dtype_check(column_types, evaluation=evaluation)
    
    @classmethod
    def expected_config(cls):
        return {
            "columns": (dict, True)  # Required: {"column_name": "expected_dtype"}
        }