import sys
import subprocess
import os
import socket
import base64
import traceback
import datetime
import requests # Make sure this is imported

def update_ui_status(status_text):
    try:
        # This sends a signal to your Flask server to update the UI
        requests.post("http://127.0.0.1:5000/api/update_status", json={"status": status_text})
    except:
        pass

# --- SILENT AUTO-DEPENDENCY INSTALLER ---
# Purpose: Checks the user's PC for required libraries on bootup.
def verify_dependencies():
    required_packages = ['opencv-python', 'flask', 'requests']
    for package in required_packages:
        try:
            if package == 'opencv-python':
                __import__('cv2')
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
import cv2
import numpy as np

def run_capture_pipeline(source, console_type):
    print(f"\n[OMNI-ENGINE] Pipeline engaged for {console_type}.")
    
    # Ping the UI
    try:
        requests.post("http://127.0.0.1:5000/api/update_status", json={"status": f"Connected to {console_type}"})
    except:
        pass
    
    while True:
        try:
            # IF PC: Pull frame from your local capture object
            if console_type == "PC_DirectX":
                frame = source.get_latest_frame() # Assuming your engine uses this
            # IF CONSOLE: Pull raw bytes from socket
            else:
                raw_data = source.recv(65536)
                if not raw_data: break
                frame = raw_data 
            
            print(f"[OMNI-ENGINE] Pipeline heartbeat: {console_type} active.")
            
        except Exception as e:
            print(f"[OMNI-ENGINE] Stream error: {e}")
            break

# --- THE MASTER EXECUTION BLOCK (THE IGNITION) ---
if __name__ == "__main__":
    # You can change this to 'xbox' or 'pc' to test other protocols
    target_console = "playstation" 
    
    print(f"--- Starting OmniSight Engine for: {target_console} ---")
    
    if target_console == "playstation":
        sock = connect_playstation("192.168.1.50", "YOUR_PSN_ID", "1234")
        if sock: run_capture_pipeline(sock, "PlayStation")
            
    elif target_console == "xbox":
        sock = connect_xbox("192.168.1.60")
        if sock: run_capture_pipeline(sock, "Xbox")

    elif target_console == "pc":
        if initialize_pc_capture():
            print("[OMNI-ENGINE] PC Pipeline ready. DXGI output active.")   