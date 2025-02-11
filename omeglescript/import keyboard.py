import pygetwindow as gw
import pyautogui
import keyboard
import time

BROWSER_TITLE = "Opera"

def send_key(key):
    windows = gw.getWindowsWithTitle(BROWSER_TITLE)
    if windows:
        win = windows[0]
        win.activate()
        time.sleep(0.1)
        pyautogui.press(key)

while True:
    if keyboard.is_pressed("f13"):
        send_key("esc")
    elif keyboard.is_pressed("f14"):
        send_key("f5")
    time.sleep(0.1)
