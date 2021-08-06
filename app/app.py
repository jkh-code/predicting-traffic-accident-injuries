from flask import Flask, render_template

app = Flask(__name__)

@app.route("/")
def index():
    """Display the index page."""
    return render_template("index.html")

@app.route("/about")
def about():
    return "This is an about page."

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)
