from flask_wtf import FlaskForm
# from flask_wtf.file import FileField, FileAllowed
# from flask_login import current_user
from wtforms import StringField, PasswordField, SubmitField, BooleanField, IntegerField, validators, SelectMultipleField, widgets, TimeField
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

# class PreferenceForm(FlaskForm):
#     temperature_preference = StringField('Temperature Preference', 
#                                          validators=[DataRequired()])
#     lighting_preference = StringField('Lighting Preference',
#                                       validators=[DataRequired()])
#     tv_watchtime = StringField('Television Watchtime', 
#                                          validators=[DataRequired()])
#     humidity_levels = StringField('Humidity Levels',
#                                       validators=[DataRequired()])
#     appliance_preference = StringField('Appliance usage time', 
#                                          validators=[DataRequired()])
#     sleep_time = StringField('Preferred time of sleep',
#                                       validators=[DataRequired()])
#     occupancy_preference = StringField('When are you at home',
#                                       validators=[DataRequired()])
#     # Add more preference fields as needed
#     submit = SubmitField('Save Preferences')


# Custom widget to allow entering custom time range
class CustomTimeRangeWidget(widgets.ListWidget):
    def __call__(self, field, **kwargs):
        if not field.data:
            field.data = []
        return super().__call__(field, **kwargs)

class TimeRangeField(SelectMultipleField):
    widget = CustomTimeRangeWidget()

class PreferenceForm(FlaskForm):
    APPLIANCE_TIME_RANGES = [
        ('08:00-10:00', '08:00 AM - 10:00 AM'),
        ('12:00-14:00', '12:00 PM - 02:00 PM'),
        ('18:00-20:00', '06:00 PM - 08:00 PM')
    ]

    SLEEP_TIME_RANGES = [
        ('22:00-06:00', '10:00 PM - 06:00 AM'),
        ('23:00-07:00', '11:00 PM - 07:00 AM'),
    ]

    temperature_preference = IntegerField('Temperature Preference', 
                                          validators=[DataRequired()])
    lighting_preference = TimeRangeField('Lighting Preference', 
                                         choices=APPLIANCE_TIME_RANGES, coerce=str)
    tv_watchtime = TimeRangeField('Television Watchtime', 
                                  choices=APPLIANCE_TIME_RANGES, coerce=str)
    humidity_levels = IntegerField('Humidity Levels', validators=[DataRequired()])
    appliance_preference = TimeRangeField('Appliance usage time', 
                                          choices=APPLIANCE_TIME_RANGES, coerce=str)
    sleep_time = TimeRangeField('Preferred time of sleep', 
                                choices=SLEEP_TIME_RANGES, coerce=str)
    occupancy_preference = TimeRangeField('When are you at home', 
                                          choices=APPLIANCE_TIME_RANGES, coerce=str)
    
    custom_lighting_preference = StringField('Custom Lighting Preference')
    custom_tv_watchtime = StringField('Custom Television Watchtime')
    custom_appliance_preference = StringField('Custom Appliance usage time')
    custom_sleep_time = StringField('Custom Preferred time of sleep')
    custom_occupancy_preference = StringField('Custom When are you at home')

    submit = SubmitField('Save Preferences')
