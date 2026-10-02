HOW TO RUN

1. Install Python libraries:

pip install flask flask-cors pyserial

2. Upload station_arduino_combined.ino to Arduino.

3. Open server.py and set your Arduino port:

SERIAL_PORT = "COM3"

4. Run:

python server.py

5. Open eco_container_all_functions_restored_detection.html with VS Code Live Server.

6. Login.

7. Click 借用／歸還.

8. Input station:

A01

or:

1

9. Click 配對站點.

10. Choose 借用 or 歸還.

11. Enter cup count.

12. Send.

Important change:
- 已借用環保杯總數 only increases after return is completed.
- 減碳額度 also only increases after return is completed.
- Borrowing only decreases available containers.
- Returning increases successful cycle count.

Arduino:
- Uses the uploaded ultrasonic cup detection logic.
- Boxes are ignored/simulated for now because there is no box sensor yet.
