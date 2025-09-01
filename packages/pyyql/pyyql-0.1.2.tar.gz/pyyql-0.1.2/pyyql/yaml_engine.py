import yaml
import ast
import pyspark.sql.functions as F
from pyspark.sql import DataFrame
from typing import Dict
import pandas as pd


def parse_tuple(string):
    try:
        s = ast.literal_eval(str(string))
        if type(s) == tuple:
            return s
        return
    except:
        return


def get_alias_tables(yaml_path: str) -> Dict:
    with open(yaml_path) as f:
        my_dict = yaml.safe_load(f)
        dependencies = my_dict.get("dependencies")
        return {
            k: v.get("table_name")
            for k, v in dependencies.items()
            if v.get("type") == "source"
        }


def get_join_conditions(yaml_path: str):
    list_conditions = []
    with open(yaml_path) as f:
        my_dict = yaml.safe_load(f)
        join_conditions = my_dict.get("join_conditions")
    for elem in join_conditions:
        list_conditions.append(parse_tuple(elem))
    return list_conditions


def get_columns_with_alias(yaml_path: str):
    with open(yaml_path) as f:
        my_dict = yaml.safe_load(f)
        cols_dict = my_dict.get("select")
    return [F.col(c).alias(cols_dict.get(c)) for c in cols_dict.keys()]


def drop_duplicated_cols_after_join(df:DataFrame):
    newcols = []
    dupcols = []

    for i in range(len(df.columns)):
        if df.columns[i] not in newcols:
            newcols.append(df.columns[i])
        else:
            dupcols.append(i)

    df = df.toDF(*[str(i) for i in range(len(df.columns))])
    for dupcol in dupcols:
        df = df.drop(str(dupcol))

    return df.toDF(*newcols)


def join_multiple_dfs(df_named_dict, join_condition_list, join_type) -> DataFrame:
    updated_df_list = []
    for item in join_condition_list:
        updated_df_list.append(
            # (df_name_1,df_name_2, Dataframe 1,     Dataframe 2, condition 1 , condition 2)
            (
                item[0],
                item[1],
                df_named_dict.get(item[0]),
                df_named_dict.get(item[1]),
                item[2],
                item[3],
            )
        )
    df_1 = updated_df_list[0][2]
    for x in updated_df_list:
        df_1 = (
            df_1.alias(x[0])
            .join(x[3].alias(x[1]), on=F.col(x[4]) == F.col(x[5]), how=join_type)
            
        )
        df_1 = drop_duplicated_cols_after_join(df_1)

    return df_1
