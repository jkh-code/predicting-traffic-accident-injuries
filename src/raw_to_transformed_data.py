import pandas as pd

import psycopg2 as pg2
from os import environ

from typing import Union

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


if __name__ == '__main__':
    pass