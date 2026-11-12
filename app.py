from flask import Flask

app = Flask(__name__)

@app.route("/")
def home():
    return "Offline Flask App Working!"

if __name__ == "__main__":
    app.run(debug=True)
