import pandas as pd
import numpy as np

from sklearn.preprocessing import OneHotEncoder
from sklearn.dummy import DummyRegressor
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.metrics import mean_squared_error
from typing import Union

from raw_to_transformed_data import get_sql_data

np.set_printoptions(suppress=True)

ModelRegressor = Union[
    LinearRegression, RandomForestRegressor, GradientBoostingRegressor]

def cv_regression_model(
        model: ModelRegressor, X: pd.DataFrame, y: pd.DataFrame, 
        scoring: str="neg_mean_squared_error", 
        cv: int=5) -> np.ndarray:
    """Perform cross validation on regression models."""
    rmses = cross_val_score(
        model, X, y, scoring=scoring, cv=cv)
    avg_rmse = np.mean(np.sqrt(-rmses))
    return avg_rmse, np.sqrt(-rmses)


if __name__ == '__main__':
    # Get crashes data
    query_crashes = """
    SELECT *
    FROM crashes;
    """
    dbname = "chi-traffic-accidents"
    df_crashes = get_sql_data(dbname, query_crashes)

    # Transforming df_crashes for preliminary model
    drop_cols = ['crash_record_id', 'crash_date', 'report_type', 
        'prim_contributory_cause', 'intersection_related_i', 'hit_and_run_i', 
        'lane_cnt', 'has_injuries']
    df_crashes = df_crashes.drop(columns=drop_cols)

    df_crashes = df_crashes.rename(columns={"crash_day_of_week": "crash_day"})
    df_crashes["street_direction"] = (
        df_crashes["street_direction"]
            .fillna(df_crashes["street_direction"].mode()[0]))

    # Create X and y
    y = df_crashes.pop("injuries_total")
    X = df_crashes.copy()
    del df_crashes

    # Transforming X and y for modeling
    numeric_cols = ["posted_speed_limit", "num_units", "crash_hour"]
    category_cols = X.columns.difference(numeric_cols)
    
    encoder = OneHotEncoder(drop=None, sparse=True)
    onehot_crashes = encoder.fit_transform(X[category_cols])
    matrix_cols = []
    for col, ele in zip(category_cols, encoder.categories_):
        for e in ele:
            matrix_cols.append(col + "_" + e.lower())
    X = pd.concat(
        [X[numeric_cols], pd.DataFrame(
            onehot_crashes.toarray(), columns=matrix_cols)], 
        axis=1)
    
    X_train, X_test, y_train, y_test = train_test_split(X, y)

    # Baseline model
    model_dum = DummyRegressor(strategy="mean")
    model_dum.fit(X_train, y_train)
    y_pred = model_dum.predict(X_test)
    rmse_dum = np.sqrt(mean_squared_error(y_test, y_pred))
    print(f"RMSE dum: {rmse_dum:.4f}")

    # Evaluate regression models
    model_lr = LinearRegression()
    model_rf = RandomForestRegressor(
        n_estimators=10,
        max_features="auto")
    model_gb = GradientBoostingRegressor(
        learning_rate=0.1,
        n_estimators=100,
        max_depth=3,
        min_samples_leaf=1,
        min_samples_split=2)
    models_all = [model_lr, model_rf, model_gb]
    # models_all = [model_lr]

    scores = []
    score_lists = []
    for model in models_all:
        score, lst = cv_regression_model(model, X_train, y_train)
        scores.append(score)
        score_lists.append(lst)
        print(f"RMSE for {model}: {score:.4f}")
        print(lst)
