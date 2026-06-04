import cv2
import numpy as np
import time

class FreezeDetector:
    """
    A deterministic state-machine implementation for game frame freeze detection.
    Transitions smoothly through IDLE -> POSSIBLE_FREEZE -> CONFIRMED_FREEZE
    to eliminate rapid UI toggles or micro-stutter glitches.
    """
    def __init__(self, similarity_threshold=0.995, consecutive_frames_required=4, cooldown_duration=3.0):
        # Configuration thresholds
        self.similarity_threshold = similarity_threshold
        self.consecutive_frames_required = consecutive_frames_required
        self.cooldown_duration = cooldown_duration

        # State tracking variables
        self.state = "IDLE"  # Internal states: IDLE, POSSIBLE_FREEZE, CONFIRMED_FREEZE
        self.previous_frame_gray = None
        self.consecutive_frozen_count = 0
        self.last_trigger_time = 0.0

    def is_frozen(self, current_frame):
        """
        Processes the incoming frame through the state machine.
        Returns True ONLY at the exact moment a freeze transitions to CONFIRMED.
        """
        if current_frame is None:
            return False

        # Convert frame to grayscale for performant structural pixel processing
        gray_frame = cv2.cvtColor(current_frame, cv2.COLOR_BGR2GRAY)

        # Baseline check: If this is the first frame, store it and stay IDLE
        if self.previous_frame_gray is None:
            self.previous_frame_gray = gray_frame
            return False

        # Check structural similarity against the prior frame buffer
        res = cv2.matchTemplate(gray_frame, self.previous_frame_gray, cv2.TM_CCOEFF_NORMED)
        _, max_val, _, _ = cv2.minMaxLoc(res)
        
        # Cache current frame for the next check loop
        self.previous_frame_gray = gray_frame
        current_time = time.time()

        # --- STATE MACHINE LOGIC MATRIX ---
        
        # Enforce structural cooldown block immediately after an analysis trigger
        if current_time - self.last_trigger_time < self.cooldown_duration:
            self.state = "IDLE"
            self.consecutive_frozen_count = 0
            return False

        is_pixel_identical = max_val >= self.similarity_threshold

        if self.state == "IDLE":
            if is_pixel_identical:
                self.state = "POSSIBLE_FREEZE"
                self.consecutive_frozen_count = 1
            else:
                self.consecutive_frozen_count = 0

        elif self.state == "POSSIBLE_FREEZE":
            if is_pixel_identical:
                self.consecutive_frozen_count += 1
                if self.consecutive_frozen_count >= self.consecutive_frames_required:
                    self.state = "CONFIRMED_FREEZE"
                    self.last_trigger_time = current_time
                    print(f"[FREEZE-ENGINE] ❄️ Freeze confirmed after {self.consecutive_frozen_count} identical frames.")
                    return True
            else:
                # Frame moved; false alarm, instantly reset back to IDLE
                self.state = "IDLE"
                self.consecutive_frozen_count = 0

        elif self.state == "CONFIRMED_FREEZE":
            if not is_pixel_identical:
                # Screen unfroze, shift back to IDLE state smoothly
                self.state = "IDLE"
                self.consecutive_frozen_count = 0

        return False