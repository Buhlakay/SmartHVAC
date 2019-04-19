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

DECISION_HEAT_ON = "rgba(255,102,102,0.5)"
DECISION_AC_ON = "rgba(102,102,255,0.5)"
DECISION_TURN_OFF = "rgba(192,192,192,0.5)"


LIST_SAMPLE_SIZE = 5
outside_temp_list = [78, 76, 67, 58, 87]
# hvac_decision_list = [0] * LIST_SAMPLE_SIZE
hvac_decision_list = [DECISION_AC_ON, DECISION_TURN_OFF, DECISION_HEAT_ON, DECISION_HEAT_ON]
timestamp_list = [datetime.now().strftime('%Y-%m-%d %H:%M:%S'), datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
    datetime.now().strftime('%Y-%m-%d %H:%M:%S'), datetime.now().strftime('%Y-%m-%d %H:%M:%S'), datetime.now().strftime('%Y-%m-%d %H:%M:%S')]

# Something mod 60 to make a circular queue of values for last 60 sampled values
counter = 0


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
# Home heat setting
homeHeat = 68
# Away Cool setting
awayCool = 80
# Home Cool setting
homeCool = 75

# Decision on what to do with the HVAC system. 'Turn AC on', 'Turn Heat on'
decision = ''


app = Flask(__name__)
port = os.getenv('VCAP_APP_PORT', '5000')


# Connect to IBM cloud instance
client = None


# Connection data for IBM Cloud
try:
    options = {
        "org": "jbkg3j",
        "id": "7",
        "auth-method": "apikey",
        "auth-key": "a-jbkg3j-2fh4t6fddr",
        "auth-token": "LieV-Obn1G1Q97QU*A"
    }
    client = ibmiotf.application.Client(options)
    client.connect()


except ibmiotf.ConnectionException as e:
    print(e)


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
def event_callback(event):
    # New Data has been published
    payload = json.loads(data.payload)
    global movement
    global outsideTemp

    movement = payload["movement"]
    outsideTemp = int(payload["temperature"])


# Decide whether to turn heat or AC on
def decide():
    desiredCool = 0
    desiredHeat = 0
    global decision
    global counter
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
        hvac_decision_list[counter % LIST_SAMPLE_SIZE] = DECISION_AC_ON
    elif (outsideTemp < desiredHeat):
        decision = 'Turn Heat On'
        hvac_decision_list[counter % LIST_SAMPLE_SIZE] = DECISION_HEAT_ON
    else:
        decision = 'Turn unit off'
        hvac_decision_list[counter % LIST_SAMPLE_SIZE] = DECISION_TURN_OFF
  
    timestamp_string = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    timestamp_list[counter % LIST_SAMPLE_SIZE] = timestamp_string

    counter += 1

    my_data = {"status": decision}
    # Publish decision to broker

    # Update this based on the Laptop information
    client.publishEvent("Laptop", "e4b3187eb170", "hvac", "json", my_data)


# Default route for display of data
@app.route('/')
def temp_controller():
    labels = [1, 2, 3, 4, 5]
    return render_template('index.html', status=decision, labels=timestamp_list, 
            title='Temperatures over Time', hvac_decisions=hvac_decision_list,
            outside_values=outside_temp_list)


# Subscribe to motion and temp events
client.subscribeToDeviceEvents(event="sensorData")
client.deviceEventCallback = decide

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(port))

    event_list = calendar.get_event_list()

    while True:
        # Check the user's schedule every 15 minutes
        # Returns True if the user has something scheduled at this time
        scheduledHome = calendar.check_user_event(event_list, datetime.now())
        decide()
        time.sleep(900)
