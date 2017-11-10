from flask import Flask, render_template, redirect, url_for, flash, session, request
from flask_wtf import Form
from wtforms import StringField, PasswordField, BooleanField, TextField, TextAreaField, SubmitField, validators, ValidationError
from wtforms.validators import InputRequired, Email, Length, EqualTo
from flask_sqlalchemy  import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user

app = Flask(__name__)

app.config['SECRET_KEY'] = 'Thisissupposedtobesecret!'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////Users/jomein/Desktop/coursework2/sourcecode/database.db'
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class LoginForm(Form):
    username = StringField('username', validators=[InputRequired(), Length(min=4, max=15)], render_kw={"placeholder": "Enter Username", "type":"username"})
    password = PasswordField('password', validators=[InputRequired(), Length(min=8, max=80)], render_kw={"placeholder": "Enter Password", "type":"password"})
    remember = BooleanField()

class RegisterForm(Form):
    email = StringField('email', validators=[InputRequired(), Email(message='Invalid email'), Length(min=6, max=40)], render_kw={"placeholder": "Enter Email", "type":"email"})
    username = StringField('username', validators=[InputRequired(), Length(min=4, max=15)], render_kw={"placeholder": "Enter Username", "type":"username"})
    password = PasswordField('password', validators=[InputRequired(), Length(min=4, max=40)], render_kw={"placeholder": "Enter Password", "type":"password"})

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(15), unique=True)
    email = db.Column(db.String(40), unique=True)
    password = db.Column(db.String(40))

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def index():
    return render_template('index.html'), 200

@app.route('/about/')
def about():
    return render_template('about.html'), 200

@app.route('/membership/')
def membership():
    return render_template('membership.html'), 200

@app.route('/westhill_bike_ride/')
def annual_ride():
    return render_template('westhill_bike_ride.html'), 200

@app.route('/signup/', methods=['GET', 'POST'])
def signup():
    form = RegisterForm()

    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data, method='sha256')
        new_user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('dashboard'))

    return render_template('signup.html', form=form, errors=form.errors.items()), 200

@app.route('/login/', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            if check_password_hash(user.password, form.password.data):
                login_user(user, remember=form.remember.data)
            	return redirect(url_for('dashboard'))
            else:
            	flash("Invalid username or password")

    return render_template('login.html', form=form, errors=form.errors.items()), 200

@app.route('/logout/')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index')), 200

@app.errorhandler(404)
def page_not_found(error):
	return render_template('404.html'), 404

if __name__ == '__main__':
   db.create_all()
   app.run(debug = True)
