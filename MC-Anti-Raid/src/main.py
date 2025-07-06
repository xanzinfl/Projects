import os
import json
import threading
import time
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import pyautogui
import pytesseract
import requests
import pygame

# Init pygame
pygame.mixer.init()

# Constants
DOCUMENTS_PATH = os.path.join(os.path.expanduser("~"), "Documents", "MCAnti-Raid")
CONFIG_PATH = os.path.join(DOCUMENTS_PATH, "config.json")
DEFAULT_SOUND_PATH = os.path.join(DOCUMENTS_PATH, "alert.mp3")
SOURCE_SOUND_PATH = os.path.join("alert.mp3")

# Default config
default_config = {
    "sound_enabled": True,
    "refresh_rate": 1.0,
    "keywords": ["block broken", "broken", "player hurts"],
    "sound_path": DEFAULT_SOUND_PATH,
    "webhook_url": "https://discord.com/api/webhooks/your-webhook-here",
    "ocr_region": [2220, 1100, 340, 350]
}

# Ensure config and default sound exist
def ensure_defaults():
    os.makedirs(DOCUMENTS_PATH, exist_ok=True)
    if not os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, 'w') as f:
            json.dump(default_config, f, indent=4)
    if not os.path.exists(DEFAULT_SOUND_PATH):
        try:
            with open(SOURCE_SOUND_PATH, 'rb') as src, open(DEFAULT_SOUND_PATH, 'wb') as dst:
                dst.write(src.read())
        except Exception as e:
            print(f"[ERROR] Could not copy default sound: {e}")

# Load config
def load_config():
    with open(CONFIG_PATH, 'r') as f:
        return json.load(f)

# Save config
def save_config(cfg):
    with open(CONFIG_PATH, 'w') as f:
        json.dump(cfg, f, indent=4)

# OCR detection logic
def check_for_subtitle(keywords, region):
    screenshot = pyautogui.screenshot(region=tuple(region))
    text = pytesseract.image_to_string(screenshot)  
    for keyword in keywords:
        if keyword.lower() in text.lower():
            return text.strip()
    return None

def send_webhook(webhook_url):
    requests.post(webhook_url, json={"content": "@everyone 👱️ Theres someone breaking in!"})

# GUI app class
class SubtitleDetectorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("MC Anti-Raid")
        self.config = load_config()
        self.running = False
        self.last_sent_time = 0
        self.alert_sound = None

        self.root.configure(bg="#1e1e1e")
        self.fg_color = "#ffffff"
        self.bg_color = "#1e1e1e"
        self.entry_bg = "#2d2d2d"
        self.button_bg = "#3c3f41"

        style_args = {"bg": self.bg_color, "fg": self.fg_color}
        entry_args = {"bg": self.entry_bg, "fg": self.fg_color, "insertbackground": self.fg_color}
        button_args = {"bg": self.button_bg, "fg": self.fg_color, "activebackground": self.fg_color, "activeforeground": self.bg_color}

        # GUI
        self.sound_var = tk.BooleanVar(value=self.config["sound_enabled"])
        self.refresh_var = tk.DoubleVar(value=self.config["refresh_rate"])
        self.sound_path_var = tk.StringVar(value=self.config["sound_path"])
        self.webhook_var = tk.StringVar(value=self.config["webhook_url"])
        self.region_var = tk.StringVar(value=", ".join(map(str, self.config["ocr_region"])))

        tk.Checkbutton(root, text="Enable Sound", variable=self.sound_var, **style_args, selectcolor=self.bg_color).grid(row=0, column=0, sticky="w")

        tk.Label(root, text="Refresh Rate (s):", **style_args).grid(row=1, column=0, sticky="w")
        tk.Entry(root, textvariable=self.refresh_var, width=10, **entry_args).grid(row=1, column=1)

        tk.Label(root, text="Alert Sound Path:", **style_args).grid(row=2, column=0, sticky="w")
        tk.Entry(root, textvariable=self.sound_path_var, width=40, **entry_args).grid(row=2, column=1)
        tk.Button(root, text="Browse", command=self.browse_sound, **button_args).grid(row=2, column=2)

        tk.Label(root, text="Discord Webhook URL:", **style_args).grid(row=3, column=0, sticky="w")
        tk.Entry(root, textvariable=self.webhook_var, width=60, **entry_args).grid(row=3, column=1, columnspan=2)

        tk.Label(root, text="OCR Region (x, y, w, h):", **style_args).grid(row=4, column=0, sticky="w")
        tk.Entry(root, textvariable=self.region_var, width=40, **entry_args).grid(row=4, column=1, columnspan=2)

        tk.Label(root, text="Detection Phrases (one per line):", **style_args).grid(row=5, column=0, columnspan=2, sticky="w")
        self.keyword_text = scrolledtext.ScrolledText(root, width=40, height=6, bg=self.entry_bg, fg=self.fg_color, insertbackground=self.fg_color)
        self.keyword_text.grid(row=6, column=0, columnspan=3)
        self.keyword_text.insert(tk.END, "\n".join(self.config["keywords"]))

        self.log_box = scrolledtext.ScrolledText(root, width=60, height=10, state="disabled", bg=self.entry_bg, fg=self.fg_color)
        self.log_box.grid(row=7, column=0, columnspan=3, pady=(10, 0))

        self.toggle_btn = tk.Button(root, text="Start Detection", command=self.toggle_detection, **button_args)
        self.toggle_btn.grid(row=8, column=0, columnspan=1, pady=10)

        self.save_btn = tk.Button(root, text="Save Config", command=self.save_user_config, **button_args)
        self.save_btn.grid(row=8, column=1, columnspan=3)

        tk.Button(root, text="Stop Sound", command=self.stop_sound, **button_args).grid(row=8, column=2, sticky="e")

    def browse_sound(self):
        path = filedialog.askopenfilename(filetypes=[("Audio Files", "*.wav *.mp3")])
        if path:
            self.sound_path_var.set(path)

    def toggle_detection(self):
        if self.running:
            self.running = False
            self.toggle_btn.config(text="Start Detection")
            self.log("[INFO] Detection Stopped.")
        else:
            self.save_user_config()
            self.running = True
            threading.Thread(target=self.run_detection, daemon=True).start()
            self.toggle_btn.config(text="Stop Detection")
            self.log("[INFO] Detection Started.")

    def stop_sound(self):
        if self.alert_sound:
            self.alert_sound.stop()
            self.log("[INFO] Sound stopped manually.")

    def save_user_config(self):
        self.config["sound_enabled"] = self.sound_var.get()
        self.config["refresh_rate"] = self.refresh_var.get()
        self.config["sound_path"] = self.sound_path_var.get()
        self.config["webhook_url"] = self.webhook_var.get()
        self.config["ocr_region"] = [int(x.strip()) for x in self.region_var.get().split(",") if x.strip().isdigit()]
        self.config["keywords"] = [line.strip() for line in self.keyword_text.get("1.0", tk.END).splitlines() if line.strip()]
        save_config(self.config)
        self.log("[INFO] Configuration saved.")

    def log(self, msg):
        self.log_box.config(state="normal")
        self.log_box.insert(tk.END, msg + "\n")
        self.log_box.yview(tk.END)
        self.log_box.config(state="disabled")

    def run_detection(self):
        if self.config["sound_enabled"]:
            try:
                self.alert_sound = pygame.mixer.Sound(self.config["sound_path"])
            except Exception as e:
                self.log(f"[ERROR] Failed to load sound: {e}")
                self.alert_sound = None
        else:
            self.alert_sound = None

        cooldown = 5
        while self.running:
            result = check_for_subtitle(self.config["keywords"], self.config["ocr_region"])
            if result:
                now = time.time()
                if now - self.last_sent_time > cooldown:
                    send_webhook(self.config["webhook_url"])
                    if self.alert_sound:
                        self.alert_sound.play()
                    self.log(f"[DETECTED] {result}")
                    self.last_sent_time = now
            time.sleep(self.config["refresh_rate"])

# Init
if __name__ == "__main__":
    if not os.path.exists(CONFIG_PATH):
        ensure_defaults()
    root = tk.Tk()
    app = SubtitleDetectorApp(root)
    root.mainloop()