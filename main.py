from flask import Flask,render_template,request,redirect,session
from wtforms import Form, BooleanField, StringField, PasswordField, validators
from wtforms.validators import DataRequired
from flask_sqlalchemy import SQLAlchemy
from flask_mysqldb import MySQL
from datetime import datetime
from flask_mail import Mail
import json

#read json
with open("config.json",'r') as j:
    params = json.load(j)["params"]

app = Flask(__name__)
app.secret_key = "this is abhishek"

# Configration for MAIL
app.config.update(
    MAIL_SERVER = "smtp.gmail.com",
    MAIL_PORT = '465',
    MAIL_USE_SSL = True,
    MAIL_USERNAME = params['gmail-username'],
    MAIL_PASSWORD = params['gmail-password']
)
mail = Mail(app)


# Servers
local_server = True
if(local_server):
    app.config['SQLALCHEMY_DATABASE_URI'] = params["local_uri"]
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = params["production_uri"]
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# DATABASE CLASS FOR BLOG POSTS
class Post(db.Model):
    sno = db.Column(db.Integer,primary_key=True)
    title = db.Column(db.String(100),nullable=False)
    subtitle = db.Column(db.String(100),nullable=False)
    slug = db.Column(db.String(50),nullable=False)
    content = db.Column(db.String(300),nullable=False)
    date = db.Column(db.DateTime,default=datetime.utcnow)

# DATABASE CLASS FOR CONTACT
class Contact(db.Model):
    sno = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(50),nullable=False)
    email = db.Column(db.String(50),nullable=False)
    phone_num = db.Column(db.String(25),nullable=False)
    msg = db.Column(db.String(200),nullable=False)
    date = db.Column(db.DateTime,default=datetime.utcnow)

# HOME PAGE
@app.route('/')
def home():
    posts = Post.query.all()[0:params["num_of_home_post"]]
    return render_template('index.html',params=params,posts=posts)

# ALL BLOG POSTS
@app.route('/all_blogs')
def all_blog():
    posts = Post.query.all()
    return render_template('all_blogs.html',posts=posts,params=params)

# SERVICES
@app.route('/services')
def services():
   return render_template('services.html')

# CONTACT ROUTE
@app.route('/contact',methods=['GET','POST'])
def contact():
    if request.method == 'POST':
        e_name = request.form.get('name')
        e_email = request.form.get('email')
        e_phone = request.form.get('phone')
        e_message = request.form.get('message')
        e_entry = Contact(name=e_name,phone_num=e_phone,msg=e_message,email=e_email)
        db.session.add(e_entry)
        db.session.commit()
        mail.send_message('New Message From Web-Blog/Contacts',sender=(e_name,e_email),recipients=[params['gmail-username']],body = e_message + "\n" + e_phone)
    return render_template('contact.html')

# LOGIN ADMIN ROUTE
@app.route('/login',methods=['GET','POST'])
def login():
    if 'user' in session and session['user'] == params['admin_name']:
        posts = Post.query.all()
        return render_template('dashboard.html',params=params,posts=posts)
    if request.method == 'POST':
        username = request.form.get('uname')
        userpass = request.form.get('pass')
        if username == params['admin_name'] and userpass == params['admin_pw']:
            session['user'] == username
            posts = Post.query.all()
            return render_template('dashboard.html',params=params,posts=posts)
    else:
        return render_template('login.html',params=params)

# DASHBOARD ROUTE
@app.route('/dashboard',methods=['GET','POST'])
def dashboard():
    posts = Post.query.all()
    return render_template('dashboard.html',posts=posts,params=params)

# ALL POST ROUTE 
@app.route('/post/<string:post_slug>',methods=['GET'])
def post_route(post_slug):
   post = Post.query.filter_by(slug=post_slug).first()
   return render_template('post.html',params=params,post=post)

# CREATE NEW POSTS
@app.route('/create',methods=['GET','POST'])
def create():
    if request.method == 'POST':
        c_title = request.form.get('title')
        c_subtitle = request.form.get('subtitle')
        c_slug = request.form.get('slug')
        c_content = request.form.get('content')
        c_entry = Post(title=c_title,subtitle=c_subtitle,content=c_content,slug=c_slug)
        db.session.add(c_entry)
        db.session.commit()
        return redirect('/create')
    return render_template('create.html')

# EDIT BLOG POSTS ROUTE
@app.route('/edit/<string:slug>', methods=['GET','POST'])
def edit(slug):
    if request.method == 'POST':
        post = Post.query.filter_by(slug=slug).first()
        box_title = request.form.get('title')
        tline = request.form.get('tline')
        slug = request.form.get('slug')
        content = request.form.get('content')
        date = datetime.now()
        print(post)
        post.title = box_title
        post.subtitle = tline
        post.slug = slug
        post.content = content
        post.date = date
        db.session.commit()
        return redirect('/edit/'+slug)
    post = Post.query.filter_by(slug=slug).first()
    return render_template('edit.html',params=params,post=post)

# DELETE BLOG POST ROUTE
@app.route('/delete/<int:sno>',methods=['GET','POST'])
def delete(sno):
    post = Post.query.filter_by(sno=sno).first()
    db.session.delete(post)
    db.session.commit()
    return redirect("/dashboard")

# LOGOUT ADMIN ROUTE
@app.route('/logout')
def logout():
    if 'user' in session:
        session.pop('user')
    return redirect('/')



if __name__ == "__main__":
    app.run(debug=True)