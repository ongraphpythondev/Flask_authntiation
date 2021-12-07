from flask import Flask , render_template , request , redirect , url_for
from flask.helpers import flash
from flask_sqlalchemy import SQLAlchemy
import forms
from flask_login import login_user, current_user, logout_user, login_required , UserMixin ,login_manager , LoginManager
from flask_bcrypt import Bcrypt
import os

app = Flask(__name__)
bcrypt = Bcrypt(app)


app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://postgres:1234@localhost/flask_user"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
SECRET_KEY = os.urandom(32)
app.config['SECRET_KEY'] = SECRET_KEY
db = SQLAlchemy(app)

# take reference from medial login and registration article
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(20),unique = True, nullable = False)
    email = db.Column(db.String(120), unique = True,nullable = False)
    password = db.Column(db.String(60), nullable = False)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if forms.RegistrationForm().validate_on_submit():
        register_form = forms.RegistrationForm()       
        hashed_password =   bcrypt.generate_password_hash(register_form.password.data).decode('utf-8')
        user = User(username = register_form.username.data,
                    email = register_form.email.data,
                    password = hashed_password)
        db.session.add(user)
        db.session.commit()

        user = User.query.filter_by(
               email = forms.RegistrationForm().email.data).first()
       
        if user and bcrypt.check_password_hash(
        user.password, forms.RegistrationForm().password.data):
           
            login_user(user)
            print(user)
            return render_template('profile.html', data = user)
    return render_template('registration.html', register_form = forms.RegistrationForm())



@app.route('/profile')
def profile():
    print(current_user)
    return render_template('profile.html', user = current_user)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if forms.LoginForm().validate_on_submit():
        login_form = forms.LoginForm()
        
        print(login_form.email.data)
        user = User.query.filter_by(email =  
               login_form.email.data).first()

        
        if user and bcrypt.check_password_hash(user.password, 
           login_form.password.data):
            
            login_user(user, remember = login_form.remember.data)
            return redirect('/profile')
        return render_template('login.html',error = "enter correct data", login_form = forms.LoginForm())
    return render_template('login.html', login_form = forms.LoginForm())


@app.route('/logout')
def logout():
    logout_user()
    return redirect('/login' )



# this run the Flask
if __name__ == "__main__":
    app.run(debug=True)