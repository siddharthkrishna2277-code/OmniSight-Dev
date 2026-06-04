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
    "intel": "Launch your stream window or game client for profile: DIVISION2",
    "local_ip": "127.0.0.1"
}
SELECTED_GAME = "division2"

@app.route('/')
def index():
    # Hardcoded route to the file index.html
    return render_template('index.html', local_ip=UI_DATA["local_ip"])

@app.route('/api/data')
def get_data():
    return jsonify(UI_DATA)

@app.route('/api/select_game', methods=['POST'])
def select_game():
    global SELECTED_GAME
    data = request.get_json()
    if data and "game" in data:
        SELECTED_GAME = data["game"].strip().lower()
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

def start_server():
    # Hardcoded host and port for your local network
    app.run(host='127.0.0.1', port=5000, debug=False, use_reloader=False)

    # ADD THIS PART AT THE VERY BOTTOM, ALIGNED TO THE LEFT MARGIN
if __name__ == "__main__":
    start_server()