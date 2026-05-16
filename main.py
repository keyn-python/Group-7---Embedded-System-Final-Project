from flask import Flask, render_template_string, request, jsonify
import requests
import os

app = Flask(__name__)

# --- ADAFRUIT IO CREDENTIALS ---
AIO_USERNAME = "CaineJimenez"
AIO_KEY = os.environ.get("AIO_KEY") # This hides your password!

# Note: Adafruit IO REST API uses lowercase and dashes for feed keys!
# If your feed is named "Energy_Management_System", the key is "energy-management-system"
FEED_KEY = "energy-management-system" 
AIO_URL = f"https://io.adafruit.com/api/v2/{AIO_USERNAME}/feeds/{FEED_KEY}/data"

HEADERS = {
    "X-AIO-Key": AIO_KEY,
    "Content-Type": "application/json"
}

# --- THE WEBSITE HTML ---
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
        #status { margin-top: 30px; font-weight: bold; color: #f9e2af; }
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
                    document.getElementById('status').innerText = "❌ Error sending command.";
                }
            })
            .catch(error => {
                document.getElementById('status').innerText = "❌ Network Error.";
            });
        }
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    # This serves the webpage when you visit the Railway URL
    return render_template_string(HTML_TEMPLATE)

@app.route('/command', methods=['POST'])
def command():
    # This receives the button click from the website and forwards it to Adafruit IO
    state = request.json.get('state')
    
    if state in ['ON', 'OFF']:
        payload = {"datum": {"value": state}}
        response = requests.post(AIO_URL, json=payload, headers=HEADERS)
        
        if response.status_code == 200:
            return jsonify({"status": "success", "state": state})
            
    return jsonify({"status": "error"}), 400

if __name__ == '__main__':
    # Railway requires apps to bind to the PORT environment variable
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
