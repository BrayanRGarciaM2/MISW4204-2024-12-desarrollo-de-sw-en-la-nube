from flask import Flask, jsonify


app = Flask(__name__)


@app.route("/")
def hello_world():
    return jsonify(hello="world")

@app.route("/brayan")
def brayan():
    return jsonify(brayan="garcia")

if __name__ == '__main__':
    print("Hello World")