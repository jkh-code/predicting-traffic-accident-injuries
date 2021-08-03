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
            df[col] = df[col].astype("string")

def transform_and_store_data(dbname, query, col_types_dict, table_name):
    print(f"Retrieving raw {table_name} data from database...")
    df = get_sql_data(db_name=dbname, query=query)
    print(f"Transforming {table_name} data...")
    for dtype, cols in col_types_dict.items():
        convert_df_columns(dtype, df, cols)
    
    # Dropping columns
    if table_name == "crashes":
        drop_cols = ["rd_no", "crash_date_est_i", "private_property_i", 
        "date_police_notified", "sec_contributory_cause", "street_no", 
        "street_name", "beat_of_occurrence", "photos_taken_i", 
        "statements_taken_i", "dooring_i", "work_zone_i", "work_zone_type", 
        "workers_present_i", "most_severe_injury", "injuries_fatal", 
        'injuries_incapacitating', 'injuries_non_incapacitating',
       'injuries_reported_not_evident', 'injuries_no_indication', 
       'injuries_unknown', "latitude", "longitude"]
        df.drop(columns=drop_cols, inplace=True)
    elif table_name == "people":
        drop_cols = ["cell_phone_use", "bac_result_value", "bac_result", 
        "ems_run_no", "ems_agency", "hospital", "injury_classification", 
        "zipcode", "crash_date", "rd_no"]
        df.drop(columns=drop_cols, inplace=True)
    
    # Removing NaN for total injuries
    df = df.loc[~df["injuries_total"].isna(), :]

    alchemy_engine = make_alchemy_engine(dbname=dbname)
    print(f"Writing {table_name} data to database...")
    df.to_sql(
        name=table_name, con=alchemy_engine, if_exists="replace", 
        index=False)
    alchemy_engine.dispose()
    return None


if __name__ == '__main__':
    print("Starting program...")

    # Defining SQL queries
    crashes_raw_query = """
        SELECT *
        FROM crashes_raw;
        """
    people_raw_query = """
        SELECT *
        FROM people_raw;
        """

    # Defining column datatypes
    crashes_col_types = {
        "datetime": ["crash_date", "date_police_notified"],
        "integer": ["posted_speed_limit", "lane_cnt", "street_no", 
            "beat_of_occurrence", "num_units", "injuries_total", 
            "injuries_fatal", "injuries_incapacitating", 
            "injuries_non_incapacitating", "injuries_reported_not_evident", 
            "injuries_no_indication", "injuries_unknown", "crash_hour", 
            "crash_day_of_week", "crash_month"],
        "float": ["latitude", "longitude"],
        "string": ["crash_record_id", "rd_no", "crash_date_est_i", 
            "traffic_control_device", "device_condition", "weather_condition", 
            "lighting_condition", "first_crash_type", "trafficway_type", 
            "alignment", "roadway_surface_cond", "road_defect", "report_type", 
            "crash_type", "intersection_related_i", "hit_and_run_i", "damage", 
            "prim_contributory_cause", "sec_contributory_cause", 
            "street_direction", "street_name", "photos_taken_i", 
            "statements_taken_i", "dooring_i", "work_zone_i", "work_zone_type", 
            "workers_present_i", "most_severe_injury"]}
    people_col_types = {
        "datetime": ["crash_date"],
        "integer": ["age"],
        "float": ["bac_result_value"],
        "string": ["person_id", "person_type", "crash_record_id", "rd_no", 
            "vehicle_id", "seat_no", "city", "state", "zipcode", "sex", 
            "drivers_license_state", "drivers_license_class", 
            "safety_equipment", "airbag_deployed", "ejection", 
            "injury_classification", "hospital", "ems_agency", "ems_run_no", 
            "driver_action", "driver_vision", "physical_condition", 
            "pedpedal_location", "bac_result", "cell_phone_use"]}

    # Transforming and storing data
    transform_and_store_data(
        dbname="chi-traffic-accidents", query=crashes_raw_query, 
        col_types_dict=crashes_col_types, table_name="crashes")
    transform_and_store_data(dbname="chi-traffic-accidents", 
        query=people_raw_query, col_types_dict=people_col_types, 
        table_name="people")
    
    print("Program complete.")
