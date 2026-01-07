import mss
import mss.tools
import numpy as np
import cv2

class ScreenCapturer:
    def __init__(self):
        self.sct = mss.mss()

    def capture_roi(self, roi):
        """
        roi: dict with {'top', 'left', 'width', 'height'}
        Returns: numpy array (BGR)
        """
        screenshot = self.sct.grab(roi)
        img = np.array(screenshot)
        return cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)

    def get_monitors(self):
        return self.sct.monitors
