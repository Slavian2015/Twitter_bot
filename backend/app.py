from flask import Flask, render_template, request, redirect, session, flash, url_for
from functools import wraps
import json

app = Flask(__name__)
main_path = '/usr/local/WB/data/users.json'


# Login
@app.route('/')
@app.route('/login', methods=['POST', 'GET'])
def login():
    status = True
    if request.method == 'POST':
        email = request.form["email"]
        pwd = request.form["upass"]

        with open(main_path, "r") as fj:
            data_full = json.load(fj)

        data = data_full.get(email, None)

        if data:
            session['logged_in'] = True
            session['username'] = data["UNAME"]
            flash('Login Successfully', 'success')
            return redirect('home')
        else:
            flash('Invalid Login. Try Again', 'danger')
    return render_template("login.html")


# check if user logged in
def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('Unauthorized, Please Login', 'danger')
            return redirect(url_for('login'))

    return wrap


# Registration
@app.route('/reg', methods=['POST', 'GET'])
def reg():
    status = False
    if request.method == 'POST':
        name = request.form["uname"]
        email = request.form["email"]
        pwd = request.form["upass"]

        with open(main_path, "r") as fj:
            data = json.load(fj)

            if name in data.keys():
                flash('This email already exists', 'error!')
                return render_template("reg.html", status=status)

        with open(main_path, 'w', encoding='utf-8') as f:
            data[email] = {"UPASS": pwd, "UNAME": name}
            json.dump(data, f, ensure_ascii=False, indent=4)

        flash('Registration Successfully. Login Here...', 'success')
        return redirect('login')
    return render_template("reg.html", status=status)


# Home page
@app.route("/home")
@is_logged_in
def home():
    return render_template('home.html')


# logout
@app.route("/logout")
def logout():
    session.clear()
    flash('You are now logged out', 'success')
    return redirect(url_for('login'))


if __name__ == '__main__':
    app.secret_key = 'secret123'
    app.run(host='0.0.0.0', port=4547, debug=True)
