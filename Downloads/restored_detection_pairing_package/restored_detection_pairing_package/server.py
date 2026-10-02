from flask import Flask, request, jsonify
from flask_cors import CORS
import serial
import threading
import time

app = Flask(__name__)
CORS(app)

SERIAL_PORT = "COM7"
BAUD_RATE = 9600

serial_lock = threading.Lock()  # NEW

stations = {
    "A01": {
        "id": "A01",
        "name": "A01 校園正門借還站",
        "online": True,
        "cups": 6,
        "boxes": 4,
        "last_cup_count": 0,
        "return_start_count": 0,
        "return_target": 0,
        "return_status": "idle"
    },
    "B02": {
        "id": "B02",
        "name": "B02 圖書館側門借還站",
        "online": True,
        "cups": 3,
        "boxes": 2,
        "last_cup_count": 0,
        "return_start_count": 0,
        "return_target": 0,
        "return_status": "idle"
    }
}

try:
    arduino = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
    time.sleep(2)
    print("Arduino connected:", SERIAL_PORT)
except Exception as e:
    arduino = None
    print("Arduino not connected:", e)
    print("Demo mode enabled.")

def read_arduino_background():
    while True:
        if arduino:
            try:
                with serial_lock:
                    line = arduino.readline().decode(errors="ignore").strip()
                if line:
                    print("Arduino:", line)

                if line.startswith("STATION_READY,"):
                    station_id = line.split(",", 1)[1].strip().upper()
                    if station_id in stations:
                        stations[station_id]["online"] = True

                if line.startswith("CUP_COUNT,"):
                    parts = line.split(",")
                    if len(parts) >= 3:
                        station_id = parts[1].strip().upper()
                        count = int(parts[2])
                        if station_id in stations:
                            stations[station_id]["last_cup_count"] = count
                            s = stations[station_id]
                            print(f"CUP_COUNT updated: {count} | return_status: {s['return_status']} | start: {s['return_start_count']} | target: {s['return_target']} | returned so far: {count - s['return_start_count']}")
                            if s["return_status"] == "waiting":
                                returned = count - s["return_start_count"]
                                if returned >= s["return_target"]:
                                    s["return_status"] = "success"
                                    print(f">>> RETURN SUCCESS: {returned} cups returned")

                if line == "ERROR_RETURN_TIMEOUT":
                    for s in stations.values():
                        if s["return_status"] == "waiting":
                            s["return_status"] = "timeout"

            except Exception as e:
                print("Read error:", e)
        time.sleep(0.05)

threading.Thread(target=read_arduino_background, daemon=True).start()

@app.route("/pair", methods=["POST"])
def pair():
    data = request.json or {}
    station_id = str(data.get("station_id", "")).upper().strip()
    if station_id == "1": station_id = "A01"
    if station_id == "2": station_id = "B02"

    if station_id in stations:
        station = stations[station_id]
        return jsonify({
            "paired": True,
            "id": station["id"],
            "name": station["name"],
            "cups": station["cups"],
            "boxes": station["boxes"]
        })
    return jsonify({"paired": False})

@app.route("/start_return", methods=["POST"])
def return_cups():
    data = request.json or {}
    station_id = str(data.get("station_id", "")).upper().strip()
    cups = int(data.get("cups", 0))

    if station_id not in stations:
        return jsonify({"status": "failed", "message": "station not found"})

    s = stations[station_id]
    s["return_start_count"] = s["last_cup_count"]
    s["return_target"] = cups
    s["return_status"] = "waiting"
    print(f">>> RETURN started: target={cups}, start_count={s['last_cup_count']}")

    if arduino:
        with serial_lock:
            arduino.write(f"RETURN,{cups},0\n".encode())
        print(f"Sent to Arduino: RETURN,{cups},0")

    return jsonify({"status": "waiting"})

@app.route("/return_status", methods=["GET"])
def return_status():
    station_id = request.args.get("station_id", "A01").upper()
    if station_id not in stations:
        return jsonify({"status": "failed"})

    s = stations[station_id]
    returned = s["last_cup_count"] - s["return_start_count"]
    if returned < 0: returned = 0

    return jsonify({
        "status": s["return_status"],
        "returned": returned,
        "target": s["return_target"]
    })

@app.route("/command", methods=["POST"])
def command():
    data = request.json or {}
    station_id = str(data.get("station_id", "")).upper().strip()
    mode = str(data.get("mode", "")).upper().strip()
    cups = int(data.get("cups", 0))
    boxes = int(data.get("boxes", 0))

    if station_id not in stations:
        return jsonify({"status": "failed", "message": "station not found"})

    command_string = f"{mode},{cups},{boxes}\n"
    print("Sending to Arduino:", command_string.strip())

    if arduino:
        with serial_lock:
            arduino.write(command_string.encode())
            start = time.time()
            while time.time() - start < 35:
                response = arduino.readline().decode(errors="ignore").strip()
                if response: print("Arduino response:", response)
                if response == "DONE":
                    return jsonify({"status": "success"})
                if response.startswith("ERROR"):
                    return jsonify({"status": "failed", "message": response})
        return jsonify({"status": "failed", "message": "Arduino timeout"})

    time.sleep(1.5)
    return jsonify({"status": "success"})

if __name__ == "__main__":
    app.run(port=5000, debug=False)