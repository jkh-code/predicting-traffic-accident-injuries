import pandas as pd
from raw_to_transformed_data import get_sql_data


if __name__ == '__main__':
    db_name = "chi-traffic-accidents"
    query_crashes = """
        SELECT *
        FROM crashes_joined
        LIMIT 100;"""
    query_people = """
        SELECT *
        FROM people
        LIMIT 100;"""
    
    df_crashes = get_sql_data(db_name, query_crashes)
    df_people = get_sql_data(db_name, query_people)

    df_crashes.to_csv("./data/crashes-data-sample.csv", index=False)
    df_crashes.to_csv("./data/people-data-sample.csv", index=False)
    