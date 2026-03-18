# Can configure these shell scripts to run to make sure you can comunicate to motor for testing only if using a XY-160D motor controller
powershell -ExecutionPolicy Bypass -File "C:\StreamDeck\Arduino\fwd.ps1"
powershell -ExecutionPolicy Bypass -File "C:\StreamDeck\Arduino\stop.ps1"
powershell -ExecutionPolicy Bypass -File "C:\StreamDeck\Arduino\rev.ps1"



Build Sheet
- Arudino Uno
- StreamDeck
- XY-160D H-bridge motor controller or BTS7960(highly recommended for this project) 43A update!!! code was modified to use the BTS7960 motor instead
- 5A Fuse 
- 24V 1.2A powersupply (for testing)
- Python (to run COM listener)
- Bitfocus Companion app (for coding http get requests to python flask listener)


Install software procedures
    - download arduino ide from https://www.arduino.cc/en/software/
    - use this to install the arduino_listner/arduino_listner.ino file onto your Arudino Uno

Board wiring,
    -   board = Arudino
        R_EN = 8;
        L_EN = 9;
        RPWM = 5;
        LPWM = 6;
        GND = GND on digital side
        B+ and B- to power supply( be sure to add a 5amp for safety use a meter to test for voltage from those 2 ends for sanity incase one of the boards are faulty)
        M+ and M- to motor or wires leading to motor


To operate this project simply connect arduino to pc and StreamDeck to pc, and start companion app
next run this script at startup 
    py C:\StreamDeck\Arduino\serial_bridge.py

you may need to delete serial_bridge.lock if it fails at startup no worries it wil create a new lock File
