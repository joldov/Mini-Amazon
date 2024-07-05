from flask import render_template, redirect, url_for, flash, request
from werkzeug.urls import url_parse
from flask_login import login_user, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo
import math

from .models.user import User
from .models.feedback import Feedback
from .models.review_of_seller import Review_Of_Seller
from .models.purchase import Purchase


from flask import Blueprint
bp = Blueprint('users', __name__)



# flask form for user login fields
class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

# login function for displaying login page + login form
@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index.index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.get_by_auth(form.email.data, form.password.data)
        if user is None:
            flash('Invalid email or password')
            return redirect(url_for('users.login'))
        login_user(user)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index.index')

        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)

# flask form for user registration fields
class RegistrationForm(FlaskForm):
    fullname = StringField('Full Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    address = StringField('Address', validators=[DataRequired()])
    seller = BooleanField('Register as Seller?')
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(),
                                       EqualTo('password')])
    submit = SubmitField('Register')

    def validate_email(self, email):
        if User.email_exists(email.data):
            raise ValidationError('Already a user with this email.')

# flask form for withdrawing/depositing money into bank
class UpdateBankForm(FlaskForm):
    withdraw = StringField('Withdraw Amount')
    deposit = StringField('Deposit Amount')
    submit = SubmitField('Submit')

# flask form for updating user name, address, password, or email
class UpdateInfoForm(FlaskForm):
    updatename = StringField('Update Name')
    updateaddress = StringField('Update Address')
    updatepassword = StringField('Update Password')
    updateemail = StringField('Update Email')
    updateseller = BooleanField('Become Seller?')
    submit = SubmitField('Submit')

# register function for displaying register page + register form
@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index.index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        if form.email.data.count('@') != 1 or len(form.email.data.strip().split(' ')) >= 2:
            flash('Invalid email format')
        if len(form.password.data.strip().split(' ')) >= 2:
            flash('Invalid password format')
        if len(form.fullname.data.strip().split(' ')) >= 5:
            flash('Long name, is this a SQL injection attack?')
        if len(form.address.data.strip().split(' ')) >= 4:
            flash('Long address, is this a SQL injection attack?')
        if form.email.data.count('@') == 1 and len(form.email.data.strip().split(' ')) < 2 and  len(form.password.data.strip().split(' ')) < 2 and len(form.fullname.data.strip().split(' ')) < 5 and len(form.address.data.strip().split(' ')) < 4:
            if User.register(form.email.data,
                            form.password.data,
                            form.fullname.data,
                            form.address.data,
                            form.seller.data):
                flash('Congratulations, you are now a registered user!')
                return redirect(url_for('users.login'))
    return render_template('register.html', title='Register', form=form)

# this function displays all users sorted by time DESC (default), paginated with 10 users per page
@bp.route('/users/page/<int:page>')
def list_users(page):
    if current_user.is_authenticated:
        users = User.get_all_users()
        per_page = 10
        total = len(users)
        pages = math.ceil(total/per_page)
        start = page*per_page - per_page
        stop = start+per_page
        if stop >= len(users):
            page_users = users[start:]
            stop = len(users)
        else:
            page_users = users[start:stop]
        return render_template('users.html',users=page_users,number=page,pages=pages,start=start+1,stop=stop,total=total)
    else:
        return render_template('users.html', users=None)

# this function displays all users sorted by name alphabetically, paginated with 10 users per page
@bp.route('/users_by_name/page/<int:page>')
def list_users_by_name(page):
    if current_user.is_authenticated:
        users = User.get_all_users_by_name()
        per_page = 10
        total = len(users)
        pages = math.ceil(total/per_page)
        start = page*per_page - per_page
        stop = start+per_page
        if stop >= len(users):
            page_users = users[start:]
            stop = len(users)
        else:
            page_users = users[start:stop]
        return render_template('users_by_name.html',users=page_users,number=page,pages=pages,start=start+1,stop=stop,total=total)
    else:
        return render_template('users_by_name.html', users=None)

# this function displays a view for a given user, displaying id, name, email, and address. 
# if the user is a seller, seller reviews are also displayed
@bp.route('/users/<int:uid>/<int:page>/<sort>')
def list_user(uid,page,sort):
    if current_user.is_authenticated:
        user = User.get(uid)
        seller = User.seller_bool(uid)
        reviews = Review_Of_Seller.get_all_reviews_of_seller(uid)
        length = len(reviews) if reviews else 0
        return render_template('user.html',user=user,seller=seller,page=page,reviews=reviews,total=length,sort=sort)
    else:
        return render_template('user.html',user=None,seller=None,page=None,reviews=None)

# this function displays the user's balance and a button to update it
@bp.route('/bank/<int:uid>')
def get_balance(uid):
    if current_user.is_authenticated:
        balance = User.get_bank_info(uid)
        return render_template('bank.html',balance=balance)
    else:
        return render_template('bank.html',balance=None)

# this function displays the flask form for withdrawing/depositing to balance
@bp.route('/update_bank/<int:uid>',methods=['GET','POST'])
def update_bank(uid):
    if current_user.is_authenticated:
        form = UpdateBankForm()
        if form.validate_on_submit():
            if form.deposit.data is not '':
                if not form.deposit.data.isnumeric():
                    flash('Input in deposit is not a number')
                else:
                    User.incr_bank_info(uid,form.deposit.data)
            if form.withdraw.data is not '':
                if not form.withdraw.data.isnumeric():
                    flash('Input in withdraw is not a number')
                else:
                    balance = User.get_bank_info(uid)
                    if float(balance.strip('$').replace(',',''))-float(form.withdraw.data) >= 0:
                        User.decr_bank_info(uid,form.withdraw.data)
                    else:
                        flash('You do not have the funds LOL')
            return redirect(url_for('users.update_bank',uid=uid))
        return render_template('update_bank.html', form=form)

# this function displays the user's name, address, email, and a button to update them
@bp.route('/profile/<int:uid>')
def get_profile(uid):
    if current_user.is_authenticated:
        name, address, email = User.get_profile(uid)
        seller = User.seller_bool(uid)
        return render_template('profile.html',name=name,address=address,email=email,seller=seller)
    else:
        return render_template('profile.html',name=None,address=None,email=None,seller=None)
        
# this function displays the flask form updating name, address, email, and password
@bp.route('/update_info/<int:uid>', methods=['GET','POST'])
def update_info(uid):
    if current_user.is_authenticated:
        form = UpdateInfoForm()
        if form.validate_on_submit():
            if form.updatename.data is not '':
                if len(form.updatename.data.strip().split(' ')) < 6:
                    User.update_name(uid,form.updatename.data)
                else:
                    flash('Name has a lot of words, is this a SQL attack?')
            if form.updateaddress.data is not '':
                if len(form.updateaddress.data.strip().split(' ')) < 5:
                    User.update_address(uid,form.updateaddress.data)
                else:
                    flash('Address has a lot of words, is this a SQL attack?')
            if form.updatepassword.data is not '':
                if len(form.updatepassword.data.strip().split(' ')) < 2:
                    User.update_password(uid,form.updatepassword.data)
                else:
                    flash('Invalid password format')
            if form.updateemail.data is not '':
                if User.email_exists(form.updateemail.data):
                    flash('That email is already taken')
                else:
                    if form.updateemail.data.count('@')==1 and len(form.updateemail.data.strip().split(' ')) < 2:
                        User.update_email(uid,form.updateemail.data)
                    else:
                        flash('Invalid email format')
            if form.updateseller.data:
                if User.seller_bool(uid):
                    flash('You are already a seller')
                else:
                    User.become_seller(uid)
            return redirect(url_for('users.update_info',uid=uid))
        return render_template('update_info.html', form=form)

# logs out current user
@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index.index'))

# gets recent feedback for given user
@bp.route('/user_feedback', methods=['GET', 'POST'])
def user_feedback():
    if request.method == 'POST':
        user_id = current_user.id
        print(f"User ID: {user_id}")  # for debugging
        recent_feedback = Feedback.get_recent_feedback_for_user(user_id, limit=5)
        print(f"Recent Feedback: {recent_feedback}")  # for debugging

        return render_template('user_feedback.html', title='My Recent Feedback', recent_feedback=recent_feedback)

    return render_template('user_feedback.html', title='My Recent Feedback')