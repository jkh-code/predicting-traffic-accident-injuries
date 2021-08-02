import pandas as pd
import numpy as np

import psycopg2 as pg2
from os import environ
from sqlalchemy import create_engine
from sqlalchemy.engine.base import Engine

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

def make_alchemy_engine(
        dbname: str='postgres', port: int=5432) -> Engine:
    """Make SQL Alchemy engine to connect to PostgreSQL database."""
    username = environ['PG_USER']
    password = environ['PG_PASSWORD']
    host = environ['PG_HOST']
    string = f'postgresql://{username}:{password}@{host}:{port}/{dbname}'
    return create_engine(string)

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
    print("Starting program...")

    crashes_raw_query = """
        SELECT *
        FROM crashes_raw;
        """
    print("Retrieving crashes data from database...")
    df_crashes = get_sql_data(
        db_name="chi-traffic-accidents", query=crashes_raw_query)
    
    # Defining crashes columns to transform datatype
    cols_datetime = ["crash_date", "date_police_notified"]
    cols_int = ["posted_speed_limit", "lane_cnt", "street_no", 
        "beat_of_occurrence", "num_units", "injuries_total", "injuries_fatal", 
        "injuries_incapacitating", "injuries_non_incapacitating", 
        "injuries_reported_not_evident", "injuries_no_indication", 
        "injuries_unknown", "crash_hour", "crash_day_of_week", "crash_month"]
    cols_float = ["latitude", "longitude"]
    cols_str = ["crash_record_id", "rd_no", "crash_date_est_i", 
        "traffic_control_device", "device_condition", "weather_condition", 
        "lighting_condition", "first_crash_type", "trafficway_type", 
        "alignment", "roadway_surface_cond", "road_defect", "report_type", 
        "crash_type", "intersection_related_i", "hit_and_run_i", "damage", 
        "prim_contributory_cause", "sec_contributory_cause", 
        "street_direction", "street_name", "photos_taken_i", 
        "statements_taken_i", "dooring_i", "work_zone_i", "work_zone_type", 
        "workers_present_i", "most_severe_injury"]

    cols_all = [cols_datetime, cols_int, cols_float, cols_str]
    cols_conversions = ["datetime", "float", "integer", "string"]

    print("Transforming crashes dataframe...")
    for conv, cols in zip(cols_conversions, cols_all):
        convert_df_columns(conv, df_crashes, cols)
    
    # Writing transformed crashes data to database
    alchemy_engine = make_alchemy_engine(dbname="chi-traffic-accidents")
    print("Writing crashes table to database...")
    df_crashes.to_sql(
        name="crashes", con=alchemy_engine, if_exists="replace", index=False)



    print("Program complete.")