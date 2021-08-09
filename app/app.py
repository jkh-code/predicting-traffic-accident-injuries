from flask import Flask, render_template, request

app = Flask(__name__)

@app.route("/")
def index():
    """Display the index page."""
    return render_template("index.html")

@app.route("/questions", methods=["GET", "POST"])
def questions():
    return render_template("questions.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)
