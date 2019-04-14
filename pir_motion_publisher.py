import RPi.GPIO as GPIO
import time
import ibmiotf.application
import requests
from uszipcode import SearchEngine

PIRPin = 17
apikey = "c26a9e4c2dd93646a896e2620f2855f0"
search = SearchEngine(simple_zipcode=True)
URL = "https://api.darksky.net/forecast/" + apikey + "/"
location = search.by_zipcode("27511");


def init():
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(PIRPin,GPIO.IN)

    try:
        options = {
                "org": "jbkg3j",
                "type": "RaspberryPi",
                "id": "b827ebe4ecec",
                "auth-method": "apikey",
                "auth-token": "LieV-Obn1G1Q97QU*A",
                "auth-key": "a-jbkg3j-2fh4t6fddr"
                }


        client = ibmiotf.application.Client(options)
        client.connect()
    except ibmiotf.ConnectionException as e:
        print(e)
 
 def set_location(data):
    global location
    payload = json.loads(data.payload)
    print(payload)
    zip = payload['zip']
    location = search.by_zipcode(zip);

init()
client.subscribeToDeviceEvents(event="zipcode")
client.deviceEventCallback = set_location
while 1:
    latitude = location.to_dict()['lat']
    longitude = location.to_dict()['lng']
    r = requests.get(URL + str(latitude) + "," + str(longitude))
    data = r.json()
    temp = data['currently']['temperature']
    motion = "0"
    if(GPIO.input(PIRPin) != 0):
        print("motion detected")
        motion = "1"
    else:
        print("no motion")
        motion = "0"
    myData = {'motion' : motion, 'temperature' : temp}
    client.publishEvent("RaspberryPi","b827ebe4ecec","sensorData","json",myData)
    time.sleep(5)
