import tkinter as tk
from tkinter import messagebox
import pyperclip
import pyautogui
import numpy as np
import cv2

# Dark theme colors
BG_COLOR = "#1e1e1e"
ENTRY_BG = "#2d2d2d"
ENTRY_FG = "#ffffff"
LABEL_FG = "#d4d4d4"
BUTTON_BG = "#3a3a3a"
BUTTON_FG = "#ffffff"
BUTTON_ACTIVE_BG = "#505050"

def preview_region(x, y, w, h):
    try:
        region = (int(x), int(y), int(w), int(h))
        screenshot = pyautogui.screenshot(region=region)
        img = np.array(screenshot)
        cv2.imshow("Subtitle Region", img)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
    except Exception as e:
        messagebox.showerror("Error", f"Failed to preview region:\n{e}")

def copy_region(x, y, w, h):
    coords = f"({x}, {y}, {w}, {h})"
    pyperclip.copy(coords)
    messagebox.showinfo("Copied", f"Copied to clipboard:\n{coords}")

def launch_gui():
    root = tk.Tk()
    root.title("Subtitle Region Tool (Dark)")
    root.geometry("210x190")
    root.configure(bg=BG_COLOR)
    root.resizable(False, False)

    fields = ['X', 'Y', 'Width', 'Height']
    entries = {}

    for i, field in enumerate(fields):
        tk.Label(
            root, text=f"{field}:", bg=BG_COLOR, fg=LABEL_FG, anchor='e'
        ).grid(row=i, column=0, padx=10, pady=5, sticky='e')

        entry = tk.Entry(root, width=15, bg=ENTRY_BG, fg=ENTRY_FG, insertbackground=ENTRY_FG)
        entry.insert(0, '0')
        entry.grid(row=i, column=1, padx=10, pady=5)
        entries[field.lower()] = entry

    def on_preview():
        preview_region(
            entries['x'].get(),
            entries['y'].get(),
            entries['width'].get(),
            entries['height'].get()
        )

    def on_copy():
        copy_region(
            entries['x'].get(),
            entries['y'].get(),
            entries['width'].get(),
            entries['height'].get()
        )

    # Buttons
    preview_btn = tk.Button(
        root, text="Preview", command=on_preview,
        bg=BUTTON_BG, fg=BUTTON_FG, activebackground=BUTTON_ACTIVE_BG, width=12
    )
    preview_btn.grid(row=5, column=0, pady=20)

    copy_btn = tk.Button(
        root, text="Copy", command=on_copy,
        bg=BUTTON_BG, fg=BUTTON_FG, activebackground=BUTTON_ACTIVE_BG, width=12
    )
    copy_btn.grid(row=5, column=1, pady=20)

    root.mainloop()

if __name__ == "__main__":
    launch_gui()
