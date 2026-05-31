import cv2
import numpy as np
import time

class FreezeDetector:
    def __init__(self, threshold=0.99, freeze_duration=1.0):
        self.threshold = threshold
        self.freeze_duration = freeze_duration
        self.last_frame = None
        self.freeze_start_time = None
        self.triggered = False

    def is_frozen(self, current_frame):
        """Monitors structural pixel variations to catch the 1-second item inspection pause."""
        if current_frame is None:
            return False

        gray = cv2.cvtColor(current_frame, cv2.COLOR_BGR2GRAY)
        resized = cv2.resize(gray, (100, 100))

        if self.last_frame is None:
            self.last_frame = resized
            return False

        res = cv2.matchTemplate(resized, self.last_frame, cv2.TM_CCOEFF_NORMED)
        similarity = res[0][0]
        self.last_frame = resized

        if similarity >= self.threshold:
            if self.freeze_start_time is None:
                self.freeze_start_time = time.time()
            elif time.time() - self.freeze_start_time >= self.freeze_duration:
                if not self.triggered:
                    self.triggered = True
                    return True
        else:
            self.freeze_start_time = None
            self.triggered = False

        return False