import pyautogui

class ActionExecutor:
    def __init__(self):
        pyautogui.FAILSAFE = True

    def click_at(self, x, y):
        """
        Clicks at absolute screen coordinates (x, y)
        """
        pyautogui.click(x, y)

    def move_to(self, x, y):
        pyautogui.moveTo(x, y)

    def scroll(self, clicks):
        """
        Scrolls the mouse wheel.
        clicks: int, positive for up, negative for down.
        """
        pyautogui.scroll(clicks)
