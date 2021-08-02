import pandas as pd
import numpy as np

import psycopg2 as pg2
from os import environ

from typing import Union, Literal, List

pd.set_option("display.max_columns", None)


def make_postgres_conn(
        dbname: str='postgres', port: int=5432) -> pg2.extensions.connection:
    """Create connection to a PostgreSQL database using credentials saved
    as environment variables."""
    conn = pg2.connect(
        dbname=dbname,
        port=port,
        host=environ['PG_HOST'],
        user=environ['PG_USER'],
        password=environ['PG_PASSWORD'])
    return conn

def get_sql_data(
        db_name: str, query: str, 
        num_rows: Union[int, None]=None) -> pd.DataFrame:
    """Retrieve data from a PostgreSQL database."""
    conn = make_postgres_conn(db_name)
    
    if not num_rows:
        df = pd.read_sql(query, conn)
    else:
        df = pd.read_sql(query, conn, params=[num_rows])
        
    conn.close()
    return df

def convert_df_columns(
        conversion_type: Literal["datetime", "float", "integer", "string"], 
        df: pd.DataFrame, columns: List[str])-> None:
    if conversion_type not in ("datetime", "float", "integer", "string"):
        raise ValueError(
            "'converstion_type' must be a value of 'datetime', "
            + "'float', 'integer', or 'string'.")
    
    for col in columns:
        if conversion_type == "datetime":
            df[col] = pd.to_datetime(df[col], format="%Y-%m-%dT%H:%M:%S.%f")
        elif conversion_type == "float":
            df[col] = pd.to_numeric(df[col], downcast="float")
        elif conversion_type == "integer":
            df[col] = pd.to_numeric(df[col], downcast="integer")
        elif conversion_type == "string":
            df[col] = df_crashes[col].astype("string")


if __name__ == '__main__':
    pass