from flask import Flask, render_template_string, request, jsonify
import requests
import os

app = Flask(__name__)

# --- ADAFRUIT IO CREDENTIALS ---
AIO_USERNAME = "CaineJimenez"
AIO_KEY = os.environ.get("AIO_KEY") 

FEED_KEY = "energy-management-system" 
AIO_URL = f"https://io.adafruit.com/api/v2/{AIO_USERNAME}/feeds/{FEED_KEY}/data"

# --- THE WEBSITE HTML (Upgraded to show exact errors) ---
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Smart Pump Dashboard</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; text-align: center; margin-top: 10%; background-color: #1e1e2e; color: #cdd6f4;}
        h1 { color: #89b4fa; }
        p { color: #a6adc8; font-size: 18px; }
        .btn-container { margin-top: 40px; }
        button { padding: 20px 50px; font-size: 22px; font-weight: bold; margin: 10px; border-radius: 12px; border: none; cursor: pointer; transition: 0.2s; color: white;}
        .on-btn { background-color: #a6e3a1; color: #11111b;}
        .off-btn { background-color: #f38ba8; color: #11111b;}
        .on-btn:hover { background-color: #94cc90; transform: scale(1.05); }
        .off-btn:hover { background-color: #d97d96; transform: scale(1.05); }
        #status { margin-top: 30px; font-weight: bold; color: #f9e2af; padding: 0 20px;}
    </style>
</head>
<body>
    <h1>🌱 Smart Irrigation Control</h1>
    <p>Control your ESP32 Pump directly from the cloud.</p>
    
    <div class="btn-container">
        <button class="on-btn" onclick="sendCommand('ON')">WATER PLANT</button>
        <button class="off-btn" onclick="sendCommand('OFF')">STOP PUMP</button>
    </div>
    
    <p id="status"></p>

    <script>
        function sendCommand(state) {
            document.getElementById('status').innerText = "Sending command to cloud...";
            fetch('/command', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ state: state })
            })
            .then(response => response.json())
            .then(data => {
                if(data.status === "success") {
                    document.getElementById('status').innerText = "✅ Success: Pump is " + state;
                } else {
                    // This prints the EXACT error from Adafruit!
                    document.getElementById('status').innerText = "❌ API Error: " + data.message;
                }
            })
            .catch(error => {
                document.getElementById('status').innerText = "❌ Network Error: " + error.message;
            });
        }
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route('/command', methods=['POST'])
def command():
    state = request.json.get('state')
    
    # 1. Check if Railway actually loaded your secret password!
    if not AIO_KEY:
        return jsonify({"status": "error", "message": "AIO_KEY variable is missing in Railway! Go to Variables tab."}), 400

    headers = {
        "X-AIO-Key": AIO_KEY,
        "Content-Type": "application/json"
    }
    
    if state in ['ON', 'OFF']:
        payload = {"value": state}
        
        try:
            # Send the request to Adafruit
            response = requests.post(AIO_URL, json=payload, headers=headers)
            
            if response.status_code == 200:
                return jsonify({"status": "success", "state": state})
            else:
                # 2. If it fails, capture the exact HTTP Code and Adafruit's complaint
                error_msg = f"{response.status_code} - {response.text}"
                return jsonify({"status": "error", "message": error_msg}), 400
                
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)}), 500
            
    return jsonify({"status": "error", "message": "Invalid command"}), 400

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
