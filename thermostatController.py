'''
Controls the Thermostat based on outside temperature, user's schedule and detection of movement
'''
import time
# IBM cloud connection
import ibmiotf.application
import os, json
from flask import Flask, redirect
from flask import render_template
from flask import request
from datetime import datetime
# from get_calendar import *
import get_calendar as calendar
import threading

DECISION_HEAT_ON = "rgba(255,102,102,0.5)"
DECISION_AC_ON = "rgba(102,102,255,0.5)"
DECISION_TURN_OFF = "rgba(192,192,192,0.5)"

running = False

LIST_SAMPLE_SIZE = 60

outside_temp_list = [0] * LIST_SAMPLE_SIZE
# outside_temp_list = [78, 76, 67, 58, 87]

hvac_decision_list = [0] * LIST_SAMPLE_SIZE
# hvac_decision_list = [DECISION_AC_ON, DECISION_TURN_OFF, DECISION_HEAT_ON, DECISION_HEAT_ON]

timestamp_list = [0] * LIST_SAMPLE_SIZE
# timestamp_list = [datetime.now().strftime('%Y-%m-%d %H:%M:%S'), datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
#   datetime.now().strftime('%Y-%m-%d %H:%M:%S'), datetime.now().strftime('%Y-%m-%d %H:%M:%S'), datetime.now().strftime('%Y-%m-%d %H:%M:%S')]

hvac_counter = 0
temp_counter = 0

# Current Time of day in UTC
timestamp_string = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
# Is user home according to schedule
scheduledHome = False
# Movement detected
movement = False
# Outside temperature
outsideTemp = 0
# final decision if user is home
userHome = False
# Away Heat setting
awayHeat = 60
# Away Cool setting
awayCool = 80
# Home heat setting
homeHeat = 68
# Home Cool setting
homeCool = 75
# ZIP code
zipCode = 27607

# Decision on what to do with the HVAC system. 'Turn AC on', 'Turn Heat on'
decision = 'Turn unit off'


app = Flask(__name__)
port = os.getenv('VCAP_APP_PORT', '5000')

event_list = calendar.get_event_list()

# Connect to IBM cloud instance
client = None

# Connection data for IBM Cloud
try:
    options = {
        "org": "jbkg3j",
        "id": "8",
        "auth-method": "apikey",
        "auth-key": "a-jbkg3j-2fh4t6fddr",
        "auth-token": "LieV-Obn1G1Q97QU*A"
    }
    client = ibmiotf.application.Client(options)
    client.connect()


except ibmiotf.ConnectionException as e:
    print(e)

def update_lists(element_list, element, counter):
    if counter >= LIST_SAMPLE_SIZE:
        element_list.pop(0)
        element_list.append(element)
    else:
        element_list[counter] = element


# Determines if the user is home based on data from motion sensor and schedule
def is_user_home():
    global movement
    global userHome

    # Favor input from the motion sensor over the schedule to determine if they are home
    if movement:
        userHome = True
    elif scheduledHome:
        userHome = True
    else:
        userHome = False
    return userHome


# Callback for a sensor value change
def event_callback(data):

    # New Data has been published
    payload = json.loads(data.payload)
    global movement
    global outsideTemp
    global temp_counter
    global scheduledHome

    movement = int(payload["movement"])
    print(movement)

    if float(payload["temperature"]) != outsideTemp:
        update_lists(outside_temp_list, outsideTemp, temp_counter)
        scheduledHome = not calendar.check_user_event(event_list, datetime.now())
        
        outsideTemp = float(payload["temperature"])
        decide()
        temp_counter += 1

   
# Decide whether to turn heat or AC on
def decide():
    desiredCool = 0
    desiredHeat = 0
    global decision
    global hvac_counter
    global hvac_decision_list
    global timestamp_list

    # This needs work to decide exactly what to do and how long to do it
    if is_user_home():
        desiredCool = homeCool
        desiredHeat = homeHeat
    else:
        desiredCool = awayCool
        desiredHeat = awayHeat

    if (outsideTemp > desiredCool):
        decision = 'Turn AC On'
        update_lists(hvac_decision_list, DECISION_AC_ON, hvac_counter)
    elif (outsideTemp < desiredHeat):
        decision = 'Turn Heat On'
        update_lists(hvac_decision_list, DECISION_HEAT_ON, hvac_counter)
    else:
        decision = 'Turn unit off'
        update_lists(hvac_decision_list, DECISION_TURN_OFF, hvac_counter)
  
    timestamp_string = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    update_lists(timestamp_list, timestamp_string, hvac_counter)

    hvac_counter += 1

    my_data = {"status": decision}
    # Publish decision to broker

    # Update this based on the Laptop information
    client.publishEvent("Laptop", "e4b3187eb170", "hvac", "json", my_data)

@app.route('/')
def show_writeup():
    return render_template('writeup.html')

# event = zipcode, key = zip
@app.route('/zip', methods=['GET', 'POST'])
def get_zip_code():
    global zipCode
    global running
    global awayHeat
    global homeHeat
    global awayCool
    global homeCool

    if request.method == 'POST':
        zipCode = request.form['zip'] if request.form['zip'] != '' else zipCode
        awayHeat = int(request.form['awayHeat']) if request.form['awayHeat'] != '' else awayHeat
        homeHeat = int(request.form['homeHeat']) if request.form['homeHeat'] != '' else homeHeat
        awayCool = int(request.form['awayCool']) if request.form['awayCool'] != '' else awayCool
        homeCool = int(request.form['homeCool']) if request.form['homeCool'] != '' else homeCool

        my_data = {'zip': str(zipCode)}
        client.publishEvent("Laptop", "7", "zipcode", "json", my_data)
        
        running = True
        return redirect('/graph')
    return render_template('zip.html')

# Default route for display of data
@app.route('/graph')
def temp_controller():
    global timestamp_list
    global hvac_decision_list
    global outside_temp_list

    if hvac_counter < LIST_SAMPLE_SIZE:
        # print(outside_temp_list)
        return render_template('graph.html', status=decision, labels=timestamp_list[0: hvac_counter], 
            title='Temperatures over Time', hvac_decisions=hvac_decision_list[0: hvac_counter],
            outside_values=outside_temp_list[0: hvac_counter], away_heat=awayHeat, home_heat=homeHeat,
            away_cool=awayCool, home_cool=homeCool, outside_temp=outsideTemp, current_decision=decision,
            zip_code=zipCode, currently_present=userHome)
    else:
        return render_template('graph.html', status=decision, labels=timestamp_list, 
            title='Temperatures over Time', hvac_decisions=hvac_decision_list,
            outside_values=outside_temp_list, away_heat=awayHeat, home_heat=homeHeat,
            away_cool=awayCool, home_cool=homeCool, outside_temp=outsideTemp, current_decision=decision,
            zip_code=zipCode, currently_present=userHome)


# Subscribe to motion and temp events
client.subscribeToDeviceEvents(event="sensorData")
client.deviceEventCallback = event_callback


def schedule_app_run():
    while True:
        if running:
            # Check the user's schedule every 15 minutes
            # Returns True if the user has something scheduled at this time
            print(scheduledHome)
            time.sleep(5)
    

if __name__ == "__main__":
    # threading.Thread(target=signal_event).start()
    # threading.Thread(target=schedule_app_run).start()
    app.run(host='0.0.0.0', port=int(port))
    
    
    