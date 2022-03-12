from flask import Flask, render_template, request, redirect, session, flash, url_for
from functools import wraps
import json
from requests_oauthlib import OAuth1Session
import random
import twit

app = Flask(__name__)
main_path = '/usr/local/WB/data/users.json'
main_keys_path = '/usr/local/WB/data/keys.json'
main_links_path = '/usr/local/WB/data/my_links.json'


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
            session['email'] = email

            with open(main_keys_path, "r") as fj:
                data_full = json.load(fj)

            session['data'] = data_full[email]

            flash('Login Successfully', 'success')
            return redirect('home')
        else:
            flash('Invalid Login. Try Again', 'danger')
    return render_template("login.html")


@app.route('/keys', methods=['POST', 'GET'])
def keys():
    if request.method == 'POST':
        consumer_key = request.form["consumer_key"]
        consumer_secret = request.form["consumer_secret"]

        request_token_url = "https://api.twitter.com/oauth/request_token?oauth_callback=oob&x_auth_access_type=write"
        oauth = OAuth1Session(consumer_key, client_secret=consumer_secret)

        try:
            fetch_response = oauth.fetch_request_token(request_token_url)
        except ValueError:
            flash("There may have been an issue with the consumer_key or consumer_secret you entered.", 'danger')

        resource_owner_key = fetch_response.get("oauth_token")
        resource_owner_secret = fetch_response.get("oauth_token_secret")
        print("Got OAuth token: %s" % resource_owner_key)

        base_authorization_url = "https://api.twitter.com/oauth/authorize"
        authorization_url = oauth.authorization_url(base_authorization_url)

        session['link'] = authorization_url

        with open(main_keys_path, "r") as fj:
            data = json.load(fj)

        with open(main_keys_path, 'w', encoding='utf-8') as f:
            data[session['email']]['consumer_key'] = consumer_key
            data[session['email']]['consumer_secret'] = consumer_secret

            data[session['email']]['resource_owner_key'] = resource_owner_key
            data[session['email']]['resource_owner_secret'] = resource_owner_secret

            json.dump(data, f, ensure_ascii=False, indent=4)
        return redirect('pincode')

    return render_template("keys.html")


@app.route('/pincode', methods=['POST', 'GET'])
def pincode():
    if request.method == 'POST':
        new_pincode = request.form["pincode"]

        with open(main_keys_path, "r") as fj:
            data = json.load(fj)

        resource_owner_key = data[session['email']]['resource_owner_key']
        resource_owner_secret = data[session['email']]['resource_owner_secret']

        consumer_key = data[session['email']]['consumer_key']
        consumer_secret = data[session['email']]['consumer_secret']

        access_token_url = "https://api.twitter.com/oauth/access_token"
        oauth = OAuth1Session(
            consumer_key,
            client_secret=consumer_secret,
            resource_owner_key=resource_owner_key,
            resource_owner_secret=resource_owner_secret,
            verifier=new_pincode,
        )
        oauth_tokens = oauth.fetch_access_token(access_token_url)

        access_token = oauth_tokens["oauth_token"]
        access_token_secret = oauth_tokens["oauth_token_secret"]

        with open(main_keys_path, 'w', encoding='utf-8') as f:
            data[session['email']]['access_token'] = access_token
            data[session['email']]['access_token_secret'] = access_token_secret

            json.dump(data, f, ensure_ascii=False, indent=4)
        flash('Connected Account Successfully...', 'success')
        return redirect('home')

    return render_template("pincode.html")


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
            data[email] = {"UPASS": pwd, "UNAME": name, "LINK": []}
            json.dump(data, f, ensure_ascii=False, indent=4)

        with open(main_keys_path, "r") as fj:
            data = json.load(fj)

        with open(main_keys_path, 'w', encoding='utf-8') as f:
            data[email] = {"consumer_key": [], "consumer_secret": [], "access_token": [], "access_token_secret": [],
                           "resource_owner_key": [], "resource_owner_secret": []}
            json.dump(data, f, ensure_ascii=False, indent=4)

        flash('Registration Successfully. Login Here...', 'success')
        return redirect('login')
    return render_template("reg.html", status=status)


# Home page
@app.route("/home", methods=['POST', 'GET'])
@is_logged_in
def home():
    if request.method == 'GET':
        all_links = []
        if session['data']["access_token"]:
            with open(main_path, "r") as fj:
                data_user = json.load(fj)

            with open(main_links_path, "r") as fj:
                data_links = json.load(fj)

            for k, v in data_links.items():
                if k in data_user[session['email']]["LINKS"]:
                    all_links.append({"id": k,
                                      "link": v["link"],
                                      "new_text": random.choice(v["text"]),
                                      "status": True})
                else:
                    all_links.append({"id": k,
                                      "link": v["link"],
                                      "new_text": random.choice(v["text"]),
                                      "status": False})

        session['all_links'] = all_links

        return render_template('home.html')
    elif request.method == 'POST':
        new_id = list(request.form.keys())[0].split("_")[-1]

        with open(main_links_path, "r") as fj:
            data_links = json.load(fj)

        new_text = f'{random.choice(data_links[f"{new_id}"]["text"])}\n{data_links[f"{new_id}"]["link"]}'

        twit.new_tweet(consumer_key=session['data']['consumer_key'],
                       consumer_secret=session['data']['consumer_secret'],
                       access_token=session['data']['access_token'],
                       access_token_secret=session['data']['access_token_secret'],
                       new_text=new_text)

        with open(main_path, "r") as fj:
            data_user = json.load(fj)

        data_user[session['email']]["LINKS"].append(f"{new_id}")

        with open(main_path, 'w', encoding='utf-8') as f:
            json.dump(data_user, f, ensure_ascii=False, indent=4)

        all_links = []

        with open(main_links_path, "r") as fj:
            data_links = json.load(fj)

        for k, v in data_links.items():
            if k in data_user[session['email']]["LINKS"]:
                all_links.append({"id": k,
                                  "link": v["link"],
                                  "new_text": random.choice(v["text"]),
                                  "status": True})
            else:
                all_links.append({"id": k,
                                  "link": v["link"],
                                  "new_text": random.choice(v["text"]),
                                  "status": False})

        session['all_links'] = all_links
        flash('RUN Successfully', 'success')
        return render_template('home.html')


@app.route("/logout")
def logout():
    session.clear()
    flash('You are now logged out', 'success')
    return redirect(url_for('login'))


if __name__ == '__main__':
    app.secret_key = 'secret123'
    app.run(host='0.0.0.0', port=4547, debug=True)
