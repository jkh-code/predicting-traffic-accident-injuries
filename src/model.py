import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from sklearn.preprocessing import OneHotEncoder, MinMaxScaler
from sklearn.dummy import DummyRegressor
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.linear_model import LinearRegression, Lasso, LassoCV
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.metrics import mean_squared_error

from typing import Union
import time
import joblib

from raw_to_transformed_data import get_sql_data

np.set_printoptions(suppress=True)
plt.style.use("ggplot")

ModelRegressor = Union[
    LinearRegression, RandomForestRegressor, GradientBoostingRegressor]

class PredictionModel:
    """Create and implement model used for predicting results."""

    def __init__(
            self, model_path: str, scalar_path: Union[None, str]=None, 
            encoder_path: Union[None, str]=None) -> None:
        """Initialize PredictionModel object."""
        self.model_ = joblib.load(model_path)
        if scalar_path:
            self.scalar_ = joblib.load(scalar_path)
        if encoder_path:
            self.encoder_ = joblib.load(encoder_path)
        
        return None
    
    def transform(self, X: pd.DataFrame) -> pd.DataFrame:
        """Transform X for use in predictions."""
        numeric_cols = ["posted_speed_limit", "num_units", "crash_hour"]
        category_cols = X.columns.difference(numeric_cols)

        # Transform numeric columns
        continuous = X[numeric_cols].copy()
        X = X.drop(columns=numeric_cols)
        scalar = self.scalar_
        transformed = scalar.transform(continuous)
        transformed = pd.DataFrame(transformed, columns=numeric_cols)
        X = pd.concat([X, transformed], axis=1)

        # Transform categorical columns
        encoder = self.encoder_
        transformed = encoder.transform(X[category_cols])
        matrix_cols = []
        for col, ele in zip(category_cols, encoder.categories_):
            for e in ele:
                matrix_cols.append(col + "_" + e.lower())
        X = pd.concat(
            [X[numeric_cols].reset_index(drop=True), pd.DataFrame(
                transformed.toarray(), columns=matrix_cols)], 
            axis=1)
        
        return X

    def predict(self, X) -> pd.DataFrame:
        """Predict value(s)."""
        model = self.model_
        y_pred = model.predict(X)
        y_pred = np.clip(y_pred, a_min=0, a_max=None)
        y_pred = np.round(y_pred, 0)
        return y_pred.astype(int)

def cv_regression_model(
        model: ModelRegressor, X: pd.DataFrame, y: pd.DataFrame, 
        scoring: str="neg_mean_squared_error", 
        cv: int=5) -> np.ndarray:
    """Perform cross validation on regression models."""
    rmses = cross_val_score(
        model, X, y, scoring=scoring, cv=cv)
    avg_rmse = np.mean(np.sqrt(-rmses))
    return avg_rmse, np.sqrt(-rmses)

def evaluate_regression_models(
        X_train: pd.DataFrame, y_train: pd.DataFrame, X_test: pd.DataFrame, 
        y_test: pd.DataFrame, run: bool=False) -> None:
    """Evaluate linear regression, random forest, and gradient boosted
    regressors."""
    if not run:
        return None

    model_lr = LinearRegression()
    model_rf = RandomForestRegressor(
        n_estimators=50,
        max_features="sqrt")
    model_gb = GradientBoostingRegressor(
        learning_rate=0.1,
        n_estimators=100,
        max_depth=3,
        min_samples_leaf=1,
        min_samples_split=2)
    models_all = [model_lr, model_rf, model_gb]

    # Baseline model
    model_dum = DummyRegressor(strategy="mean")
    model_dum.fit(X_train, y_train)
    y_pred = model_dum.predict(X_test)
    rmse_dum = np.sqrt(mean_squared_error(y_test, y_pred))
    print(f"RMSE dum: {rmse_dum:.4f}")

    scores = []
    score_lists = []
    for model in models_all:
        score, lst = cv_regression_model(model, X_train, y_train)
        scores.append(score)
        score_lists.append(lst)
        print(f"RMSE for {model}: {score:.4f}")
        print(lst)

    return None

def evaluate_model_times(
        X_train: pd.DataFrame, y_train: pd.DataFrame, X_test: pd.DataFrame, 
        y_test: pd.DataFrame, run: bool=False) -> Union[pd.DataFrame, None]:
    """Evaluate fitting and predicting time for models."""
    if not run:
        return None

    print("Evaluating models...")
    model_lr = LinearRegression()
    model_gb = GradientBoostingRegressor(
        learning_rate=0.1,
        n_estimators=100,
        max_depth=3,
        min_samples_leaf=1,
        min_samples_split=2)
    models_all = [model_lr, model_gb]
    
    fit_times = []
    pred_times = []
    rmse_scores = []
    for model in models_all:
        print(f"Evaluating model: {model}")
        model_ = model

        start_time = time.time()
        model_.fit(X_train, y_train)
        model_time = time.time() - start_time
        fit_times.append(model_time)

        start_time = time.time()
        y_pred = model_.predict(X_test)
        pred_time = time.time() - start_time
        pred_times.append(pred_time)

        rmse = np.sqrt(mean_squared_error(y_test, y_pred))
        rmse_scores.append(rmse)
    
    df = pd.DataFrame({
        "model": models_all, "rmse": rmse_scores, "fit_time": fit_times, 
        "pred_time": pred_times})
    print(df)
    return df

def create_linear_regression_model(
        X_train: pd.DataFrame, y_train: pd.DataFrame, X_test: pd.DataFrame, 
        y_test: pd.DataFrame, run: bool=False, 
        save: bool=True) -> Union[None, LinearRegression]:
    """Create and save final linear regression model."""
    if not run:
        return None

    model = LinearRegression()
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))

    print(f"Model RMSE: {rmse}")

    if save:
        joblib.dump(model, "./models/logistic-reg-model.pkl")

    return model

def evaluate_with_lasso_regression_plot(
        X_train: pd.DataFrame, y_train: pd.DataFrame, limit_plot: bool=False,
        run: bool=False, save: bool=True) -> None:
    """Plot the beta versus alpha curves to eyeball important features."""
    if not run:
        return None
    print("Evaluating features with lasso...")
    columns = X_train.columns
    num_features = X_train.shape[1]
    num_alphas = 50
    min_alpha_exp = -6
    max_alpha_exp = -1
    coefs = np.zeros((num_alphas, num_features))
    alphas = np.logspace(min_alpha_exp, max_alpha_exp, num_alphas)
    for i, alpha in enumerate(alphas):
        model = Lasso(alpha=alpha)
        model.fit(X_train, y_train)
        coefs[i] = model.coef_

    # Extracting columns with non-zero values after the 26th element
    print("Plotting beta as a function of alpha curves...")
    fig, ax = plt.subplots(figsize=(10, 5))
    if limit_plot:
        non_zero_indices = np.where(coefs[26, :] != 0)[0]
        for feature in non_zero_indices:
            plt.plot(
                alphas, coefs[:, feature],
                label=r"$\beta$_{}".format(columns[feature]))
        ax.set_title(
            r"Lasso Regression $\beta$'s as a function of $\alpha$ for "
                + "Top Features")
        ax.legend(title=None, loc="upper right", bbox_to_anchor=(1, 1))
    else:
        for feature in range(num_features):
            plt.plot(
                alphas, coefs[:, feature],
                label=r"$\beta$_{}".format(columns[feature]))

        ax.axvline(0.00003274, color="black")
        ax.text(
            0.00003274, 0.65, r"  $\alpha=3.274\mathrm{e}{-5}$", 
            transform=ax.get_xaxis_text1_transform(0)[0])

        ax.set_title(r"Lasso Regression $\beta$'s as a function of $\alpha$")

    ax.set_xscale("log")
    ax.set_xlabel(r"$\alpha$")
    ax.set_ylabel(r"$\beta$")
    fig.tight_layout()
    if save:
        plt.savefig("./images/lasso-regression-beta-alpha-plot.png")

    return None

def create_lasso_regression_model(
        X_train: pd.DataFrame, y_train: pd.DataFrame, X_test: pd.DataFrame, 
        y_test: pd.DataFrame, run: bool=False, save: bool=True
        ) -> Union[None, Lasso]:
    """Create and save lasso regression model."""
    if not run:
        return None

    # Create model
    print("Creating lasso CV model...")
    model = LassoCV(n_alphas=250, cv=5, n_jobs=-1)

    print("Fitting lasso CV model...")
    start_time = time.time()
    model.fit(X_train, y_train)
    fit_time = time.time()-start_time

    fit_alpha = model.alpha_
    fit_coefs = model.coef_

    print("Predicting with lasso CV model...")
    start_time = time.time()
    y_pred = model.predict(X_test)
    pred_time = time.time()-start_time

    rmse = np.sqrt(mean_squared_error(y_test, y_pred))

    # Feature selection
    importance = np.abs(model.coef_)
    keep_features = X_train.columns[importance > 0]
    discard_features = X_train.columns[importance == 0]

    # Save model
    if save:
        print("Saving lasso CV model...")
        joblib.dump(model, "./models/lasso-reg-model.pkl")
    
    # Model report
    print("Lasso CV model report:")
    print("----------------------")
    print(f"RMSE     : {rmse}")
    print(f"Alpha    : {fit_alpha}")
    print(f"Pred time: {pred_time}")
    print("")
    print(f"Features to keep: {len(keep_features)}")
    print(f"Features to keep: {keep_features}")
    print(f"Features to drop: {len(discard_features)}")
    print(f"Features to drop: {discard_features}")

    return model

if __name__ == '__main__':
    print("Starting program...")

    drop_additional = True
    save_elements = False

    # Get crashes data
    query_crashes = """
    SELECT *
    FROM crashes_joined;
    """
    dbname = "chi-traffic-accidents"
    print("Accessing data from database...")
    df_crashes = get_sql_data(dbname, query_crashes)

    # Transforming df_crashes for preliminary model
    print("Transforming data...")
    drop_cols = ['crash_record_id', 'crash_date', 'report_type', 
        'prim_contributory_cause', 'intersection_related_i', 'hit_and_run_i', 
        'lane_cnt', 'has_injuries']
    if drop_additional:
        drop_additional = ['num_bikes_involved', 'num_extricated', 
            "num_pedestrians_involved", "num_ejected"]
    else:
        drop_additional = []
    df_crashes = df_crashes.drop(columns=drop_cols+drop_additional)

    df_crashes = df_crashes.rename(columns={"crash_day_of_week": "crash_day"})
    df_crashes["street_direction"] = (
        df_crashes["street_direction"]
            .fillna(df_crashes["street_direction"].mode()[0]))

    # Create X and y
    y = df_crashes.pop("injuries_total")
    X = df_crashes.copy()
    del df_crashes

    # Transforming X and y for modeling
    if drop_additional:
        numeric_cols = ["posted_speed_limit", "num_units", "crash_hour"]
    else:
        numeric_cols = ["posted_speed_limit", "num_units", "crash_hour", 
            "num_bikes_involved", "num_pedestrians_involved", 
            "num_extricated", "num_ejected"]
    
    # MinMax scale
    continuous = X[numeric_cols].copy()
    X = X.drop(columns=numeric_cols)
    scaler = MinMaxScaler()
    transformed_data = scaler.fit_transform(continuous)
    transformed_data = pd.DataFrame(transformed_data, columns=numeric_cols)
    X = pd.concat([X, transformed_data], axis=1)
    if save_elements:
        print("Saving scaler...")
        joblib.dump(scaler, "./models/scaler.pkl")

    # OneHot encode
    category_cols = X.columns.difference(numeric_cols)
    encoder = OneHotEncoder(drop=None, sparse=True)
    onehot_crashes = encoder.fit_transform(X[category_cols])
    matrix_cols = []
    for col, ele in zip(category_cols, encoder.categories_):
        for e in ele:
            matrix_cols.append(col + "_" + e.lower())
    X = pd.concat(
        [X[numeric_cols].reset_index(drop=True), pd.DataFrame(
            onehot_crashes.toarray(), columns=matrix_cols)], 
        axis=1)
    if save_elements:
        print("Saving encoder...")
        joblib.dump(encoder, "./models/encoder.pkl")
    
    print("Creating train-test split...")
    X_train, X_test, y_train, y_test = train_test_split(X, y)

    # Evaluate regression models
    evaluate_regression_models(X_train, y_train, X_test, y_test)

    # Evaluate model time
    df_eval = evaluate_model_times(X_train, y_train, X_test, y_test)

    # Create logistic model
    create_linear_regression_model(X_train, y_train, X_test, y_test)

    # Evaluate features with lasso regression plot
    evaluate_with_lasso_regression_plot(X_train, y_train)

    # Lasso regression CV
    create_lasso_regression_model(X_train, y_train, X_test, y_test)

    print("Program complete.")
