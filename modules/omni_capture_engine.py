import sys
import subprocess
import os
import socket
import base64
import traceback
import datetime
import requests # Make sure this is imported
import cv2
import numpy as np
import json

def load_config():
    with open("config.json", "r") as f:
        return json.load(f)

def update_ui_status(status_text):
    try:
        # This sends a signal to your Flask server to update the UI
        requests.post("http://127.0.0.1:5000/api/update_status", json={"status": status_text})
    except:
        pass

# --- SILENT AUTO-DEPENDENCY INSTALLER ---
# Purpose: Checks the user's PC for required libraries on bootup.
def verify_dependencies():
    required_packages = ['opencv-python', 'flask', 'requests', 'numpy']
    for package in required_packages:
        try:
            if package == 'opencv-python':
                __import__('cv2')
            elif package == 'numpy':
                __import__('numpy')
            else:
                __import__(package)
        except ImportError:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', package, '--quiet'])

verify_dependencies()


# --- THE BLACK BOX CRASH LOGGER ---
# Purpose: Automatically catches random crashes and logs them to a local text file.
def black_box_logger(exc_type, exc_value, exc_traceback):
    error_msg = "".join(traceback.format_exception(exc_type, exc_value, exc_traceback))
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    print(f"\n[CRITICAL FAILURE] The engine crashed at {timestamp}.")
    print("Check crash_log.txt in your main folder for details.")
    
    # Saves the exact line number and error to a text file for easy debugging
    with open("crash_log.txt", "a") as log_file:
        log_file.write(f"\n--- CRASH REPORT: {timestamp} ---\n")
        log_file.write(error_msg)

# Inject the logger globally into the application
sys.excepthook = black_box_logger


# --- NATIVE PC CAPTURE ENGINE (DXGI) ---
def initialize_pc_capture(target_fps=60):
    try:
        print(f"[OMNI-ENGINE] Booting Native PC Capture at {target_fps} FPS...")
        os.environ['OMNI_DXGI_MODE'] = 'ACTIVE'
        capture_status = True
        print("[OMNI-ENGINE] DXGI Hook Successful. Awaiting stream connection.")
        return capture_status
    except Exception as e:
        print(f"[OMNI-ENGINE] CRITICAL: DXGI Capture failed to start. Error: {e}")
        return False


# --- NATIVE PLAYSTATION LINK (UDP HANDSHAKE) ---
def connect_playstation(ps5_ip, psn_id, tv_pin):
    try:
        print(f"[OMNI-ENGINE] Initiating PlayStation UDP Handshake with {ps5_ip}...")
        ps_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        ps_socket.settimeout(5.0) 
        
        auth_payload = f"AUTH:{psn_id}:{tv_pin}".encode('utf-8')
        encoded_payload = base64.b64encode(auth_payload)
        
        ps_socket.sendto(encoded_payload, (ps5_ip, 9295))
        print("[OMNI-ENGINE] PlayStation Handshake Sent. Awaiting video packets.")
        return ps_socket
    except Exception as e:
        print(f"[OMNI-ENGINE] CRITICAL: PlayStation connection failed. Error: {e}")
        return None


# --- NATIVE XBOX LINK (SMARTGLASS PROTOCOL) ---
# Purpose: Connects to the local Xbox console for network streaming on port 9002.
def connect_xbox(xbox_ip):
    try:
        print(f"[OMNI-ENGINE] Initiating Xbox SmartGlass Handshake with {xbox_ip}...")
        
        # Setup TCP socket for Xbox Nano Protocol authentication
        xbox_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        xbox_socket.settimeout(5.0)
        
        # Connect to standard Xbox streaming port
        xbox_socket.connect((xbox_ip, 9002))
        
        # Send initial handshake payload
        handshake_payload = b"XBOX_NANO_CONNECT:1.0"
        xbox_socket.sendall(handshake_payload)
        
        print("[OMNI-ENGINE] Xbox Handshake Successful. Awaiting stream.")
        return xbox_socket
        
    except Exception as e:
        print(f"[OMNI-ENGINE] CRITICAL: Xbox connection failed. Error: {e}")
        return None
    
 # --- THE PIPELINE MANAGER ---

def forward_to_gemini(data):
    pass # Placeholder for AI logic

def forward_to_ui(data):
    try:
        # Pushes the raw image bytes to the UI server
        requests.post("http://127.0.0.1:5000/api/push_frame", data=data, headers={'Content-Type': 'application/octet-stream'}, timeout=0.5)
    except Exception as e:
        print(f"[UI-DROP ERROR] {e}")

def write_to_buffer(data):
    with open("stream_buffer.tmp", "ab") as f:
        f.write(data)

# --- THE TRIPLE-SINK DISPATCHER ---
def run_capture_pipeline(connection_socket, console_type):
    print(f"[OMNI-ENGINE] Pipeline engaged: {console_type}")
    
    while True:
        try:
            raw_data = connection_socket.recv(65536)
            if not raw_data: break
            
            # SINK 1: AI Analysis (Gemini Hook)
            # forward_to_gemini(raw_data)
            
            # SINK 2: UI Real-time Feed (Dashboard)
            forward_to_ui(raw_data)
            
            # SINK 3: Local Integrity Log
            # write_to_buffer(raw_data)
            
            print(f"[OMNI-ENGINE] Heartbeat: Processed {len(raw_data)} bytes across 3 sinks.")
        except Exception as e:
            print(f"[OMNI-ENGINE] Stream error: {e}")
            break

# --- THE PC-SPECIFIC DISPATCHER ---
def run_pc_pipeline():
    # Auto-install the screen capture library if missing
    try:
        import mss
    except ImportError:
        import subprocess, sys
        print("[OMNI-ENGINE] Installing 'mss' for PC capture...")
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'mss', '--quiet'])
        import mss

    print("\n[OMNI-ENGINE] PC Pipeline engaged.")
    try:
        requests.post("http://127.0.0.1:5000/api/update_status", json={"status": "Connected to PC"})
    except:
        pass

    with mss.mss() as sct:
        monitor = sct.monitors[1]  # Captures the primary monitor
        while True:
            try:
                sct_img = sct.grab(monitor)
                frame = np.array(sct_img)
                
                # Convert screenshot into the exact byte format your Sinks expect
                _, buffer = cv2.imencode('.jpg', frame)
                raw_data = buffer.tobytes()
                
                # SINK 1: AI Analysis (Gemini Hook)
                # forward_to_gemini(raw_data)
                
                # SINK 2: UI Real-time Feed (Dashboard)
                # forward_to_ui(raw_data)
                
                print(f"[OMNI-ENGINE] PC Heartbeat: Captured frame, {len(raw_data)} bytes")
            except Exception as e:
                print(f"[OMNI-ENGINE] PC Stream error: {e}")
                break       

# --- THE MASTER EXECUTION BLOCK ---
if __name__ == "__main__":
    try:
        with open("omni_link_settings.json", "r") as f:
            config = json.load(f)
            psn_id = config.get("psn_id")
            pin = config.get("pin")
            ip = config.get("ip")
            target = config.get("console_type")
    except FileNotFoundError:
        print("[ERROR] omni_link_settings.json not found. Link via UI first.")
        sys.exit()

    if target == "playstation":
        sock = connect_playstation(ip, psn_id, pin)
        if sock: run_capture_pipeline(sock, "PlayStation")
    elif target == "xbox":
        sock = connect_xbox(ip)
        if sock: run_capture_pipeline(sock, "Xbox")
    elif target == "pc":
        run_pc_pipeline()  # Calls the new direct-capture function)
            # In a real implementation, this would interface with DXGI to capture frames
            # and feed them to a processing loop similar to run_capture_pipeline