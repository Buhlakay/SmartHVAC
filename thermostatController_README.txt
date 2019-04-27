Prior to running thermostatController:
- All dependencies listed in the file must be installed with the pip3 command. 
- The apikey variable must be replaced with your personal Dark Sky API key. 
- Device id in the options dictionary must be replaced with the wlan0 mac address of your Raspberry Pi.

To run thermostatController.py:
- Type 'python3 pir_motion_publisher.py'
- Navigate to localhost, port 5000 (or whatever you have changed the desired port number for Flask)
- Enter desired ZIP code and desired home/away heat and cool threshold values (if wanted)

To exit the program:
- Press CTRL+Z to exit the program
- NOTE: For Linux environments, the Flask application may stay running after termination in some cases. To deal with this:
    - Type 'lsof :5000' (or whichever port number you are using)
    - Find the process id's of the persisting processes on the desired port number
    - Kill the processes using 'kill -9 <PID>'

Results:
- Graph should be displayed with all of the user preferences displayed on the screen
- User can go back and change their preferences at any time
