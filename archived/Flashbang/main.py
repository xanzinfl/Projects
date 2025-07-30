import tkinter as tk
import random
import threading
import time
from screeninfo import get_monitors

FLASH_DURATION = 0.1  # seconds
MIN_INTERVAL = 2      # minimum time between flashes
MAX_INTERVAL = 30    # maximum time between flashes

def flash_on_display(monitor):
    win = tk.Tk()
    win.attributes("-fullscreen", True)
    win.attributes("-topmost", True)
    win.configure(background="white")
    win.geometry(f"{monitor.width}x{monitor.height}+{monitor.x}+{monitor.y}")
    win.after(int(FLASH_DURATION * 1000), win.destroy)
    win.mainloop()

def flashbang_all_displays():
    monitors = get_monitors()
    threads = []
    for monitor in monitors:
        t = threading.Thread(target=flash_on_display, args=(monitor,))
        t.start()
        threads.append(t)
    for t in threads:
        t.join()

def random_flashes():
    while True:
        wait_time = random.uniform(MIN_INTERVAL, MAX_INTERVAL)
        time.sleep(wait_time)
        flashbang_all_displays()

if __name__ == "__main__":
    print("⚠️ Random flashbang app started. Press Ctrl+C to stop.")
    try:
        random_flashes()
    except KeyboardInterrupt:
        print("\nStopped by user.")
