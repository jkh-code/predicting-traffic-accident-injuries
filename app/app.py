from flask import Flask, render_template, request, redirect, url_for
import pandas as pd
import numpy as np

from src.model import PredictionModel

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    """Display the index page."""
    return render_template("index.html", page_title="Welcome")

@app.route("/questions", methods=["GET", "POST"])
def questions():
    """Display the questions page."""
    return render_template("questions.html", page_title="Form")

@app.route("/results", methods=["GET", "POST"])
def results():
    """Display the results page."""
    if request.method == "POST":
        # Convert HTML names to model names
        answers_d = dict()
        for key, value in request.form.items():
            key = key.replace("-", "_")
            answers_d[key] = [value]
        X = pd.DataFrame.from_dict(answers_d)

        # Transform and predict
        model_path = "./models/lasso-reg-model.pkl"
        scalar_path = "./models/scaler.pkl"
        encoder_path = "./models/encoder.pkl"
        prediction_model = PredictionModel(
            model_path, scalar_path, encoder_path)
        X_transformed = prediction_model.transform(X)
        y_pred = prediction_model.predict(X_transformed)

        cols = X.columns.to_list()
        cols = [col.replace("_", " ").title() for col in cols]
        table = X.values.reshape(-1, 1)
        titles = np.array(cols).reshape(-1, 1)
        result = y_pred
        comb = np.concatenate((titles, table), axis=1)

        return render_template(
            "results.html", comb=comb, result=result, page_title="Results")
    else:
        return redirect(url_for("index"), page_title="Welcome")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)
