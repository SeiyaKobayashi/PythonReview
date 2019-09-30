from flask import Flask, render_template, request, redirect

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/register", methods=["POST"])
def register():
    if not request.form.get("name") or not request.form.get("email") \
       or not request.form.get("password") or not request.form.get("gender"):
        return redirect("/")
    elif len(request.form.get("password")) <= 3:
        return redirect("/")
    else:
        name = request.form.get("name")
        email = request.form.get("email")
        password = request.form.get("password")
        gender = request.form.get("gender")
        return render_template("success.html", name=name, email=email, password=password, gender=gender)

if __name__ == '__main__':
    app.run()
