from pyspark.sql import SparkSession, DataFrame

class CSVReader():
    def __init__(self, input_path: str, ss: SparkSession):
        self.input_path = input_path
        self.ss = ss
        
    def read(self) -> DataFrame:
        return self.ss.read.option('header', True).csv(self.input_path,inferSchema=True)
        