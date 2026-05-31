import pygetwindow as gw
import mss
import numpy as np
import cv2

# Global target matrix supporting a massive multi-genre library
GAME_WINDOW_MAP = {
    # Action RPGs & Looters
    "division2": ["PS Remote Play", "Xbox", "The Division 2", "Tom Clancy's The Division 2"],
    "destiny2": ["PS Remote Play", "Xbox", "Destiny 2"],
    "diablo4": ["PS Remote Play", "Xbox", "Diablo IV", "Diablo 4"],
    "pathofexile": ["PS Remote Play", "Xbox", "Path of Exile", "Path of Exile 2", "PoE2"],
    "warframe": ["PS Remote Play", "Xbox", "Warframe"],
    "monsterhunter": ["PS Remote Play", "Xbox", "Monster Hunter: World", "Monster Hunter Wilds", "MHW", "MHW_Wilds"],
    
    # Competitive & Tactical Shooters
    "valorant": ["Valorant"],
    "counterstrike": ["Counter-Strike 2", "CS2", "Counter-Strike: Global Offensive"],
    "apexlegends": ["PS Remote Play", "Xbox", "Apex Legends"],
    "callofduty": ["PS Remote Play", "Xbox", "Call of Duty", "Call of Duty: Warzone", "Call of Duty: Black Ops 6"],
    "helldivers2": ["PS Remote Play", "Xbox", "Helldivers 2", "Helldivers II"],
    
    # MMOs & Open World RPGs
    "worldofwarcraft": ["World of Warcraft", "WoW"],
    "finalfantasy14": ["PS Remote Play", "Xbox", "FINAL FANTASY XIV", "FFXIV"],
    "eldenring": ["PS Remote Play", "Xbox", "Elden Ring"],
    "cyberpunk2077": ["PS Remote Play", "Xbox", "Cyberpunk 2077"],
    "genshinimpact": ["PS Remote Play", "Xbox", "Genshin Impact"],
    
    # Battle Royale & Sandbox
    "fortnite": ["PS Remote Play", "Xbox", "Fortnite"],
    "minecraft": ["Minecraft", "Minecraft Launcher"]
}

def find_active_game_window(selected_game):
    """Dynamically targets the active game window based on your dashboard dropdown selection."""
    targets = GAME_WINDOW_MAP.get(selected_game, ["PS Remote Play", "Xbox"])
    for target in targets:
        windows = gw.getWindowsWithTitle(target)
        if windows and not windows[0].isMinimized:
            return windows[0], target
    return None, None

def capture_window_frame(window):
    """Grabs uncompressed screenshot pixels directly from the targeted window borders."""
    if not window:
        return None
    
    with mss.mss() as sct:
        monitor = {
            "top": window.top,
            "left": window.left,
            "width": window.width,
            "height": window.height
        }
        screenshot = sct.grab(monitor)
        frame = np.array(screenshot)
        frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)
        return frame