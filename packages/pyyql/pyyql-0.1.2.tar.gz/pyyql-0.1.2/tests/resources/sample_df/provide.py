from pyspark.sql import Row
from tests.samplesparksession import SampleSparkSession    

spark = SampleSparkSession().new_spark_session()

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

print(df_dict_with_alias)