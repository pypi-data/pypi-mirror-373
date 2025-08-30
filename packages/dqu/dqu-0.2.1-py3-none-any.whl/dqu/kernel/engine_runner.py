from dqu.utils.exceptions import UnsupportedEngineException

class EngineRunner:
    """
    Runs data quality checks using the specified engine (Pandas, Spark, Flink, or Ray).
    """
    def __init__(self, df, engine, run_id=None, columns=None):
        """
        Initialize the EngineRunner.

        Args:
            df: The dataframe to check.
            engine (str): 'pandas', 'spark', 'flink', or 'ray'.
            run_id (str, optional): Optional run identifier.
        Raises:
            UnsupportedEngineException: If engine is not supported.
        """
        self.run_id = run_id
        if engine == "pandas":
            from dqu.kernel.engine.pandas_engine import PandasEngine
            self.engine = PandasEngine(df, self.run_id)
        elif engine == "spark":
            from dqu.kernel.engine.spark_engine import SparkEngine
            self.engine = SparkEngine(df, self.run_id)
        elif engine == "flink":
            from dqu.kernel.engine.flink_engine import FlinkEngine
            if columns is None:
                raise ValueError("FlinkEngine requires 'columns' argument for DataStream input.")
            self.engine = FlinkEngine(df, columns=columns, run_id=self.run_id)
        elif engine == "ray":
            from dqu.kernel.engine.ray_engine import RayEngine
            self.engine = RayEngine(df, self.run_id)
        else:
            raise UnsupportedEngineException(engine)

    def run_dup_check(self, columns, evaluation="basic"):
        return self.engine.run_dup_check(columns, evaluation=evaluation)

    def run_empty_check(self, columns, evaluation="basic"):
        return self.engine.run_empty_check(columns, evaluation=evaluation)
    
    def run_unique_check(self, column, evaluation="basic"):
        return self.engine.run_unique_check(column, evaluation=evaluation)
    
    def run_dtype_check(self, column, evaluation="basic"):
        return self.engine.run_dtype_check(column, evaluation=evaluation)
    
    def run_stringformat_check(self, column, pattern, evaluation="basic"):
        return self.engine.run_stringformat_check(column, pattern=pattern, evaluation=evaluation)
    
    def run_schemavalidation_check(self, expected_schema):
        return self.engine.run_schemavalidation_check(expected_schema)
    
    def run_range_check(self, column, min_val, max_val, evaluation="basic"):
        return self.engine.run_range_check(column, min_val, max_val, evaluation=evaluation)
    
    def run_categoricalvalues_check(self, column, allowed_values, evaluation="basic"):
        return self.engine.run_categoricalvalues_check(column, allowed_values, evaluation=evaluation)
    
    def run_statisticaldistribution_check(self, column, mode, reference_stats=None, tolerance=0.05):
        return self.engine.run_statisticaldistribution_check(column, mode, reference_stats, tolerance)
    
    def run_datafreshness_check(self, column, freshness_threshold):
        return self.engine.run_datafreshness_check(column, freshness_threshold)
    
    def run_referential_integrity_check(self, column, reference_df, reference_column, evaluation="basic"):
        return self.engine.run_referential_integrity_check(column, reference_df, reference_column, evaluation=evaluation)
    
    def run_rowcount_check(self, min_rows=None, max_rows=None):
        return self.engine.run_rowcount_check(min_rows, max_rows)
    
    def run_custom_check(self, column, func, evaluation="basic"):
        return self.engine.run_custom_check(column, func, evaluation=evaluation)
