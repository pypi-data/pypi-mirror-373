from dqu.base import BaseDQCheck
from dqu.kernel.engine_runner import EngineRunner
from dqu.utils.exceptions import ColumnNotFoundException
from dqu.utils.config_validator import ConfigValidator

class DquDataFreshnessCheck(BaseDQCheck):
    """
    Data Freshness Check:
    Ensures that the latest value in a datetime column is recent (within threshold).
    Question asked : "Is the most recent timestamp in the data newer than 7 days (freshness_threshold) ago?"
    """

    def run(self, evaluation="basic"):
        ConfigValidator.validate(self.config, self.expected_config())
        column = self.config.get("column")
        freshness_threshold = self.config.get("freshness_threshold", "1d")

        if not column:
            raise ValueError("'column' is required in the config.")

        df = self.qdf.get_df()
        engine = self.qdf.get_engine()
        
        if engine not in {"ray", "flink"}:
            if column not in df.columns:
                raise ColumnNotFoundException(column)

        # Pass columns for flink, else None
        columns_arg = self.qdf.columns if engine in {"flink"} else None
        runner = EngineRunner(df, engine, run_id=self.run_id, columns=columns_arg)
        return runner.run_datafreshness_check(column, freshness_threshold)
    
    @classmethod
    def expected_config(cls):
        return {
            "column": (str, True),
            "freshness_threshold": (str, False),  # Accepts formats like '1d', '2h', '30m'
        }
