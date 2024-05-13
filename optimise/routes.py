from datetime import datetime, timedelta, time
from flask import render_template, url_for, redirect, flash, request, jsonify, abort, session
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from optimise import app, db, bcrypt
from optimise.forms import RegistrationForm, LoginForm, changeExpenseBudget, PreferenceForm
from optimise.models import User, Stats, Preference
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

    
    # Consumption
    today_date = (datetime.today().date()).strftime('%Y-%m-%d')
    yesterday_date = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')

    consumption_ph_today = average_energy_per_hour(today_date)
    consumption_ph_yesterday = average_energy_per_hour(yesterday_date)

    if abs(consumption_ph_yesterday - consumption_ph_today) <= 5: 
        first_insight = 'Vola, you are keeping track of your consumption'
    if abs(consumption_ph_yesterday - consumption_ph_today) > 5: 
        first_insight = 'Be careful!!!, you are consuming more than yesterday'


    tips = recommendationz()
    print(tips)

    # Actual energy
    hourly_consumptions_actual = average_energy_per_hour_all()
    cumulative_hourly_expenses = cumulative_hourly_costs(hourly_consumptions_actual, cost_per_watt_hour)
    latest_hour_actual, latest_cost_actual = cumulative_hourly_expenses[-1]

    # Predicted energy
    hourly_consumptions_predicted = average_energy_per_hour_all_predict()
    cumulative_hourly_expenses_predict = cumulative_hourly_costs(hourly_consumptions_predicted, cost_per_watt_hour)
    latest_hour_predict, latest_cost_predict = cumulative_hourly_expenses_predict[-1]


    month_predict = round(latest_cost_predict, 2)
    currentMonth_expense = round(latest_cost_actual, 2)
    savings = round((budget - currentMonth_expense), 2)
    expense_form = changeExpenseBudget()
    if expense_form.validate_on_submit():
        current_user.budget = expense_form.expense_budget.data
        db.session.commit()
        flash(f'Expense Budget updated successfully!', 'success')
        return redirect(url_for('home'))
    return render_template('home.html', title='Action Center', expense_form=expense_form, first_insight=first_insight,
                            first_name=first_name, budget=budget, month_predict=month_predict, 
                            currentMonth_expense=currentMonth_expense, savings=savings, tips=tips)

@app.route("/profile", methods=['GET', 'POST'])
@login_required
def profile():
    temp = (Preference.query.filter_by(user_id=current_user.id, preference_name='Temperature').first()).preference_value1
    lighting = (Preference.query.filter_by(user_id=current_user.id, preference_name='Lighting').first()).preference_value1
    tvWatchtime = (Preference.query.filter_by(user_id=current_user.id, preference_name='TV Watchtime').first()).preference_value1
    humidity = (Preference.query.filter_by(user_id=current_user.id, preference_name='Humidity Levels').first()).preference_value1
    appliance = (Preference.query.filter_by(user_id=current_user.id, preference_name='Appliance Usage Time').first()).preference_value1
    sleepTime = (Preference.query.filter_by(user_id=current_user.id, preference_name='Sleep Time').first()).preference_value1
    occupancy = (Preference.query.filter_by(user_id=current_user.id, preference_name='Occupancy').first()).preference_value1
    print(temp)
    pform = PreferenceForm()
    if pform.validate_on_submit():
        # Get data from the form
        user_id = current_user.id  # Assuming you are using Flask-Login
        temperature_preference = pform.temperature_preference.data
        lighting_preference = pform.lighting_preference.data
        tv_watchtime = pform.tv_watchtime.data
        humidity_levels = pform.humidity_levels.data
        appliance_preference = pform.appliance_preference.data
        sleep_time = pform.sleep_time.data
        occupancy_preference = pform.occupancy_preference.data
        
        # Check if preferences already exist for the user
        existing_preferences = Preference.query.filter_by(user_id=user_id).all()
        existing_preference_names = {preference.preference_name for preference in existing_preferences}
        
        # Update or add preferences
        preferences_to_add = []
        for preference_name, preference_value in [
            ('Temperature', str(temperature_preference)),
            ('Lighting', lighting_preference),
            ('TV Watchtime', tv_watchtime),
            ('Humidity Levels', str(humidity_levels)),
            ('Appliance Usage Time', appliance_preference),
            ('Sleep Time', sleep_time),
            ('Occupancy', occupancy_preference)
        ]:
            preference = next((pref for pref in existing_preferences if pref.preference_name == preference_name), None)
            if preference:
                # Update existing preference
                preference.preference_value1 = preference_value
            else:
                # Add new preference
                preference = Preference(
                    user_id=user_id,
                    preference_name=preference_name,
                    preference_value1=preference_value
                )
                preferences_to_add.append(preference)
        
        try:
            db.session.add_all(preferences_to_add)
            db.session.commit()
            flash('Preferences saved successfully.', 'success')
        except IntegrityError:
            db.session.rollback()
            flash('An error occurred while saving preferences.', 'error')

        flash(f'Preferences set successfully!', 'success')
        return redirect(url_for('profile'))
    return render_template('profile.html', title='Profile', pform=pform, temp=temp, humid=humidity,
                           light=lighting, tv=tvWatchtime, appliance=appliance, sleep=sleepTime, occupancy=occupancy)

# Actual
def average_energy_per_hour_all():
    hourly_consumptions = db.session.query(
        func.strftime('%Y-%m-%d %H:00:00', Stats.date).label('hour_truncated'),
        func.avg(Stats.energy).label('average_energy')
    ).group_by(
        func.strftime('%Y-%m-%d %H:00:00', Stats.date)
    ).all()
    return hourly_consumptions

# Predict
def average_energy_per_hour_all_predict():
    hourly_consumptions = db.session.query(
        func.strftime('%Y-%m-%d %H:00:00', Stats.date).label('hour_truncated'),
        func.avg(Stats.energy_prediction).label('average_energy')
    ).group_by(
        func.strftime('%Y-%m-%d %H:00:00', Stats.date)
    ).all()
    return hourly_consumptions

def cumulative_hourly_costs(hourly_consumptions, cost_per_watt_hour):
    cumulative_costs = []
    cumulative_energy = 0

    for hour, value in hourly_consumptions:
        cumulative_energy += value
        cumulative_cost = cumulative_energy * cost_per_watt_hour
        cumulative_costs.append((hour, cumulative_cost))

    return cumulative_costs



def average_energy_per_hour(target_date):
    hourly_consumptions = db.session.query(
        func.strftime('%Y-%m-%d %H:00:00', Stats.date).label('hour_truncated'),
        func.avg(Stats.energy).label('average_energy')
    ).filter(
        func.date(Stats.date) == target_date
    ).group_by(
        func.strftime('%Y-%m-%d %H:00:00', Stats.date)
    ).all()
    
    average_eph = overall_power_consumption(hourly_consumptions)
    return average_eph

def overall_power_consumption(hourly_consumptions):
    total_consumption = sum(consumption for hour, consumption in hourly_consumptions)
    return total_consumption


def calculate_energy_savings_with_natural_ventilation(temperature_inside, temperature_outside, airflow_rate):
    """
    Calculate potential energy savings from natural ventilation.

    Args:
    - temperature_inside: Temperature inside the building (in Celsius)
    - temperature_outside: Temperature outside the building (in Celsius)
    - airflow_rate: Airflow rate through the building (in cubic meters per hour)

    Returns:
    - energy_savings: Potential energy savings from natural ventilation (in kWh)
    """

    # Temperature difference between inside and outside
    temperature_difference = temperature_inside - temperature_outside
    
    # Assume specific heat capacity of air (in J/kg°C)
    specific_heat_capacity_air = 1005  # J/kg°C
    
    # Density of air at standard conditions (in kg/m^3)
    air_density = 1.225  # kg/m^3

    # Calculate energy savings using the formula: Q = m * c * ΔT
    # Where Q is the energy saved (in Joules), m is the mass flow rate of air (in kg/s),
    # c is the specific heat capacity of air (in J/kg°C), and ΔT is the temperature difference (in °C)
    
    # Convert airflow rate from cubic meters per hour to cubic meters per second
    airflow_rate_per_second = airflow_rate / 3600  # 1 hour = 3600 seconds

    # Calculate mass flow rate of air (in kg/s)
    mass_flow_rate = airflow_rate_per_second * air_density
    
    # Calculate energy savings (in Joules)
    energy_saved = mass_flow_rate * specific_heat_capacity_air * temperature_difference
    
    # Convert energy savings from Joules to kilowatt-hours (kWh)
    energy_savings_kWh = energy_saved / 3600000  # 1 kWh = 3.6 × 10^6 Joules
    
    return energy_savings_kWh


def recommendations_tips():
    tips = ["test1", "test2"]

    # Temperature preference
    preference_temperature = Preference.query.filter_by(user_id=current_user.id, preference_name='temperature').first()

    if preference_temperature:
        temperature_threshold = float(preference_temperature.preference_value1)  # Convert to float
        stats_temp = Stats.query.filter_by(user_id=current_user.id).order_by(Stats.date.desc()).first()
        
        if stats_temp:
            current_temperature = stats_temp.temperature
            diff = abs(current_temperature - temperature_threshold)

            if diff <= 3:
                now = datetime.now().time()
                day_start_time = time(10, 0)  # 10:00 AM
                day_end_time = time(17, 0)    # 5:00 PM
                if day_start_time <= now <= day_end_time:
                    airflow_rate = 6 * 1000  # Convert to meters per hour
                    energy_savings = calculate_energy_savings_with_natural_ventilation(current_temperature, 26, airflow_rate)
                    tips.append(f"Consider using natural ventilation. It would save you around {energy_savings:.2f} kWh.")


    # Temperature
    preference_temperature = Preference.query.filter_by(user_id=current_user.id, preference_name='temperature').first()

    if preference_temperature:
        temperature_threshold = preference_temperature.preference_value1
        stats_records = Stats.query.filter_by(user_id=current_user.id).order_by(Stats.date).all()
        
        duration_in_range = timedelta()  # Initialize duration counter to zero
        prev_record = None
        
        for record in stats_records:
            if prev_record is not None and abs(record.temperature - temperature_threshold) <= 3:
                # Calculate duration when temperature stays in range
                duration_in_range += record.date - prev_record.date
            prev_record = record
        
        # Convert duration to hours and minutes
        hours = duration_in_range.seconds // 3600
        minutes = (duration_in_range.seconds % 3600) // 60
        tips.append("Temperature stays in range for: {hours} hours and {minutes} minutes \nYou may consider using natural ventilation during day")


    # Tv watch time
    preference_tvwatchtime = Preference.query.filter_by(user_id=current_user.id, preference_name='tv-watchtime').first()

    if preference_tvwatchtime:
        min_hour_threshold_string = preference_tvwatchtime.preference_value1
        max_hour_threshold_string = preference_tvwatchtime.preference_value2 

        min_hour, min_minute = map(int, min_hour_threshold_string.split(':'))
        max_hour, max_minute = map(int, max_hour_threshold_string.split(':'))

        sum_of_statsL = db.session.query(db.func.sum(Stats.value)).filter(
            Stats.user_id == current_user.id,
            Stats.light == True,
            db.extract('hour', Stats.datetime) >= min_hour,
            db.extract('minute', Stats.datetime) >= min_minute,
            db.extract('hour', Stats.datetime) <= max_hour,
            db.extract('minute', Stats.datetime) <= max_minute
        ).scalar()

        if sum_of_statsL > 60:
            tips.append("Television is stays on beyond set watch time")

    # Occupancy
    preference_occupancy = Preference.query.filter_by(user_id=current_user.id, preference_name='occupancy').first()

    if preference_occupancy:
        min_hour_threshold_string = preference_occupancy.preference_value1
        max_hour_threshold_string = preference_occupancy.preference_value2 

        min_hour, min_minute = map(int, min_hour_threshold_string.split(':'))
        max_hour, max_minute = map(int, max_hour_threshold_string.split(':'))

        sum_of_statsL = db.session.query(db.func.sum(Stats.value)).filter(
            Stats.user_id == current_user.id,
            Stats.light == True,
            db.extract('hour', Stats.datetime) >= min_hour,
            db.extract('minute', Stats.datetime) >= min_minute,
            db.extract('hour', Stats.datetime) <= max_hour,
            db.extract('minute', Stats.datetime) <= max_minute
        ).scalar()

        sum_of_statsLM = db.session.query(db.func.sum(Stats.value)).filter(
            Stats.user_id == current_user.id,
            Stats.light == True,
            Stats.motion == True,
            db.extract('hour', Stats.datetime) >= min_hour,
            db.extract('minute', Stats.datetime) >= min_minute,
            db.extract('hour', Stats.datetime) <= max_hour,
            db.extract('minute', Stats.datetime) <= max_minute
        ).scalar()

        if sum_of_statsL > 60:
            tips.append("Lights are unnecessarily ON when away")

        if sum_of_statsLM > 60:
            tips.append("Late night activity during sleeping hours highten power consumption")

    # Sleeptime preference
    preference_sleep = Preference.query.filter_by(user_id=current_user.id, preference_name='sleeptime').first()

    if preference_sleep:
        min_hour_threshold_string = preference_sleep.preference_value1
        max_hour_threshold_string = preference_sleep.preference_value2 

        min_hour, min_minute = map(int, min_hour_threshold_string.split(':'))
        max_hour, max_minute = map(int, max_hour_threshold_string.split(':'))

        sum_of_statsL = db.session.query(db.func.sum(Stats.value)).filter(
            Stats.user_id == current_user.id,
            Stats.light == True,
            db.extract('hour', Stats.datetime) >= min_hour,
            db.extract('minute', Stats.datetime) >= min_minute,
            db.extract('hour', Stats.datetime) <= max_hour,
            db.extract('minute', Stats.datetime) <= max_minute
        ).scalar()

        sum_of_statsLM = db.session.query(db.func.sum(Stats.value)).filter(
            Stats.user_id == current_user.id,
            Stats.light == True,
            Stats.motion == True,
            db.extract('hour', Stats.datetime) >= min_hour,
            db.extract('minute', Stats.datetime) >= min_minute,
            db.extract('hour', Stats.datetime) <= max_hour,
            db.extract('minute', Stats.datetime) <= max_minute
        ).scalar()

        if sum_of_statsL > 60:
            tips.append("Lights are unnecessarily ON during sleep hours")

        if sum_of_statsLM > 60:
            tips.append("Late night activity during sleeping hours highten power consumption")

    # Day's consumption
    today_date = (datetime.today().date()).strftime('%Y-%m-%d') 
    consumptionToday = average_energy_per_hour(today_date)

    if consumptionToday > 22:
        # Consider sum target expense math
        tips.append("Consider lowering your thermostat by 1-2 degrees to save energy on heating.")


    # if user_data['appliances']:
    #     high_energy_appliances = [app for app in user_data['appliances'] if app['energy_usage'] > 100]
    #     if high_energy_appliances:
    #         tips.append("Try to limit usage of high-energy appliances such as your {}.".format(', '.join([app['name'] for app in high_energy_appliances])))
        
    return tips


def recommendationz():
    tips = ["Loading.."]


    # Occupancy
    preference_occupancy = Preference.query.filter_by(user_id=current_user.id, preference_name="Occupancy").first()
    
    if preference_occupancy:
        occupancy = preference_occupancy.preference_value1
        occupancy_start, occupancy_end = map(str, occupancy.split('-'))

        occupancy_start_hour, occupancy_start_minute = map(int, occupancy_start.split(':'))
        occupancy_end_hour, occupancy_end_minute = map(int, occupancy_end.split(':'))

        sum_of_statsL = db.session.query(db.func.count()).filter(
            Stats.user_id == current_user.id,
            Stats.light == True,
            db.extract('hour', Stats.date) < occupancy_start_hour,
            db.extract('hour', Stats.date) > occupancy_end_hour
        ).scalar()

        if sum_of_statsL > 60:
            tips.append("Turn off the lights when away")

        stat = db.session.query(db.func.count()).filter(
            Stats.user_id == current_user.id,
            Stats.energy >= 12,
            db.extract('hour', Stats.date) >= occupancy_start_hour,
            db.extract('hour', Stats.date) <= occupancy_end_hour
        ).scalar()
        
        if stat > 4:
            tips.append("Appliances should be turned off when away")

    # tv Watchtime
    preference_tvwatchtime = Preference.query.filter_by(user_id=current_user.id, preference_name='TV Watchtime').first()

    if preference_tvwatchtime:
        tvWatchtime = preference_tvwatchtime.preference_value1
        tvWatchtime_start, tvWatchtime_end = map(str, tvWatchtime.split('-'))

        tvWatchtime_start_hour, tvWatchtime_start_minute = map(int, tvWatchtime_start.split(':'))
        tvWatchtime_end_hour, tvWatchtime_end_minute = map(int, tvWatchtime_end.split(':'))

        sum_of_statsL = db.session.query(db.func.count()).filter(
            Stats.user_id == current_user.id,
            Stats.light == True,
            db.extract('hour', Stats.date) < tvWatchtime_start_hour,
            db.extract('hour', Stats.date) > tvWatchtime_end_hour
        ).scalar()

        if sum_of_statsL > 60:
            tips.append("Television is stays on beyond set watch time")

    # Sleeptime
    preference_sleep = Preference.query.filter_by(user_id=current_user.id, preference_name='Sleep Time').first()
    if preference_sleep:
        sleep_time = preference_sleep.preference_value1
        sleep_start, sleep_end = map(str, sleep_time.split('-'))

        sleep_start_hour, sleep_start_minute = map(int, sleep_start.split(':'))
        sleep_end_hour, sleep_end_minute = map(int, sleep_end.split(':'))

        # Check lights during sleep time
        sum_of_lightChecks = db.session.query(db.func.count()).filter(
            Stats.user_id == current_user.id,
            Stats.light == True,
            db.extract('hour', Stats.date) >= sleep_start_hour,
            db.extract('hour', Stats.date) <= sleep_end_hour
        ).scalar()

        # Check late night activity
        sum_of_statsLM = db.session.query(db.func.count()).filter(
            Stats.user_id == current_user.id,
            Stats.light == True,
            Stats.motion == True,
            db.extract('hour', Stats.date) >= sleep_start_hour,
            db.extract('hour', Stats.date) <= sleep_end_hour
        ).scalar()

        if sum_of_lightChecks > 60:
            tips.append("Lights are unnecessarily ON during sleep hours")

        if sum_of_statsLM > 80:
            tips.append("Late night activity during sleeping hours highten power consumption")
    
    # Temperature
    preference_temperature = Preference.query.filter_by(user_id=current_user.id, preference_name='Temperature').first()

    if preference_temperature:
        temp = int(preference_temperature.preference_value1)
        stat = Stats.query.filter_by(user_id=current_user.id).order_by(Stats.date.desc()).first()

        # Calculate the timestamp 60 minutes (1 hour) ago
        time_ago = datetime.now() - timedelta(hours=3)

        # Query to get the average temperature record in the last 60 minutes (1 hour)
        average_temperature_time_ago = Stats.query \
            .filter(Stats.user_id == current_user.id) \
            .filter(Stats.date >= time_ago) \
            .with_entities(func.avg(Stats.temperature)) \
            .scalar()
        if average_temperature_time_ago is None:
            average_temperature_time_ago = 0
        if abs(average_temperature_time_ago - temp) > 3:
            tips.append("Schedule your AC")

        # Get the current time
        current_time = datetime.now().time()

        # Define daytime range (for example, from 6 AM to 6 PM)
        daytime_start = datetime.strptime('09:00:00', '%H:%M:%S').time()
        daytime_end = datetime.strptime('17:00:00', '%H:%M:%S').time()

        # Check if current time is within the daytime range
        if daytime_start <= current_time <= daytime_end:
            # print("It's daytime!")
            if temp - average_temperature_time_ago > 3:
                tips.append(f'You may use Natural ventilation between {daytime_start} and {daytime_end} hours')
        
            


    
    return tips


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

# Energy Trends
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

    return jsonify({
        'average_energy_yesterday': average_energy_yesterday,
        'average_energy_today': average_energy_today
    })

# Assuming the cost per Watt-hour is UGX 250
cost_per_watt_hour = 250

@app.route('/track_energy_cost', methods=['GET'])
@login_required
def track_energy_cost():

    hourly_consumptions = average_energy_per_hour_all()
    cumulative_hourly_expenses = cumulative_hourly_costs(hourly_consumptions, cost_per_watt_hour)

    target_expense = current_user.budget # Set value by user from User model

    data = {
        'target_expense': target_expense,
        'cumulative_hourly_costs': cumulative_hourly_expenses
    }
    return jsonify(data)




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
        hashed_password = bcrypt.generate_password_hash(form.password.data)
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
            session.clear()
            session['user_id'] = user.id  
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('loginPage.html', title='Login', form=form)

@app.route("/logout")
def logout():
    session.clear()
    logout_user()
    return redirect(url_for('base'))