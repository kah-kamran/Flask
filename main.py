from flask import Flask, render_template, request, session
from flask_sqlalchemy import SQLAlchemy
from datetime import date
from flask_mail import Mail, Message
import json

with open('config.json', 'r') as c:
    params = json.load(c)["params"]

local_server = True
app = Flask(__name__)
app.secret_key = 'super-secret-key'

app.config.update(
    MAIL_SERVER = 'smtp.gmail.com',
    MAIL_PORT = '465',
    MAIL_USE_SSL = True,
    MAIL_USERNAME = params['gmail-user'],
    MAIL_PASSWORD = params['gmail-password']
)
mail = Mail(app)

if (local_server):
    app.config["SQLALCHEMY_DATABASE_URI"] = params["local_uri"]
else:
    app.config["SQLALCHEMY_DATABASE_URI"] = params["prod_uri"]

db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique=True, nullable=False)
    email = db.Column(db.String)

class Contacts(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    phone_num = db.Column(db.String, nullable=False)
    msg = db.Column(db.String,  nullable=False)
    date = db.Column(db.String, nullable=False)
    email = db.Column(db.String)

class Posts(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    slug = db.Column(db.String, nullable=False)
    content = db.Column(db.String,  nullable=False)
    date = db.Column(db.String, nullable=False)

with app.app_context():
    db.create_all()

@app.route("/")
def home():
    # posts = Posts.query.all()
    posts = Posts.query.order_by(Posts.sno).all()[0:3]
    return render_template('index.html', params=params, posts=posts)

@app.route("/dashboard" , methods=['GET', 'POST'])
def dashboard():
    if ('user' in session and session['user'] == params['admin_user']):
        return render_template('dashboard.html', params=params)

    if request.method=='POST':
        email = request.form.get('email')
        password = request.form.get('password')
        if (email == params['admin_user'] and password == params['admin_password']):
            session['user']= email
            return render_template('dashboard.html', params=params)
    else:
        return render_template('login.html', params=params)


@app.route("/post/<string:post_slug>", methods=["GET"])
def post_routes(post_slug):
    post = Posts.query.filter_by(slug=post_slug).first()
    return render_template('post.html', params=params, post=post)

@app.route("/about")
def about():
    return render_template('about.html', params=params)


@app.route("/contact", methods = ['GET', 'POST'])
def contact():
    if (request.method=='POST'):
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        message = request.form.get('message')
        current_date = date.today()

        entry = Contacts(name=name, phone_num=phone, msg=message, email=email, date=current_date)
        db.session.add(entry)
        db.session.commit()
        # msg =  Message('Hello from the other side!', sender = email, recipients = [params["gmail-user"]])
        # msg.body = message + "\n" + phone ,
        # mail.send(msg)
        mail.send_message('New message from ' + name,
                            sender = email,
                            recipients = [params["gmail-user"]],
                            body = message + "\n" + phone,
                            )
    return render_template('contact.html', params=params)


app.run(debug=True)