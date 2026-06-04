# type: ignore
import os
import logging
from flask import Flask, render_template, jsonify, request, make_response

# Point Flask explicitly to the clean standalone directories
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
template_dir = os.path.join(BASE_DIR, 'templates')
static_dir = os.path.join(BASE_DIR, 'static')

app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)

# Suppress annoying background terminal web spam
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

# Global runtime state tracking
UI_DATA = {
    "status": "SYSTEM SYNCHRONIZED",
    "source": "Awaiting Native Link...",
    "intel": "Launch your stream window or game client for profile: DIVISION2",
    "local_ip": "127.0.0.1"
}
SELECTED_GAME = "division2"

@app.route('/')
def index():
    # Flask safely injects local_ip straight into templates/index.html
    response = make_response(render_template('index.html', local_ip=UI_DATA["local_ip"]))
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

@app.route('/api/data')
def get_data():
    return jsonify(UI_DATA)

@app.route('/api/select_game', methods=['POST'])
def select_game():
    global SELECTED_GAME
    try:
        data = request.get_json()
        if not data or "game" not in data:
            return jsonify({"status": "error", "message": "Malformed configuration payload"}), 400
            
        selected_game = data["game"].strip().lower()
        if selected_game in ["division2", "destiny2", "diablo4"]:
            SELECTED_GAME = selected_game
            return jsonify({"status": "success", "active_game": SELECTED_GAME})
            
        return jsonify({"status": "error", "message": "Unsupported target game profile"}), 400
    except Exception as e:
        return jsonify({"status": "error", "message": f"Server processing breakdown: {str(e)}"}), 500

@app.route('/api/force_simulation', methods=['POST'])
def force_simulation():
    global UI_DATA
    UI_DATA["status"] = "SYNCHRONIZED TEST"
    UI_DATA["source"] = "Simulated Core Matrix Injector"
    UI_DATA["intel"] = """### 🚨 COGNITIVE SYSTEM OVERRIDE INTEGRITY INTERCEPT\n* **Simulated Drop Triggered:** Exotic Analytical Data Card Array processed successfully.\n* **Recalibration Library Alert:** Affix values verified within maximum 100% brackets.\n* **Diagnostic Report:** Interface layouts, tab toggles, and processing pipelines are executing flawlessly."""
    return jsonify({"status": "success"})

def get_selected_game():
    global SELECTED_GAME
    return SELECTED_GAME

def update_ui_data(status, source, intel):
    global UI_DATA
    UI_DATA["status"] = status
    UI_DATA["source"] = source
    UI_DATA["intel"] = intel

def start_server():
    try:
        # Route on 0.0.0.0 to enable mobile sync over Wi-Fi
        app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False, threaded=True)
    except Exception as e:
        print(f"[UI-SERVER] ⚠️ Server deployment exception caught: {str(e)}")