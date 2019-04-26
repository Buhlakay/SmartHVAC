Prior to running pir_motion_publisher.py:
- Raspberry Pi is connected to the internet on the same network as the other devices.
- You can ssh into Raspberry Pi(must be enabled on Raspberry Pi, must have the local IP of the device).
- pir_motion_publisher.py is on Raspberry Pi.
- PIR Motion Sensor is connected to the Raspberry Pi GPIO pins as specified in the Raspberry Pi schematics diagram.
- All dependencies listed in the file must be installed with the pip3 command. 
- The apikey variable must be replaced with your personal Dark Sky API key. 
- Device id in the options dictionary must be replaced with the wlan0 mac address of your Raspberry Pi.

To run pir_motion_publisher.py:
- ssh into Raspberry Pi
- Navigate to the folder containing pir_motion_publisher.py
- Type 'python3 pir_motion_publisher.py'
- pir_motion_publisher.py should now be reading motion sensor values and retrieving temperature information from the Dark Sky API. 

To exit the program:
- Press CTRL+C to exit the program

Results:
- The Raspberry Pi will sample values from the PIR motion sensor.
- The program will publish movement information (based on whether movement has been detected within the last 30 seconds) as well as 
the temperature of the specified zip code to the MQTT broker on the sensorData topic.
- Temperature sent in degrees Fahrenheit, motion sensor values are 0 or 1, where a 0 is no presence and 1 is present. 
