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

# Current Time of day in UTC
timestamp_string = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
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

    # This needs work to decide exactly what to do and how long to do it
    if is_user_home():
        desiredCool = homeCool
        desiredHeat = homeHeat
    else:
        desiredHeat = awayCool
        desiredHeat = awayHeat

    if (outsideTemp > desiredCool) and (insideTemp > desiredCool):
        decision = 'Turn AC On'
    elif (outsideTemp < desiredHeat) and (insideTemp < desiredHeat):
        decision = 'Turn Heat On'
    else:
        decision = 'Turn unit off'

    my_data = {"status": decision}
    # Publish decision to broker

    # Update this based on the Laptop information
    client.publishEvent("Laptop", "e4b3187eb170", "hvac", "json", my_data)

# Default route for display of data
@app.route('/')
def temp_Controller():

    return render_template('index.html', status=decision, timestamp=timestamp_string)


# Subscribe to motion and temp events
client.subscribeToDeviceEvents(event="motion")
client.deviceEventCallback = decide

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(port))


