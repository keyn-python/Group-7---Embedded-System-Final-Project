import os
from flask import Flask, jsonify

app = Flask(__name__)

# State to track the pump status
device_state = {"pump": "OFF"}

@app.route('/')
def home():
    return "<h1>EcoPot System Online</h1><p>Status: Monitoring soil moisture logic.</p>"

# Endpoint to check the current status (Used by ESP32)
@app.route('/status', methods=['GET'])
def get_status():
    return jsonify(device_state)

# Endpoint to change the status (Used by Google Voice/Dashboard)
@app.route('/set-pump/<action>', methods=['GET'])
def set_pump(action):
    action = action.upper()
    if action in ["ON", "OFF"]:
        device_state["pump"] = action
        return jsonify({"message": f"Pump state updated to {action}", "status": device_state["pump"]})
    return jsonify({"error": "Invalid action. Use ON or OFF"}), 400

if __name__ == "__main__":
    # Uses Railway's dynamic port or defaults to 8080 for local testing
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
