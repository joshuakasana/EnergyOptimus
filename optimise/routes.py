from datetime import datetime, timedelta
from flask import render_template, url_for, redirect, flash, request, jsonify, abort
from sqlalchemy import func
from optimise import app, db, bcrypt
from optimise.forms import RegistrationForm, LoginForm, changeExpenseBudget, PreferenceForm
from optimise.models import User, Stats
from flask_login import login_user, current_user, logout_user, login_required

@app.route('/data', methods=['POST'])
def receive_data():
    print('Initiated')
    if not request.json:
        abort(400, 'Request body must be in JSON format')

    data = request.json
    required_fields = ['device_id', 'date', 'temperature', 'humidity', 'light', 'motion', 'current', 'energy', 'energy_prediction']
    for field in required_fields:
        if field not in data:
            abort(400, f'Missing required field: {field}')

    # Process and store the received data
            
    device_id = data.get('device_id')
    user = User.query.filter_by(device_id=device_id).first()

    if user:
        user_id = user.id
    else:
        abort(403, 'Unauthorized device')  # Or handle unauthorized device appropriately

    light_detected = bool(data.get('light_value'))
    motion_detected = bool(data.get('motion_value'))

    try:
        converted_datetime = datetime.fromisoformat(data['date'])
    except ValueError:
        abort(400, "Datetime error")


    save_data_to_database(data, user_id, light_detected, motion_detected, converted_datetime)
    return jsonify({'message': 'Data received and stored successfully'}), 200

def save_data_to_database(data, user_id, light, motion, converted_datetime):
    stat = Stats(user_id=user_id, device_id=data['device_id'], 
                 date=converted_datetime, temperature=data['temperature'], humidity=data['humidity'],
                 light=light, motion=motion, current=data['current'], energy=data['energy'],
                 energy_prediction=data['energy_prediction'])
    db.session.add(stat)
    db.session.commit()


@app.route("/")
# @app.route("/base")
# @app.route("/index")
def base():
    return render_template('index.html', title='Satient')



@app.route("/home", methods=['GET', 'POST'])
@login_required
def home():
    first_name = current_user.first_name
    budget = current_user.budget
    stats = Stats.query.all()
    

    month_predict = 13000
    currentMonth_expense = 7409.99
    savings = budget - currentMonth_expense
    expense_form = changeExpenseBudget()
    form = PreferenceForm()
    if expense_form.validate_on_submit():
        current_user.budget = expense_form.expense_budget.data
        db.session.commit()
        flash(f'Expense Budget updated successfully!', 'success')
        return redirect(url_for('home'))
    if form.validate_on_submit():
        flash(f'Preferences set successfully!', 'success')
        return redirect(url_for('home'))
    return render_template('home.html', title='Action Center', expense_form=expense_form, form=form,
                            first_name=first_name, budget=budget, month_predict=month_predict, 
                            currentMonth_expense=currentMonth_expense, savings=savings)

def average_energy_per_hour(target_date):
    average_eph = db.session.query(
        func.strftime('%Y-%m-%d %H:00:00', Stats.date).label('hour_truncated'),
        func.avg(Stats.energy).label('average_energy')
    ).filter(
        func.date(Stats.date) == target_date
    ).group_by(
        func.strftime('%Y-%m-%d %H:00:00', Stats.date)
    ).all()

@app.route('/get_current_data', methods=['GET'])
@login_required
def get_current_data():
    # Query the database for the latest temperature and humidity data
    stat = Stats.query.filter_by(user_id=current_user.id).order_by(Stats.date.desc()).first()

    if stat:
        temperature = stat.temperature
        humidity = stat.humidity
    else:
        # If no data is available, set default values
        temperature = 25
        humidity = 75

    # Return the current time, temperature, and humidity as JSON
    return jsonify({
        'temperature': temperature,
        'humidity': humidity
    })

@app.route('/get_energy_consumption', methods=['GET'])
@login_required
def get_energy_consumption():
    # Get the current datetime
    current_datetime = datetime.now()
    print(current_datetime)

    # Calculate the datetime for yesterday and today
    yesterday_datetime = current_datetime - timedelta(days=1)
    print(yesterday_datetime)

    # Extract date part from datetime objects
    current_date = current_datetime.date()
    yesterday_date = yesterday_datetime.date()

    # Calculate the start and end of yesterday
    yesterday_start = datetime.combine(yesterday_date, datetime.min.time())
    yesterday_end = datetime.combine(yesterday_date, datetime.max.time())

    # Calculate the start of today
    today_start = datetime.combine(current_date, datetime.min.time())
    today_end = datetime.combine(current_date, datetime.max.time())

    # Filter records for yesterday
    stats_yesterday = Stats.query.filter(
        Stats.user_id == current_user.id,
        Stats.date >= yesterday_start,
        Stats.date <= yesterday_end
    ).all()

    # Filter records for today
    stats_today = Stats.query.filter(
        Stats.user_id == current_user.id,
        Stats.date >= today_start,
        Stats.date <= today_end
    ).all()

    # Calculate total energy consumption for yesterday
    total_energy_yesterday = sum(stat.energy for stat in stats_yesterday) if stats_yesterday else 0

    # Calculate total energy consumption for today
    total_energy_today = sum(stat.energy for stat in stats_today) if stats_today else 0

    # Calculate the number of records for yesterday and today
    num_records_yesterday = len(stats_yesterday)
    num_records_today = len(stats_today)

    # Calculate the average energy consumption for yesterday and today
    average_energy_yesterday = round(total_energy_yesterday / num_records_yesterday, 2) if num_records_yesterday > 0 else 0
    average_energy_today = round(total_energy_today / num_records_today, 2) if num_records_today > 0 else 0
    print('1....',average_energy_today)
    print('2....',average_energy_yesterday)

    return jsonify({
        'average_energy_yesterday': average_energy_yesterday,
        'average_energy_today': average_energy_today
    })


@app.route('/get_energy_data', methods=['GET'])
@login_required
def get_energy_data():
    # Query the Stats table for energy and predicted energy data
    stats = Stats.query.filter_by(user_id=current_user.id).order_by(Stats.date).all()

    # Extract timestamps and energy values
    timestamps = [stat.date.strftime("%a %H:%M:%S") for stat in stats]
    energy_values = [stat.energy for stat in stats]
    predicted_energy_values = [stat.energy_prediction for stat in stats]

    # Prepare data to send back to the client
    data = {
        'timestamps': timestamps,
        'energy_values': energy_values,
        'predicted_energy_values': predicted_energy_values
    }

    return jsonify(data)



@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(last_name=form.last_name.data, first_name=form.first_name.data, username=form.username.data, email=form.email.data, device_id=form.device_id.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('login'))
    return render_template('registerPage.html', title='Register', form=form)



@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('loginPage.html', title='Login', form=form)

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('base'))