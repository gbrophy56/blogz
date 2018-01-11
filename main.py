from flask import Flask, request, redirect, render_template, session, flash, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:MyNewPass@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'thekeytomythoughts'

class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150))
    body = db.Column(db.Text)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    date = db.Column(db.DateTime)
    def __init__(self, title, body, owner_id, date=None):
        self.title = title
        self.body = body
        self.owner_id = owner_id
        if date is None:
            date = datetime.utcnow()
        self.date = date

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique =True)
    password = db.Column(db.String(50))
    blogs = db.relationship('Blog', backref="user")
    def __init__(self, username, password):
        self.username = username
        self.password = password
 
@app.before_request
def require_login():
    allowed_routes = ['login', 'blog', 'index', 'signup']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')
@app.route('/')
def index():
    users = user.query.order_by(user.username).all()
    return render_template('index.html', title="Home", users = users)       
@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        
        if user and user.password == password:
            session['username'] = username
            flash("Logged in")
            return redirect('/newpost')
        elif user and user.password != password:
            flash('Your password is incorrect', 'error')
            return render_template('login.html', username = username)
        else:
            flash('Username does not exist', 'error')
            return render_template('login.html', username = username)
    return render_template('login.html', title="login",)
@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form ['password']
        verify = request.form['verify']
        existing_user = User.query.filter_by(username=username).first()
        is_error = False
        #username check
        if not username:
            flash('You need to enter a user name', 'error')
            is_error = True
  
        elif existing_user:
            flash('Username already exists', 'error')
            is_error = True     
        
        elif len(username) < 3 or len(username) >20 or (' ' in username):
            flash('Your user name must be between 3 and 20 characters in length and contain no spaces', 'error')
            is_error = True
        if not password:
            flash('You need to enter a password', 'error')
            is_error = True
        
        elif len(password) < 3 or len(password) >20 or (' ' in password):
            flash('Your password must be between 3 and 20 characters in length and contain no spaces', 'error')
            is_error = True
        if not verify:
            flash('You need to verify your password', 'error')
            is_error = True
        elif password != verify:
            flash('Verification failed, your passwords did not match', 'error')
            is_error = True
        if is_error == True:
            return render_template('signup.html', username=username)
        else:
            new_user = User(username, password)
            db.session.add(new_user)
            db.session.commit()
            session['username'] = username
            return redirect('/newpost')
        
    return render_template('signup.html', title="signup")
@app.route('/logout')
def logout():
    del session['username']
    return redirect('/blog')
@app.route('/blog', methods=['POST', 'GET'])
def blog():
    user_username = request.args.get('user')
    blog_id = request.args.get('id')
    if blog_id:
        blog = Blog.query.get(blog_id)
        return render_template('blog.html', title="ABlog", blog=blog)
    elif user_username:
        user = User.query.filter_by(username=user_username).first()
        user_blogs = Blog.query.filter_by(owner_id=user.id).all()
        return render_template('singleUser.html', title="Usersblogs", blogs=user_blogs)
    else:
        posted_blogs = Blog.query.order_by(Blog.date.desc()).all()
        return render_template('singleUser.html', title="Blogz", blogs=posted_blogs)
@app.route('/newpost', methods=['POST', 'GET'])
def newpost():
    owner = User.query.filter_by(username=session['username']).first()
    if request.method == 'POST':
        new_title = request.form['title']
        new_body = request.form['body']
        new_blog = Blog(new_title, new_body, owner.id)
        is_error = False
        if not new_title:
            flash('You need to enter a title', 'error')
            is_error = True
        elif not new_body:
            flash('You need to enter something in your post', 'error')
            is_error = True
        if is_error == True:
            return redirect('/newpost')
        else:            
            db.session.add(new_blog)
            db.session.commit()
            return redirect(url_for('blog',id=str(new_blog.id)))
    return render_template('newpost.html', title = "newpost")
if __name__ == '__main__':
    app.run()
