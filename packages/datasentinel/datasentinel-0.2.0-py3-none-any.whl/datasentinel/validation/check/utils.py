import re
from typing import Any

from toolz import first


def get_type(df: Any) -> str:
    return first(re.match(r".*'(.*)'", str(type(df))).groups())


def to_df_if_delta_table(df: Any) -> Any:
    if "delta" in get_type(df):
        return df.toDF()
    return df
