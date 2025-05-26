import serial
import time
from datetime import datetime
import os

SERIAL_PORT = "/dev/ttyACM0"
BAUD_RATE = 115200
LOG_FILE = "tank_data.csv"

def parse_message(line):
    # Example: [2025-05-26 08:14:03] Dry Creek: 14.6 inches
    try:
        timestamp_end = line.find(']')
        timestamp = line[1:timestamp_end]

        rest = line[timestamp_end+2:]
        tank_id, depth_str = rest.split(':')
        tank_id = tank_id.strip()
        depth = float(depth_str.replace("inches", "").strip())

        return f"{timestamp},{tank_id},{depth:.2f}"
    except Exception as e:
        print(f"Parse error: {e}")
        return None

def main():
    if not os.path.exists(LOG_FILE):
        with open(LOG_FILE, "w") as f:
            f.write("timestamp,tank_id,inches\n")

    ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=5)
    print(f"Listening on {SERIAL_PORT}...")

    while True:
        try:
            line = ser.readline().decode("utf-8", errors="ignore").strip()
            if line:
                print(f"Raw line: {line}")
                parsed = parse_message(line)
                if parsed:
                    with open(LOG_FILE, "a") as f:
                        f.write(parsed + "\n")
                    print("Logged:", parsed)
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(1)

if __name__ == "__main__":
    main()
