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
