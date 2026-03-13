# RM_streamdeck_controller
this repo is made to control remote mast mic boom through streamdeck

# Can configure these shell scripts to run to make sure you can comunicate to motor
powershell -ExecutionPolicy Bypass -File "C:\StreamDeck\Arduino\fwd.ps1"
powershell -ExecutionPolicy Bypass -File "C:\StreamDeck\Arduino\stop.ps1"
powershell -ExecutionPolicy Bypass -File "C:\StreamDeck\Arduino\rev.ps1"



Build Sheet
- Arudino Uno
- StreamDeck
- XY-160D H-bridge motor controller or BTS7960 43A
- 5A Fuse 
- 24V 1.2A powersupply (for testing)
- Python (to run COM listener)
- Bitfocus Companion app (for coding http get requests to python flask listener)


""" For Full operation 
1- use the arduino IDE to load the arduino_listener onto the arduino board (fully close arudino IDE for serial_bridge.py will not be able to run if another program is using the serial port to talk to the arduino board) then 
2- run the serial_bridge.py (this assumes ardunio is on COM3 in device manager) in your powershell at startup
3- through Companion app (bitfocus companion) use a simple Generic: http plugin (GET) for your streamdeck
4- to setup buttons set the http plugin Base URL to http://127.0.0.1:8787/
5- select HTTP Get when creating a button and set button URI to http://127.0.0.1:8787/fwd_down for on press and http://127.0.0.1:8787/fwd_up for release action 
6- Create a new button for motor reverse as well Press action uri would be http://127.0.0.1:8787/rev_down and release action would be http://127.0.0.1:8787/rev_up
7- open terminal and press buttons to ensure you are getting a 200-OK in the powershell


"""
