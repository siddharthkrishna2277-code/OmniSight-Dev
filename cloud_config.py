import requests
import json

# --- DYNAMIC CLOUD TOGGLES (THE KILL SWITCH) ---
# Purpose: Connects to your GitHub to read the master remote control file.

# Note: We will replace this URL with your actual raw GitHub link before final launch.
GITHUB_CONFIG_URL = "https://raw.githubusercontent.com/YOUR_USERNAME/Project_OmniSight/main/config.json"

def fetch_cloud_config():
    print("[OMNI-CLOUD] Checking GitHub for latest kill switches and updates...")
    
    # These are the safe default settings in case the user has no Wi-Fi
    local_fallback = {
        "maintenance_mode": False,
        "enable_pc_capture": True,
        "enable_playstation": True,
        "enable_xbox": True,
        "app_version": "1.0.0"
    }

    try:
        # Attempt to fetch the live config from your GitHub with a strict 3-second timeout
        response = requests.get(GITHUB_CONFIG_URL, timeout=3)
        
        if response.status_code == 200:
            print("[OMNI-CLOUD] Cloud config successfully synced.")
            return response.json()
        else:
            print("[OMNI-CLOUD] Warning: Cloud config unreachable. Using local defaults.")
            return local_fallback
            
    except Exception as e:
        print(f"[OMNI-CLOUD] Network offline or GitHub blocked. Using local defaults.")
        return local_fallback

def check_for_updates(cloud_config, current_version="1.0.0"):
    # Reads the app_version from GitHub and compares it to the local app
    latest_version = cloud_config.get("app_version", current_version)
    
    if latest_version != current_version:
        print(f"\n[OMNI-UPDATE] 🚨 A new mandatory patch (Version {latest_version}) is available!")
        print("[OMNI-UPDATE] Please download the latest update from GitHub.\n")
        return True
        
    return False