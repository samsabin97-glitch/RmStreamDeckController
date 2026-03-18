from flask import Flask, jsonify
import serial
from serial import SerialException
import time
import sys
import os
import atexit
import signal
import logging
import tempfile
from logging.handlers import RotatingFileHandler
from pathlib import Path
from threading import Lock
from typing import Optional, Tuple

# =========================
# APP INFO
# =========================
APP_NAME = "serial_bridge"
DEFAULT_HOST = "127.0.0.1"   # localhost only = firewall-friendlier
DEFAULT_PORT = 8787

# =========================
# RUNTIME PATH HELPERS
# =========================
def get_app_root() -> Path:
    """
    Return the folder the script/exe lives in.
    Works for both normal Python and PyInstaller onefile exe.
    """
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent


def ensure_writable_dir(preferred: Path) -> Path:
    """
    Use preferred folder if writable, otherwise fall back to LOCALAPPDATA
    or temp dir. This keeps the app portable and resilient.
    """
    candidates = [
        preferred,
        Path(os.getenv("LOCALAPPDATA", "")) / APP_NAME if os.getenv("LOCALAPPDATA") else None,
        Path(tempfile.gettempdir()) / APP_NAME,
    ]

    for candidate in candidates:
        if candidate is None:
            continue
        try:
            candidate.mkdir(parents=True, exist_ok=True)
            test_file = candidate / ".write_test"
            test_file.write_text("ok", encoding="utf-8")
            test_file.unlink(missing_ok=True)
            return candidate
        except Exception:
            continue

    raise RuntimeError("Could not find a writable runtime directory")


APP_ROOT = get_app_root()
DATA_DIR = ensure_writable_dir(APP_ROOT / "data")

# =========================
# CONFIG
# =========================
PRIMARY_PORT = os.getenv("SERIAL_BRIDGE_PORT1", r"\\.\COM3")
SECONDARY_PORT = os.getenv("SERIAL_BRIDGE_PORT2", r"\\.\COM4")
BAUD = int(os.getenv("SERIAL_BRIDGE_BAUD", "9600"))

HOST = os.getenv("SERIAL_BRIDGE_HOST", DEFAULT_HOST)
PORT = int(os.getenv("SERIAL_BRIDGE_HTTP_PORT", str(DEFAULT_PORT)))

STARTUP_DELAY = float(os.getenv("SERIAL_BRIDGE_STARTUP_DELAY", "2.0"))
SERIAL_TIMEOUT = float(os.getenv("SERIAL_BRIDGE_SERIAL_TIMEOUT", "1.0"))
WRITE_TIMEOUT = float(os.getenv("SERIAL_BRIDGE_WRITE_TIMEOUT", "1.0"))
RECONNECT_DELAY = float(os.getenv("SERIAL_BRIDGE_RECONNECT_DELAY", "1.5"))

LOCK_PATH = DATA_DIR / f"{APP_NAME}.lock"
LOG_PATH = DATA_DIR / f"{APP_NAME}.log"

LOG_MAX_BYTES = 1_000_000
LOG_BACKUP_COUNT = 5

# =========================
# GLOBALS
# =========================
app = Flask(__name__)
ser: Optional[serial.Serial] = None
serial_lock = Lock()
active_port: Optional[str] = None
shutdown_requested = False


# =========================
# LOGGING
# =========================
def setup_logging() -> logging.Logger:
    logger = logging.getLogger(APP_NAME)
    logger.setLevel(logging.INFO)
    logger.propagate = False

    if logger.handlers:
        return logger

    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    file_handler = RotatingFileHandler(
        LOG_PATH,
        maxBytes=LOG_MAX_BYTES,
        backupCount=LOG_BACKUP_COUNT,
        encoding="utf-8",
    )
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    return logger


logger = setup_logging()
logger.info("Starting %s | PID=%s", APP_NAME, os.getpid())
logger.info("APP_ROOT=%s", APP_ROOT)
logger.info("DATA_DIR=%s", DATA_DIR)


# =========================
# PID / LOCK HELPERS
# =========================
def pid_exists(pid: int) -> bool:
    if pid <= 0:
        return False

    try:
        if os.name == "nt":
            import ctypes
            PROCESS_QUERY_LIMITED_INFORMATION = 0x1000
            handle = ctypes.windll.kernel32.OpenProcess(
                PROCESS_QUERY_LIMITED_INFORMATION, False, pid
            )
            if handle == 0:
                return False
            ctypes.windll.kernel32.CloseHandle(handle)
            return True
        else:
            os.kill(pid, 0)
            return True
    except Exception:
        return False


def remove_lock() -> None:
    try:
        if LOCK_PATH.exists():
            LOCK_PATH.unlink()
            logger.info("Removed lock file: %s", LOCK_PATH)
    except Exception as e:
        logger.warning("Failed removing lock file: %s", e)


def create_lock() -> None:
    if LOCK_PATH.exists():
        try:
            existing_pid_raw = LOCK_PATH.read_text(encoding="utf-8").strip()
            existing_pid = int(existing_pid_raw)

            if pid_exists(existing_pid):
                logger.error("Another instance is already running. PID=%s", existing_pid)
                sys.exit(1)

            logger.warning("Found stale lock from dead PID %s. Removing it.", existing_pid)
            remove_lock()

        except ValueError:
            logger.warning("Lock file contents invalid. Removing stale lock.")
            remove_lock()
        except Exception as e:
            logger.warning("Could not inspect lock file: %s. Removing it.", e)
            remove_lock()

    try:
        fd = os.open(str(LOCK_PATH), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        os.write(fd, str(os.getpid()).encode("utf-8"))
        os.close(fd)
        logger.info("Acquired lock: %s", LOCK_PATH)
    except FileExistsError:
        logger.error("Lock already exists. Refusing to start.")
        sys.exit(1)


# =========================
# SERIAL HELPERS
# =========================
def _try_open_port(port_name: str) -> Optional[serial.Serial]:
    logger.info("Trying serial port %s @ %s", port_name, BAUD)
    try:
        candidate = serial.Serial(
            port=port_name,
            baudrate=BAUD,
            timeout=SERIAL_TIMEOUT,
            write_timeout=WRITE_TIMEOUT,
        )
        time.sleep(STARTUP_DELAY)
        candidate.reset_input_buffer()
        logger.info("Opened serial port %s", port_name)
        return candidate
    except Exception as e:
        logger.warning("Failed to open %s: %s", port_name, e)
        return None


def open_serial() -> serial.Serial:
    global ser, active_port

    for port_name in (PRIMARY_PORT, SECONDARY_PORT):
        candidate = _try_open_port(port_name)
        if candidate is not None:
            ser = candidate
            active_port = port_name
            return ser

    raise RuntimeError("Unable to open any configured serial port")


def close_serial() -> None:
    global ser, active_port

    try:
        if ser is not None and ser.is_open:
            ser.close()
            logger.info("Closed serial port %s", active_port)
    except Exception as e:
        logger.warning("Error closing serial port: %s", e)
    finally:
        ser = None
        active_port = None


def ensure_serial() -> None:
    global ser

    if shutdown_requested:
        raise RuntimeError("Shutdown in progress")

    if ser is not None and ser.is_open:
        return

    logger.warning("Serial not connected. Attempting reopen in %.1f sec...", RECONNECT_DELAY)
    time.sleep(RECONNECT_DELAY)
    open_serial()


def send(cmd: str) -> Tuple[bool, Optional[str]]:
    payload = (cmd.strip() + "\n").encode("ascii", errors="ignore")

    with serial_lock:
        try:
            ensure_serial()
            assert ser is not None
            ser.write(payload)
            ser.flush()
            logger.info("Sent command=%r bytes=%s port=%s", cmd, len(payload), active_port)
            return True, None

        except (SerialException, OSError) as e:
            logger.warning("Serial write failed for %r: %s", cmd, e)
            close_serial()

            try:
                logger.info("Attempting reconnect and retry for command=%r", cmd)
                open_serial()
                assert ser is not None
                ser.write(payload)
                ser.flush()
                logger.info("Sent after reconnect command=%r bytes=%s port=%s", cmd, len(payload), active_port)
                return True, None
            except Exception as e2:
                logger.error("Reconnect/retry failed for %r: %s", cmd, e2)
                close_serial()
                return False, str(e2)

        except Exception as e:
            logger.exception("Unexpected send error for %r", cmd)
            return False, str(e)


# =========================
# CLEANUP
# =========================
def cleanup() -> None:
    close_serial()
    remove_lock()


def handle_exit(signum=None, frame=None) -> None:
    global shutdown_requested
    shutdown_requested = True
    logger.info("Shutdown requested signal=%s", signum)
    cleanup()
    sys.exit(0)


atexit.register(cleanup)

if hasattr(signal, "SIGINT"):
    signal.signal(signal.SIGINT, handle_exit)
if hasattr(signal, "SIGTERM"):
    signal.signal(signal.SIGTERM, handle_exit)


# =========================
# ROUTES
# =========================
@app.get("/health")
def health():
    connected = bool(ser is not None and ser.is_open)
    return jsonify(
        ok=True,
        app=APP_NAME,
        pid=os.getpid(),
        serial_connected=connected,
        serial_port=active_port,
        baud=BAUD,
        host=HOST,
        http_port=PORT,
        data_dir=str(DATA_DIR),
        log_file=str(LOG_PATH),
    )


@app.get("/fwd_down")
def fwd_down():
    ok, err = send("FWD")
    return jsonify(ok=ok, command="FWD", error=err), (200 if ok else 500)


@app.get("/fwd_up")
def fwd_up():
    ok, err = send("STOP")
    return jsonify(ok=ok, command="STOP", error=err), (200 if ok else 500)


@app.get("/rev_down")
def rev_down():
    ok, err = send("REV")
    return jsonify(ok=ok, command="REV", error=err), (200 if ok else 500)


@app.get("/rev_up")
def rev_up():
    ok, err = send("STOP")
    return jsonify(ok=ok, command="STOP", error=err), (200 if ok else 500)


@app.get("/stop")
def stop():
    ok, err = send("STOP")
    return jsonify(ok=ok, command="STOP", error=err), (200 if ok else 500)


@app.get("/shutdown_serial")
def shutdown_serial():
    with serial_lock:
        close_serial()
    return jsonify(ok=True, message="Serial port closed")


# =========================
# STARTUP
# =========================
def startup() -> None:
    create_lock()
    try:
        open_serial()
    except Exception as e:
        logger.error("Startup serial open failed: %s", e)
        cleanup()
        sys.exit(1)


if __name__ == "__main__":
    startup()
    logger.info("Flask server starting on http://%s:%s", HOST, PORT)
    app.run(
        host=HOST,
        port=PORT,
        debug=False,
        use_reloader=False,
        threaded=True,
    )