from pyspark.sql import SparkSession


class SampleSparkSession:
    def __init__(
        self, app_name="YQL - Local Spark Job Testing", master="local[*]"
    ) -> None:
        self.app_name = app_name
        self.master = master

    def new_spark_session(self) -> SparkSession:
        return (
            SparkSession.builder.appName(self.app_name)
            .master(self.master)
            .getOrCreate()
        )