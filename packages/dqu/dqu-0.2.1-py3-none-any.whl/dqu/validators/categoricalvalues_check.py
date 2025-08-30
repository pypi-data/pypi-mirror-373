from dqu.base import BaseDQCheck
from dqu.kernel.engine_runner import EngineRunner
from dqu.utils.exceptions import ColumnNotFoundException
from dqu.utils.config_validator import ConfigValidator

class DquCategoricalValuesCheck(BaseDQCheck):
    """
    Categorical Values Check Rule:
    Validates that all values in a column are within an allowed set.
    """

    def run(self, evaluation="basic"):
        ConfigValidator.validate(self.config, self.expected_config())
        column = self.config.get("column")
        allowed_values = self.config.get("allowed_values")

        if not column or not allowed_values:
            raise ValueError("'column' and 'allowed_values' must be specified in config.")

        df = self.qdf.get_df()
        engine = self.qdf.get_engine()
        if engine not in {"ray", "flink"}:
            if column not in df.columns:
                raise ColumnNotFoundException(column)
        
        # Pass columns for flink, else None
        columns_arg = self.qdf.columns if engine in {"flink"} else None
        runner = EngineRunner(df, engine, run_id=self.run_id, columns=columns_arg)
        return runner.run_categoricalvalues_check(column, allowed_values, evaluation=evaluation)
    
    @classmethod
    def expected_config(cls):
        return {
            "column": (str, True),
            "allowed_values": (list, True)
        }
