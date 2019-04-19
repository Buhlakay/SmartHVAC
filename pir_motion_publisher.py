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
count = 0
motionCount = 0
moved = False
lastTemp

def set_location(data):
    global location
    payload = json.loads(data.payload.encode("utf-8"))
    print(payload)
    zip = payload['zip']
    location = search.by_zipcode(zip);

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
client.subscribeToDeviceEvents(event="zipcode")
client.deviceEventCallback = set_location

latitude = location.to_dict()['lat']
longitude = location.to_dict()['lng']
r = requests.get(URL + str(latitude) + "," + str(longitude))
data = r.json()
lastTemp = data['currently']['temperature']
print(lastTemp)
while 1:
    latitude = location.to_dict()['lat']
    longitude = location.to_dict()['lng']
    if count == 60:
        r = requests.get(URL + str(latitude) + "," + str(longitude))
        data = r.json()
        lastTemp = data['currently']['temperature']
        print(lastTemp)
        count = 0
    motion = "0"
    if(GPIO.input(PIRPin) != 0):
        print("motion detected")
        moved = True
        motionCount = 0
    else:
        print("no motion")
        motionCount += 1
        if motionCount == 60:
            moved = False
    if moved:
        motion = "1"
    else:
        motion = "0"
        
    myData = {'movement' : motion, 'temperature' : lastTemp}
    client.publishEvent("RaspberryPi","b827ebe4ecec","sensorData","json",myData)
    count += 1
    time.sleep(1)

