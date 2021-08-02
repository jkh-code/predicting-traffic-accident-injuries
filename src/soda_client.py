import pandas as pd
from sodapy import Socrata
from os import environ
import psycopg2 as pg2
from sqlalchemy import create_engine
from sqlalchemy.engine.base import Engine

from typing import Literal

pd.set_option("display.max_columns", None)

class SodaClient:
    """
    Client for downloading and storing traffic crashes and traffic crashes 
    people raw data from Chicago Data Portal.
    """

    def __init__(
            self, 
            app_token: str=environ["CHI_API_KEY"],
            dbname: str="chi-traffic-accidents",
            port: int=5432
            ) -> None:
        """Initialize the client."""
        self.app_token = app_token
        self.dbname = dbname
        self.port = port

        self.username = environ['PG_USER']
        self.password = environ['PG_PASSWORD']
        self.host = environ['PG_HOST']

        self.dataset = None
        self.dataset_code = None
        self.sql_table = None

        return None
    
    def get_raw_data(self) -> pd.DataFrame:
        """Connect to SODA API and fetch data."""
        print("Connecting to SODA API...")
        soda_client = Socrata("data.cityofchicago.org", self.app_token)

        print("Retrieving data from API...")
        raw_data = soda_client.get_all(self.dataset_code, content_type="json")
        df_data = pd.DataFrame.from_records(raw_data)

        print("Closing SODA API connection...")
        soda_client.close()

        return df_data

    def store_raw_data(self, df: pd.DataFrame) -> None:
        """Connect to PostgreSQL database and store raw data."""
        print("Connecting to database...")
        engine_string = (
            f"postgresql://{self.username}:{self.password}@{self.host}"
            + f":{self.port}/{self.dbname}")
        alchemy_engine = create_engine(engine_string)

        print("Writing to database...")
        df.to_sql(
            self.sql_table, alchemy_engine, index=False, if_exists="replace")
        
        print("Closing database connection...")
        alchemy_engine.dispose()

        return None
    
    def collect_data(
            self, dataset: Literal["crashes", "people"]="crashes") -> None:
        """Fetch data from the SODA API and save raw data to PostgreSQL 
        database"""
        self.dataset = dataset
        if self.dataset == "crashes":
            self.dataset_code = "85ca-t3if"
            self.sql_table = "crashes_raw"
        elif self.dataset == "people":
            self.dataset_code = "u6pd-qa9d"
            self.sql_table = "people_raw"
        else:
            self.dataset_code = None
            raise ValueError("`dataset` must be set to 'crashes' or 'people'.")
        
        print(f"Collecting the {self.dataset} dataset...")
        df_data = self.get_raw_data()
        if self.dataset == "crashes":
            df_data = df_data.drop(columns=["location"])

        self.store_raw_data(df_data)
        print(f"Completed collecting the {self.dataset} dataset...\n")


if __name__ == '__main__':
    print("Starting program...\n")
    datasets = ["crashes", "people"]
    for dataset in datasets:
        soda_client = SodaClient()
        soda_client.collect_data(dataset)

    print("Program ended.")
