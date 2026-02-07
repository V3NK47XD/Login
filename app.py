from flask import Flask, render_template
from auth import auth

app = Flask(__name__)

# Register blueprint
app.register_blueprint(auth)

@app.route("/")
def home():
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)
