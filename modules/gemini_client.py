import os
import cv2
import base64
import requests

# Copilot Hardening: Remove hardcoded keys. Fall back to environment variable.
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "YOUR_FALLBACK_ENV_KEY")
GEMINI_MODEL = "gemini-1.5-flash"
GEMINI_ENDPOINT = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent"

def encode_image_to_base64(cv2_image):
    """Converts an OpenCV image buffer into a base64 string for API transmission."""
    try:
        if cv2_image is None:
            return None
        _, buffer = cv2.imencode('.jpg', cv2_image)
        return base64.b64encode(buffer).decode('utf-8')
    except Exception as e:
        print(f"[GEMINI-CLIENT] ⚠️ Frame encoding anomaly: {str(e)}")
        return None

def analyze_gear_card(image_frame, game_prompt):
    """Sends the cropped screenshot to Gemini with explicit timeouts to prevent thread locking."""
    if GEMINI_API_KEY == "YOUR_FALLBACK_ENV_KEY" or not GEMINI_API_KEY:
        return "⚠️ [GEMINI] Configuration Error: GEMINI_API_KEY environment variable is missing."

    base64_image = encode_image_to_base64(image_frame)
    if not base64_image:
        return "⚠️ [GEMINI] Analysis Bypassed: Failed to process local video frame buffer."

    # Constructing standard structural payload
    payload = {
        "contents": [
            {
                "parts": [
                    {"text": game_prompt},
                    {
                        "inlineData": {
                            "mimeType": "image/jpeg",
                            "data": base64_image
                        }
                    }
                ]
            }
        ]
    }

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {GEMINI_API_KEY}"
    }

    try:
        # Copilot Hardening: Enforce 3.5s connection threshold and 15s maximum read timeout
        response = requests.post(
            GEMINI_ENDPOINT, 
            json=payload, 
            headers=headers, 
            timeout=(3.5, 15.0)
        )
        response.raise_for_status()
        
        # Parse output safely
        response_data = response.json()
        intel_text = response_data['candidates'][0]['content']['parts'][0]['text']
        return intel_text.strip()

    except requests.exceptions.Timeout:
        print("[GEMINI-CLIENT] ⚠️ API request timed out. Main engine thread preserved.")
        return "⏳ [SYSTEM] Tactical Analysis delayed: Cloud link timed out under heavy load."
         
    except requests.exceptions.RequestException as e:
        print(f"[GEMINI-CLIENT] ⚠️ Network transmission failure: {str(e)}")
        return "⚠️ [SYSTEM] Synchronization offline: Unable to reach AI core analytics server."
         
    except (KeyError, IndexError) as e:
        print(f"[GEMINI-CLIENT] ⚠️ Parsing error on incoming payload structure: {str(e)}")
        return "⚠️ [SYSTEM] Diagnostics alert: Received malformed analytics data from host server."