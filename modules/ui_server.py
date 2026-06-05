print("DEBUG: The file is executing!")
# type: ignore
import logging
from flask import Flask, render_template, jsonify, request, make_response

# 🚨 Hardcoded server setup: Pointing directly to the sub-folder
app = Flask(__name__, template_folder='templates', static_folder='static')

# Force Flask to reload the index.html file whenever you save it
app.config['TEMPLATES_AUTO_RELOAD'] = True

log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

# Hardcoded initial state
UI_DATA = {
    "status": "SYSTEM SYNCHRONIZED",
    "source": "Awaiting Native Link...",
    "intel": "Launch your stream window or game client for profile: NONE",
    "local_ip": "127.0.0.1"
}
SELECTED_GAME = "none"

@app.route('/')
def index():
    # Hardcoded route to the file index.html
    return render_template('index.html', local_ip=UI_DATA["local_ip"])

@app.route('/api/data')
def get_data():
    return jsonify(UI_DATA)

@app.route('/api/select_game', methods=['POST'])
def select_game():
    global SELECTED_GAME, UI_DATA
    data = request.get_json()
    if data and "game" in data:
        game_name = data["game"].strip().lower()
        SELECTED_GAME = game_name

        UI_DATA["intel"] = f"Launch your stream window or game client for profile: {game_name.upper()}"
        
        return jsonify({"status": "success"})
    return jsonify({"status": "error"}), 400

@app.route('/api/force_simulation', methods=['POST'])
def force_simulation():
    global UI_DATA
    # Set simulation mode data
    UI_DATA["status"] = "SIMULATION ACTIVE"
    UI_DATA["source"] = "Native Link: SIMULATED"
    UI_DATA["intel"] = "Launch your stream window or game client for profile: DIVISION2 (SIMULATION MODE)"
    return jsonify({"status": "success", "message": "Simulation mode activated"})

# --- ADDED: BRIDGE ROUTE ---
@app.route('/api/update_status', methods=['POST'])
def update_status():
    global UI_DATA
    data = request.get_json()
    UI_DATA["source"] = data.get("status", "Unknown")
    return jsonify({"status": "success"})

import json

@app.route('/api/link_console', methods=['POST'])
def link_console():
    data = request.get_json()
    with open("modules/omni_link_settings.json", "w") as f:
        json.dump(data, f)
    return jsonify({"status": "Configuration Saved"})

from flask import Response, request

# Buffer to hold the latest video frame
global_frame = None

@app.route('/api/push_frame', methods=['POST'])
def push_frame():
    global global_frame
    global_frame = request.data
    return "OK", 200

def generate_feed():
    global global_frame
    import time
    while True:
        if global_frame:
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + global_frame + b'\r\n')
        # This keeps the loop alive but yields control back to the server
        time.sleep(0.05)

@app.route('/video_feed')
def video_feed():
    # This route streams the video to your HTML dashboard
    return Response(generate_feed(), mimetype='multipart/x-mixed-replace; boundary=frame')

def start_server():
    # Hardcoded host and port for your local network
    app.run(host='127.0.0.1', port=5000, debug=False, use_reloader=False)

# ADD THIS PART AT THE VERY BOTTOM, ALIGNED TO THE LEFT MARGIN
if __name__ == "__main__":
    start_server()