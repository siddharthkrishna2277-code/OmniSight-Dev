import os
import cv2
from google import genai
from google.genai import types

def analyze_gear_card(image_frame, prompt_instruction):
    """Connects to the Gemini API securely using the user's local environmental variable."""
    # This grabs your secure, private API key from your Windows settings later
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        return "⚠️ Setup Error: GEMINI_API_KEY environment variable not found on this laptop."

    try:
        # Compresses the raw screen pixels into a lightweight JPEG package for fast uploading
        _, buffer = cv2.imencode('.jpg', image_frame)
        image_bytes = buffer.tobytes()

        # Boots up the Google GenAI connection client
        client = genai.Client(api_key=api_key)
        
        # Fires the compressed screen slice + your custom gaming rules straight up to the model
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=[
                types.Part.from_bytes(data=image_bytes, mime_type='image/jpeg'),
                prompt_instruction
            ]
        )
        return response.text
    except Exception as e:
        return f"⚠️ API Connection Issue: {str(e)}"