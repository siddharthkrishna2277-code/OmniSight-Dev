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
import subprocess
import webbrowser

# --- OMNISIGHT V1 CORE IMPORTS ---
import cloud_config
from modules import window_grabber, freeze_detector, gemini_client, ui_server, omni_capture_engine

LOCAL_VERSION = "1.0.2"
SECURE_ZIP_URL = "https://github.com/siddharthkrishna2277-code/OmniSight-Dev/archive/refs/heads/main.zip"

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

# --- SECURE CONTAINER AUTO-UPDATER (HARDENED) ---
def execute_secure_updater(zip_url):
    print("\n[OMNI-UPDATE] 📥 Secure Update found! Downloading package...")
    try:
        # Copilot Hardening: Enforce connection timeout (3.0s) and read timeout (30s)
        response = requests.get(zip_url, timeout=(3.0, 30.0))
        response.raise_for_status()
        
        with open("omni_update.zip", "wb") as f:
            f.write(response.content)

        print("[OMNI-UPDATE] 🔄 Prepping staging area...")
        if not os.path.exists("update_staging"):
            os.makedirs("update_staging", exist_ok=True)
            
        with zipfile.ZipFile("omni_update.zip", 'r') as zip_ref:
            zip_ref.extractall("update_staging")

        extracted_folders = os.listdir("update_staging")
        if not extracted_folders:
            raise ValueError("Downloaded update package is empty.")
            
        target_dir = os.path.join("update_staging", extracted_folders[0]) if len(extracted_folders) == 1 else "update_staging"

        bat_script = f"""@echo off
echo [OMNI-UPDATER] Waiting for main process to close safely...
timeout /t 3 /nobreak > NUL
echo [OMNI-UPDATER] Installing new core files...
xcopy /s /y "{target_dir}\\*" .\\ > NUL
echo [OMNI-UPDATER] Cleaning up temporary files...
rmdir /s /q "update_staging"
del omni_update.zip
echo [OMNI-UPDATER] Booting updated OmniSight Engine...
start "" python main.py
del "%~f0"
"""
        with open("install_update.bat", "w") as b:
            b.write(bat_script)

        print("[OMNI-UPDATE] ✅ Download complete! Handing off to local installer...")
        subprocess.Popen("install_update.bat", shell=True)
        sys.exit(0)

    except requests.exceptions.RequestException as e:
        print(f"[OMNI-UPDATE] ⚠️ Network error during download: {str(e)}")
    except (OSError, zipfile.BadZipFile, ValueError) as e:
        print(f"[OMNI-UPDATE] ⚠️ Deployment installation error: {str(e)}")
    except Exception as e:
        print(f"[OMNI-UPDATE] ⚠️ Unexpected pipeline failure: {str(e)}")

def main_loop():
    detector = freeze_detector.FreezeDetector()
    local_ip = get_local_ip()
    
    print("\n=============================================================")
    print(" 🚀 OMNISIGHT AI CORE OPERATIONAL // GENERALIST GAME ENGINE")
    print("=============================================================")
    print(f" -> Dashboard link on THIS PC: http://localhost:5000")
    print(f" -> Open on SMARTPHONE or TABLET: http://{local_ip}:5000")
    print("=============================================================\n")

    # Copilot Hardening: Auto-launch browser cleanly via main loop orchestration
    try:
        webbrowser.open("http://localhost:5000")
    except Exception as e:
        print(f"[⚙] Dashboard UI auto-launch deferred: {str(e)}")

    while True:
        try:
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
        except Exception as e:
            print(f"[⚙] Core iteration anomaly caught: {str(e)}")
            time.sleep(1.0)

if __name__ == "__main__":
    try:
        ui_server.UI_DATA["local_ip"] = get_local_ip()
        threading.Thread(target=ui_server.start_server, daemon=True).start()

        # --- 1. CHECK CLOUD TOGGLES & UPDATES ---
        current_config = cloud_config.fetch_cloud_config()
        needs_update = cloud_config.check_for_updates(current_config, current_version=LOCAL_VERSION)

        if needs_update:
            execute_secure_updater(SECURE_ZIP_URL)

        # --- 2. BOOT THE CAPTURE ENGINE ---
        if current_config.get("enable_pc_capture", True):
            omni_capture_engine.initialize_pc_capture(target_fps=60)
        else:
            print("[OMNI-ENGINE] PC Capture is disabled via Cloud Config.")
            
        # --- 3. START MAIN APPLICATION LOOP ---
        main_loop()
    except KeyboardInterrupt:
        print("\n[SYSTEM] Graceful shutdown executed by user.")
        sys.exit(0)