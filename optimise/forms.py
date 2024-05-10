from flask_wtf import FlaskForm
# from flask_wtf.file import FileField, FileAllowed
# from flask_login import current_user
from wtforms import StringField, PasswordField, SubmitField, BooleanField, IntegerField, validators, SelectField, DateTimeField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from optimise.models import User


class RegistrationForm(FlaskForm):
    last_name = StringField('Last Name',
                           validators=[DataRequired(), Length(min=2, max=20)])
    first_name = StringField('First Name',
                           validators=[DataRequired(), Length(min=2, max=20)])
    username = StringField('Username',
                           validators=[DataRequired(), Length(min=4, max=20)])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    device_id = StringField('House identifier',
                           validators=[DataRequired(), Length(min=4, max=20)])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('That username is taken. Please choose a different one.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('That email is taken. Please choose a different one.')
        
    def validate_device_id(self, device_id):
        user = User.query.filter_by(device_id=device_id.data).first()
        if user:
            raise ValidationError('That device id is already in use. Please choose a different one.')


class LoginForm(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Sign in')

class changeExpenseBudget(FlaskForm):
    expense_budget = IntegerField('Expense Budget', validators=[DataRequired()])
    submit = SubmitField('Submit')
class PreferenceForm(FlaskForm):
    APPLIANCE_TIME_RANGES = [
        (None, 'Choose...'),
        ('08:00-10:00', '08:00 AM - 10:00 AM'),
        ('12:00-14:00', '12:00 PM - 02:00 PM'),
        ('18:00-20:00', '06:00 PM - 08:00 PM')
    ]

    SLEEP_TIME_RANGES = [
        (None, 'Choose...'),
        
        ('21:00-05:00', '9:00 PM - 5:00 AM'),
        ('21:00-05:00', '9:00 PM - 5:00 AM'),
        ('22:00-06:00', '10:00 PM - 06:00 AM'),
        ('23:00-07:00', '11:00 PM - 07:00 AM')
    ]

    temperature_preference = IntegerField(u'Temperature Preference', validators=[DataRequired()])
    lighting_preference = SelectField(u'Lighting Preference', 
                                      choices=APPLIANCE_TIME_RANGES, coerce=str,
                                      validators=[DataRequired()])
    tv_watchtime = SelectField(u'Television Watchtime', 
                               choices=APPLIANCE_TIME_RANGES, coerce=str,
                               validators=[DataRequired()])
    humidity_levels = IntegerField(u'Humidity Levels', validators=[DataRequired()])
    appliance_preference = SelectField(u'Appliance usage time', 
                                       choices=APPLIANCE_TIME_RANGES, coerce=str,
                                       validators=[DataRequired()])
    sleep_time = SelectField(u'Preferred time of sleep', 
                             choices=SLEEP_TIME_RANGES, coerce=str,
                             validators=[DataRequired()])
    occupancy_preference = SelectField(u'When are you at home', 
                                       choices=APPLIANCE_TIME_RANGES, coerce=str,
                                       validators=[DataRequired(message="Please select an option")])

    submit = SubmitField('Save Preferences')

    def validate_lighting_preference(self, lighting_preference):
        if lighting_preference.data == "None":
            raise ValidationError('Please select an option other than "Choose..."')
    
    def validate_tv_watchtime(self, tv_watchtime):
        if tv_watchtime.data == "None":
            raise ValidationError('Please select an option other than "Choose..."')
    
    def validate_appliance_preference(self, appliance_preference):
        if appliance_preference.data == 'None':
            raise ValidationError('Please select an option other than "Choose..."')
    
    def validate_sleeptime(self, sleeptime):
        if sleeptime.data == 'None':
            raise ValidationError('Please select an option other than "Choose..."')

    def validate_occupancy_preference(self, occupancy_preference):
        if occupancy_preference.data == 'None':
            raise ValidationError('Please select an option other than "Choose..."')
