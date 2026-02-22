from flask import Flask, request
import serial, time, sys, os
import atexit
print("PID:", os.getpid())
# input("Press Enter to exit...")

PORT = r"\\.\COM3"
BAUD = 9600

# --- single-instance guard ---
LOCK_PATH = r"C:\StreamDeck\Arduino\serial_bridge.lock"
try:
    # O_EXCL makes this atomic: if it exists, someone else is running
    fd = os.open(LOCK_PATH, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    os.write(fd, str(os.getpid()).encode())
    os.close(fd)
except FileExistsError:
    print("[FAIL] serial_bridge.py already running (lock exists).")
    sys.exit(1)

def _cleanup():
    # close serial first, then remove lock
    try:
        if ser and ser.is_open:
            ser.close()
            print("[OK] Closed serial")
    except Exception:
        pass
    try:
        os.remove(LOCK_PATH)
    except Exception:
        pass

atexit.register(_cleanup)

print('boom control Start')
app = Flask(__name__)

# --- open serial ONCE ---
try:
    ser = serial.Serial(PORT, BAUD, timeout=1, write_timeout=1)
    time.sleep(2.0)  # let Arduino finish boot after port open (DTR reset)
    ser.reset_input_buffer()
    print(f"[OK] Opened {PORT} @ {BAUD}")
except Exception as e:
    print(f"[FAIL] Could not open {PORT}: {e}")
    sys.exit(1)

def send(cmd: str):
    payload = (cmd.strip() + "\n").encode("ascii", errors="ignore")
    ser.write(payload)
    ser.flush()
    print(f"[SERIAL] Sent: {cmd!r} bytes={len(payload)}")

@app.get("/fwd_down")
def fwd_down():
    send("FWD")
    return "ok"

@app.get("/fwd_up")
def fwd_up():
    send("STOP")
    return "ok"

@app.get("/rev_down")
def rev_down():
    send("REV")
    return "ok"

@app.get("/rev_up")
def rev_up():
    send("STOP")
    return "ok"

print("boom control end")
if __name__ == "__main__":
    # Turn off Flask reloader or it will spawn a second process (and re-open COM3)
    app.run(host="127.0.0.1", port=8787, debug=False, use_reloader=False)