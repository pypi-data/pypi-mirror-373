from pyspark.sql import Row
import unittest
import pyyql.yaml_engine as engine
from samplesparksession import SampleSparkSession
import os
import sys

os.environ['PYSPARK_PYTHON'] = sys.executable
os.environ['PYSPARK_DRIVER_PYTHON'] = sys.executable

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
spark = SampleSparkSession().new_spark_session()


class Test_yaml_engine(unittest.TestCase):
    test_yaml = ROOT_DIR + "/resources/sample_yaml.yaml"

    def test_parse_tuple(self):
        parsed_tuple = engine.parse_tuple(string='("df1", "df2", "df1.A1", "df2.B1")')
        assert parsed_tuple == ("df1", "df2", "df1.A1", "df2.B1")

    def test_get_alias_tables(self):
        dependencies_source = engine.get_alias_tables(yaml_path=self.test_yaml)
        assert dependencies_source == {
            "df1": "df1",
            "df2": "df2",
            "df3": "df3",
            "df4": "df4",
        }

    def test_join_conditions(self):
        join_conditions = engine.get_join_conditions(yaml_path=self.test_yaml)
        assert join_conditions == [
            ("df1", "df2", "df1.A1", "df2.B1"),
            ("df2", "df3", "df2.B1", "df3.C1"),
            ("df1", "df4", "df1.A1", "df4.D1"),
        ]

    def test_get_columns_with_alias(self):
        string_type_column = "[Column<'df1.A1 AS df1_A1'>, Column<'df1.B1 AS df1_B1'>, Column<'df1.C1 AS df1_C1'>, Column<'df2.B1 AS df2_B1'>, Column<'df2.B2 AS df2_B2'>, Column<'df3.B3 AS df2_B3'>, Column<'df4.D1 AS df4_D1'>, Column<'df4.D2 AS df4_D2'>, Column<'df4.D3 AS df4_D3'>]"
        column_alias = engine.get_columns_with_alias(yaml_path=self.test_yaml)
        assert str(column_alias) == string_type_column

    def test_join_multiple_dfs(self):
        lst1 = [[1, 2, 3], ["A", "B", "C"], ["aa", "bb", "cc"]]
        lst2 = [[2, 3, 4], ["A", "B", "C"], ["aa", "bb", "cc"]]
        lst3 = [[1, 2, 4], ["A", "B", "C"], ["aa", "bb", "cc"]]
        lst4 = [[1, 2, 4], ["A", "B", "C"], ["aa", "bb", "cc"]]

        R1 = Row("A1", "A2", "A3")
        R2 = Row("B1", "B2", "B3")
        R3 = Row("C1", "C2", "C3")
        R4 = Row("D1", "D2", "D3")

        df1 = (
            spark.sparkContext.parallelize([R1(*r) for r in zip(*lst1)])
            .toDF()
            .alias("df1")
        )
        df2 = (
            spark.sparkContext.parallelize([R2(*r) for r in zip(*lst2)])
            .toDF()
            .alias("df2")
        )
        df3 = (
            spark.sparkContext.parallelize([R3(*r) for r in zip(*lst3)])
            .toDF()
            .alias("df3")
        )
        df4 = (
            spark.sparkContext.parallelize([R4(*r) for r in zip(*lst4)])
            .toDF()
            .alias("df4")
        )

        joined_df = [
            Row(
                A1=1,
                A2="A",
                A3="aa",
                B1=None,
                B2=None,
                B3=None,
                C1=None,
                C2=None,
                C3=None,
                D1=1,
                D2="A",
                D3="aa",
            ),
            Row(
                A1=2,
                A2="B",
                A3="bb",
                B1=2,
                B2="A",
                B3="aa",
                C1=2,
                C2="B",
                C3="bb",
                D1=2,
                D2="B",
                D3="bb",
            ),
            Row(
                A1=3,
                A2="C",
                A3="cc",
                B1=3,
                B2="B",
                B3="bb",
                C1=None,
                C2=None,
                C3=None,
                D1=None,
                D2=None,
                D3=None,
            ),
        ]

        df_dict_with_alias = {"df1": df1, "df2": df2, "df3": df3, "df4": df4}
        conditions_join_list = engine.get_join_conditions(yaml_path=self.test_yaml)

        engine.join_multiple_dfs(
            df_named_dict=df_dict_with_alias, 
            join_condition_list=conditions_join_list,
             join_type="left"
        ).show()
        assert (
            engine.join_multiple_dfs(
                df_named_dict=df_dict_with_alias,
                join_condition_list=conditions_join_list,
                join_type="left"
            ).collect()
            == joined_df
        )


if __name__ == "__main__":
    unittest.main()
