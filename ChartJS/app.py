from flask import Flask, render_template

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/line")
def line():
    return render_template("line.html")

@app.route("/bar")
def bar():
    return render_template("bar.html")

@app.route("/hbar")
def hbar():
    return render_template("hbar.html")

@app.route("/doughnut")
def doughnut():
    return render_template("doughnut.html")

if __name__ == '__main__':
    app.run()
