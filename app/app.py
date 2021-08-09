from flask import Flask, render_template, request, redirect, url_for
import pandas as pd

from src.model import PredictionModel

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    """Display the index page."""
    return render_template("index.html")

@app.route("/questions", methods=["GET", "POST"])
def questions():
    return render_template("questions.html")

@app.route("/results", methods=["GET", "POST"])
def results():
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
        X = prediction_model.transform(X)
        y_pred = prediction_model.predict(X)
        print(y_pred)

        return render_template("results.html")
    else:
        return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)
