from flask import Flask, render_template, redirect, url_for, flash, session, request
from flask_wtf import Form
from wtforms import StringField, PasswordField, BooleanField, TextField, TextAreaField, SubmitField, validators, ValidationError
from wtforms.validators import InputRequired, Email, Length, EqualTo
from flask_sqlalchemy  import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask.ext.mail import Message, Mail

mail = Mail()

app = Flask(__name__)

app.config['SECRET_KEY'] = 'Thisissupposedtobesecret!'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////Users/jomein/Desktop/coursework2/sourcecode/database.db'
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

app.config["MAIL_SERVER"] = "smtp.gmail.com"
app.config["MAIL_PORT"] = 465
app.config["MAIL_USE_SSL"] = True
app.config["MAIL_USERNAME"] = 'jo@mein.co.uk'
app.config["MAIL_PASSWORD"] = ''

mail.init_app(app)

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

class Rides(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    date = db.Column(db.String(30))
    time = db.Column(db.String(30))
    location = db.Column(db.String(30))
    message = db.Column(db.String(400))

    def __init__(self, name, date, time, location, message):
        self.name = name
        self.date = date
        self.time = time
        self.location = location
        self.message = message

class ContactForm(Form):
  name = TextField("Name", [validators.required("Please enter your name")], render_kw={"placeholder": "Name", "type":"name"})
  email = TextField("Email", [validators.required("Please enter your email address"), validators.Email()], render_kw={"placeholder": "Email Address", "type":"email"})
  subject = TextField("Subject", [validators.required("Please enter a subject")], render_kw={"placeholder": "Enter Subject", "type":"subject"})
  message = TextAreaField("Message", [validators.required("Please enter a message")], render_kw={"placeholder": "Message", "type":"message"})
  submit = SubmitField("Send")

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

@app.route('/events/')
def events():
    return render_template('event.html', Rides = Rides.query.all()), 200

@app.route('/contact/', methods=['GET', 'POST'])
def contact():
	form = ContactForm()

	if request.method == 'POST':
  		if form.validate() == False:
  			flash('All Fields Are Required')
  			return render_template('contact.html', form=form)
  		else:
  			msg = Message (form.subject.data, sender='form.email.data', recipients=['jo@mein.co.uk'])
      		msg.body = """
      		From: %s <%s>
     		 %s
      		""" % (form.name.data, form.email.data, form.message.data)
      		mail.send(msg)
                flash('Thank you for your message. We will get back to you shortly.')
    		return redirect('/contact/')

        elif request.method == 'GET':
            return render_template('contact.html', form=form), 200

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

@app.route('/dashboard/')
@login_required
def dashboard():
    return render_template('dashboard.html', name=current_user.username), 200

@app.route('/dashboard/create_ride/', methods=['GET', 'POST'])
@login_required
def create_ride():
   if request.method == 'POST':
      if not request.form['name'] or not request.form['date'] or not request.form['time'] or not request.form['location'] or not request.form['message']:
         flash('Please enter all the fields', 'error')
      else:
         ride = Rides(request.form['name'], request.form['date'], request.form['time'], request.form['location'],
            request.form['message'])

         db.session.add(ride)
         db.session.commit()
         return redirect(url_for('events'))
   return render_template('create_ride.html'), 200

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
