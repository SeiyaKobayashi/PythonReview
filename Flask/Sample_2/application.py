from flask import render_template, request, redirect
from init_db import app, get_db, insert_db, query_db

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

        insert_db("INSERT INTO user (name, email, password, gender) \
                   VALUES(?, ?, ?, ?)", (name, email, password, gender))
        user = query_db("SELECT * FROM user WHERE email = ?", (email,), True)

        return render_template("success.html", user=user)

@app.route("/view")
def view():
    users = query_db("SELECT * FROM user")
    return render_template("view.html", users=users)

if __name__ == '__main__':
    app.run()
