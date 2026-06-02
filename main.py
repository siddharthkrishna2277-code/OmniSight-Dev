import os
import sys
import time
import requests
import socket
import threading
import json
import shutil
import zipfile
import io

# --- OMNISIGHT V1 CORE IMPORTS ---
import cloud_config
from modules import window_grabber, freeze_detector, gemini_client, ui_server, omni_capture_engine

LOCAL_VERSION = "1.0.0"
UPDATE_URL = "https://raw.githubusercontent.com/siddharthkrishna2277-code/OmniSight-Dev/refs/heads/main/main.py"

# 🛡️ THE SYSTEM FEATURE MANIFEST LEDGER
SYSTEM_FEATURE_MANIFEST = {
    "version": LOCAL_VERSION,
    "features": {
        "sidebar_refinement": {"status": "Verified", "type": "UI_Layout"},
        "native_streaming_pipeline": {"status": "Verified", "type": "Network_Core"},
        "zero_app_onboarding_guide": {"status": "Verified", "type": "UI_Layout"},
        "connected_settings_panel": {"status": "Verified", "type": "UI_Layout"},
        "static_visual_storefront": {"status": "Verified", "type": "UI_Layout"},
        "hidden_developer_suite": {"status": "Verified", "type": "Admin_Core"}
    },
    "required_files": [
        "window_grabber.py",
        "freeze_detector.py",
        "gemini_client.py",
        "ui_server.py"
    ]
}

# Reformatted to single-line strings
GAME_PROMPTS = {
    "division2": "You are ISAC, an elite AI tactical assistant for a Level 40 agent in The Division 2.\n1. Look for Max Rolls (bars filled 100% to the right). If found, flag it: '🚨 RECALIBRATION LIBRARY WARNING: Extract this!'\n2. Track green gear sets (Striker, Hunter's Fury) and advise if it triggers their 4-piece talent.\n3. If it has weapon damage with skill stats, flag it as a Mismatched Hybrid for a Drone/Turret build.\nProvide exactly 3 punchy, high-intelligence tactical bullet points in clean Markdown.",
    "destiny2": "You are a Ghost tactical armor evaluation link for Destiny 2.\n1. Scan the weapon/armor perks and stats. Identify the weapon archetype.\n2. Flag if this roll is a PvE 'God Roll' or PvP 'Crucible Roll' based on structural trait combinations.\n3. Check the Resilience or Recovery tier impact.\nProvide exactly 3 short, space-magic analytical bullet points in clean Markdown.",
    "diablo4": "You are a Horadric Archive analyzer for Diablo IV loot.\n1. Scan the item aspects and minor affix rolls.\n2. Advise if the stat ranges are near max roll brackets for endgame builds.\n3. Flag if the legendary aspect should be extracted to the Codex of Power or salvaged.\nProvide exactly 3 dark, clear tactical analysis bullet points in clean Markdown."
}

def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"

def crop_screen_by_game_rules(frame, game):
    if frame is None:
        return None
    height, width, _ = frame.shape
    
    if game == "division2":
        return frame[int(height*0.15):int(height*0.85), int(width*0.65):int(width*0.98)]
    elif game == "destiny2":
        return frame[int(height*0.10):int(height*0.90), int(width*0.05):int(width*0.50)]
    else:
        return frame[int(height*0.10):int(height*0.90), int(width*0.50):int(width*0.95)]

def execute_dynamic_updater():
    ZIP_URL = "https://github.com/siddharthkrishna2277-code/OmniSight-Dev/archive/refs/heads/main.zip"
    print("📡 Checking the cloud for new engine updates...")
    try:
        response = requests.get(ZIP_URL)
        if response.status_code == 200:
            print("📥 Update found! Downloading and preparing extraction...")
            with zipfile.ZipFile(io.BytesIO(response.content)) as zip_ref:
                temp_dir = "omnisight_temp_update"
                zip_ref.extractall(temp_dir)
                extracted_folder = os.path.join(temp_dir, os.listdir(temp_dir)[0])
                print("🗑️ Wiping old files and installing new architecture...")
                for item in os.listdir(extracted_folder):
                    source_path = os.path.join(extracted_folder, item)
                    destination_path = os.path.join(os.getcwd(), item)
                    if os.path.isdir(source_path):
                        if os.path.exists(destination_path):
                            shutil.rmtree(destination_path)
                        shutil.copytree(source_path, destination_path)
                    else:
                        shutil.copy2(source_path, destination_path)
                shutil.rmtree(temp_dir)
                print("✅ Architecture successfully updated! Rebooting system...")
                os.execv(sys.executable, ['python'] + sys.argv)
        else:
            print("☁️ System is already up to date or cloud is unreachable.")
    except Exception as e:
        print(f"⚠️ Pipeline Error: {str(e)}")

def main_loop():
    detector = freeze_detector.FreezeDetector()
    local_ip = get_local_ip()
    
    print("\n=============================================================")
    print(" 🚀 OMNISIGHT AI CORE OPERATIONAL // GENERALIST GAME ENGINE")
    print("=============================================================")
    print(f" -> Dashboard link on THIS PC: http://localhost:5000")
    print(f" -> Open on SMARTPHONE or TABLET: http://{local_ip}:5000")
    print("=============================================================\n")

    while True:
        active_game = ui_server.get_selected_game()
        window, source_name = window_grabber.find_active_game_window(active_game)
        
        if not window:
            ui_server.update_ui_data("Awaiting game client...", "None", f"Launch stream window or game client for profile: {active_game.upper()}")
            time.sleep(1.5)
            continue

        frame = window_grabber.capture_window_frame(window)
        if frame is not None:
            if detector.is_frozen(frame):
                print(f"[⚙] 1-Second Grid Freeze Locked on [{active_game.upper()}]. Querying brain...")
                ui_server.update_ui_data("Processing...", source_name, "Scanning structural stat values using Gemini...")
                
                cropped_img = crop_screen_by_game_rules(frame, active_game)
                active_prompt = GAME_PROMPTS.get(active_game, GAME_PROMPTS["division2"])
                
                intel_output = gemini_client.analyze_gear_card(cropped_img, active_prompt)
                ui_server.update_ui_data("System Synchronized", source_name, intel_output)
                
        time.sleep(0.2)

if __name__ == "__main__":
    # ⚠️ The auto-updater is paused below with a hashtag so your manual file edits don't get overwritten!
    # execute_dynamic_updater()
    
    ui_server.UI_DATA["local_ip"] = get_local_ip()
    threading.Thread(target=ui_server.start_server, daemon=True).start()

    # --- 1. CHECK CLOUD TOGGLES & UPDATES ---
    current_config = cloud_config.fetch_cloud_config()
    cloud_config.check_for_updates(current_config, current_version=LOCAL_VERSION)

    # --- 2. BOOT THE CAPTURE ENGINE ---
    if current_config.get("enable_pc_capture", True):
        omni_capture_engine.initialize_pc_capture(target_fps=60)
    else:
        print("[OMNI-ENGINE] PC Capture is disabled via Cloud Config.")
        
    # --- 3. START MAIN APPLICATION LOOP ---
    main_loop()