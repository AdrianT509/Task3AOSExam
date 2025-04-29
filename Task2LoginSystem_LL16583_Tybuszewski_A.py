from flask import Flask, render_template, url_for, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_required, login_user, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length, ValidationError
from flask_bcrypt import Bcrypt

app = Flask(__name__)
#Creates the instance of the system of Database UI and Secret Key
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///Login Database.sql'
app.config['SECRET_KEY'] ='AdminSecretKey'
db = SQLAlchemy(app)

#Initialise Bcrypt
bcrypt=Bcrypt(app)

#Initialise LoginManager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

#Creates the Database for User's Username and Password
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    password = db.Column(db.String(80), nullable=False)


#Creates the Register Form for users to Register
class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired(), Length(min= 4, max= 20)], render_kw={'placeholder': 'Username'})
    password = PasswordField('Password', validators=[InputRequired(), Length(min= 4, max= 20)], render_kw={'placeholder': 'Password'})
    register= SubmitField ('Register')

#Creates the Login Form for users to log in to
class LoginForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired(), Length(min=4, max=20)], render_kw={'placeholder': 'Username'})
    password = PasswordField('Password', validators=[InputRequired(), Length(min=4, max=20)], render_kw={'placeholder': 'Password'})
    submit = SubmitField('Login')

#Validation for the username so the same username doesn't get used
def validate_username(self, username):
    existing_user_username= User.query.filter_by(username=username.data).first()
    if existing_user_username:
        raise ValidationError("This username is taken. Please try a different one")

#The user loader for flask-login 
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

#Flask page for the login
@app.route('/Log in', methods=['GET', 'POST']) 
def Login():
    form = LoginForm() 
    if form.validate_on_submit():  
        user = User.query.filter_by(username=form.username.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            if bcrypt.check_password_hash(user.password, form.password.data):
                login_user(user) 
                return redirect(url_for('dashboard'))
    return render_template('Log in Page.html', form=form) 

#Flask Page for the Register
@app.route('/Register', methods=['GET', 'POST'])
def Register():
    form = RegisterForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        new_user = User(username=form.username.data, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('Create an account Page.html')

@app.route('/dashboard')
@login_required
def dashboard():
    return f"Welcome, {current_user.username}!"

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)