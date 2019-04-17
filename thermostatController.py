'''
Controls the Thermostat based on outside temperature, inside temperature, user's schedule and detection of movement
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


# Is user home according to schedule
scheduledHome = False
# Movement detected
movement = False
# Outside temperature
outsideTemp = 0
# Inside temperature
insideTemp = 0
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
        "id": "6",
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
    # Determine if event
    if event.eventId == 'motion':
        global movement
        movement = event.data
    if event.eventId == 'temp':
        global insideTemp
        insideTemp = event.data


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
        desiredHeat = awayCool
        desiredHeat = awayHeat

    if (outsideTemp > desiredCool) and (insideTemp > desiredCool):
        decision = 'Turn AC On'
        hvac_decision_list[counter % LIST_SAMPLE_SIZE] = DECISION_AC_ON
    elif (outsideTemp < desiredHeat) and (insideTemp < desiredHeat):
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
client.subscribeToDeviceEvents(event="motion")
client.deviceEventCallback = decide

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(port))


