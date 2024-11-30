import pytz
from datetime import datetime, timedelta
import tkinter as tk
import pystray
from pystray import MenuItem as item
from PIL import Image, ImageDraw
from plyer import notification
import json
import os
import sys

tray_icon = None
time_remaining_tooltip = "Time remaining: Unknown"
settings = {
    "minimize_to_tray": False,
    "notification_text": "It's 4:20 somewhere!",
    "run_on_startup": False
}

next_420_info = {}
documents_folder = os.path.join(os.getenv('USERPROFILE') or os.getenv('HOME'), 'Documents')
app_subfolder = os.path.join(documents_folder, "420Finder")
os.makedirs(app_subfolder, exist_ok=True)
settings_file = os.path.join(app_subfolder, "settings.json")

def load_settings():
    global settings
    if os.path.exists(settings_file):
        with open(settings_file, "r") as f:
            settings.update(json.load(f))

def save_settings():
    with open(settings_file, "w") as f:
        json.dump(settings, f)

def get_next_420():
    global next_420_info
    now = datetime.now(pytz.utc)
    local_tz = datetime.now().astimezone().tzinfo
    min_time_until = None
    next_420_info = {}
    for tz_name in pytz.all_timezones:
        timezone = pytz.timezone(tz_name)
        localized_now = now.astimezone(timezone)

        if localized_now.hour < 4 or (localized_now.hour == 4 and localized_now.minute < 20):
            next_420_time = localized_now.replace(hour=4, minute=20, second=0, microsecond=0)
        elif localized_now.hour < 16 or (localized_now.hour == 16 and localized_now.minute < 20):
            next_420_time = localized_now.replace(hour=16, minute=20, second=0, microsecond=0)
        else:
            next_day = localized_now + timedelta(days=1)
            next_420_time = next_day.replace(hour=4, minute=20, second=0, microsecond=0)

        next_420_time_utc = next_420_time.astimezone(pytz.utc)
        time_until_utc = next_420_time_utc - now
        total_seconds_utc = int(time_until_utc.total_seconds())

        if total_seconds_utc < 0:
            continue

        if min_time_until is None or total_seconds_utc < min_time_until:
            min_time_until = total_seconds_utc
            local_time = next_420_time.astimezone(local_tz)

            next_420_info = {
                'next_420_time_utc': next_420_time_utc,
                'next_420': next_420_time.strftime("%I:%M %p %Z"),
                'timezone': tz_name,
                'local_time': local_time.strftime("%I:%M %p %Z"),
            }

    return next_420_info

def update_info():
    global tray_icon, time_remaining_tooltip, next_420_info, holding_420_text

    if not next_420_info:
        get_next_420()

    now = datetime.now(pytz.utc)
    time_until = next_420_info['next_420_time_utc'] - now
    total_seconds = int(time_until.total_seconds())

    if total_seconds >= 0:
        hours, remainder = divmod(total_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        if hours > 0:
            time_remaining_str = f"{hours}h {minutes}m {seconds}s"
        elif minutes > 0:
            time_remaining_str = f"{minutes}m {seconds}s"
        else:
            time_remaining_str = f"{seconds}s"

        label_var.set(f"The next 4:20 is in {next_420_info['timezone']} at {next_420_info['next_420']}\n"
                      f"Local time: {next_420_info['local_time']}\n"
                      f"Time remaining: {time_remaining_str}")

        time_remaining_tooltip = f"Time remaining: {time_remaining_str}"
    else:
        label_var.set("It's 4:20 now!")
        time_remaining_tooltip = "Time remaining: Now"
        notify_420()
        root.after(15000, get_next_420())

    if tray_icon:
        tray_icon.title = time_remaining_tooltip
    root.after(1000, update_info)

def notify_420():
    notification_text = settings.get("notification_text", "It's 4:20 somewhere!")
    notification.notify(
        title="It's 4:20!",
        message=notification_text,
        app_name="420 Finder",
        timeout=10  # Notification disappears after 10 seconds
    )

def minimize_to_tray():
    if settings["minimize_to_tray"]:
        root.withdraw()
        global tray_icon
        tray_icon = create_tray_icon()
        tray_icon.run_detached()
    else:
        root.destroy()

def restore_window(icon, item):
    icon.stop()
    global tray_icon
    tray_icon = None
    root.after(0, root.deiconify)

def quit_app(icon, item):
    icon.stop()
    global tray_icon
    tray_icon = None
    root.after(0, root.destroy)

def toggle_minimize_to_tray():
    settings["minimize_to_tray"] = not settings["minimize_to_tray"]
    toggle_button_var.set(f"Minimize to Tray: {'Enabled' if settings['minimize_to_tray'] else 'Disabled'}")
    save_settings()

def open_settings_window():
    settings_window = tk.Toplevel(root)
    settings_window.title("Settings")
    settings_window.geometry("300x200")
    settings_window.resizable(False, False)

    tk.Label(settings_window, text="Notification Text:").pack(pady=5)
    notif_text_var = tk.StringVar(value=settings.get("notification_text", "It's 4:20 somewhere!"))
    notif_entry = tk.Entry(settings_window, textvariable=notif_text_var, width=40)
    notif_entry.pack()

    run_on_startup_var = tk.BooleanVar(value=settings.get("run_on_startup", False))
    run_on_startup_check = tk.Checkbutton(settings_window, text="Run on System Startup", variable=run_on_startup_var)
    run_on_startup_check.pack(pady=5)

    # Add a note about potential app blocking
    tk.Label(settings_window, text="Note: Enabling startup may cause\nWindows to block the app.", fg="red").pack(pady=5)

    def save_and_close():
        settings["notification_text"] = notif_text_var.get()
        settings["run_on_startup"] = run_on_startup_var.get()
        save_settings()
        handle_startup()
        settings_window.destroy()

    tk.Button(settings_window, text="Save", command=save_and_close).pack(pady=10)


def handle_startup():
    startup_folder = os.path.join(os.getenv('APPDATA'), 'Microsoft', 'Windows', 'Start Menu', 'Programs', 'Startup')
    shortcut_path = os.path.join(startup_folder, 'Next420Finder.lnk')
    if settings["run_on_startup"]:
        create_startup_shortcut(shortcut_path)
    else:
        if os.path.exists(shortcut_path):
            os.remove(shortcut_path)

def create_startup_shortcut(shortcut_path):
    from win32com.client import Dispatch

    python_executable = sys.executable
    script_path = os.path.abspath(__file__)

    shell = Dispatch('WScript.Shell')
    shortcut = shell.CreateShortCut(shortcut_path)
    shortcut.Targetpath = python_executable
    shortcut.Arguments = f'"{script_path}"'
    shortcut.WorkingDirectory = os.getcwd()
    shortcut.IconLocation = python_executable
    shortcut.save()

def create_tray_icon():
    icon_image = Image.new("RGB", (64, 64), "black")
    draw = ImageDraw.Draw(icon_image)
    draw.rectangle((16, 16, 48, 48), fill="green")
    menu = pystray.Menu(
        item("Restore", restore_window),
        item("Quit", quit_app)
    )
    return pystray.Icon("Next420Finder", icon_image, time_remaining_tooltip, menu)

load_settings()
handle_startup()

root = tk.Tk()
root.title("Next 4:20 Finder")
root.geometry("320x125")
root.resizable(False, False)
root.protocol("WM_DELETE_WINDOW", minimize_to_tray)
label_var = tk.StringVar()
label = tk.Label(root, textvariable=label_var, wraplength=300, justify="left")
label.pack(pady=10)
buttons_frame = tk.Frame(root)
buttons_frame.pack(pady=10)
toggle_button_var = tk.StringVar(value=f"Minimize to Tray: {'Enabled' if settings['minimize_to_tray'] else 'Disabled'}")
toggle_button = tk.Button(buttons_frame, textvariable=toggle_button_var, command=toggle_minimize_to_tray)
toggle_button.grid(row=0, column=0, padx=5)
settings_button = tk.Button(buttons_frame, text="Settings", command=open_settings_window)
settings_button.grid(row=0, column=1, padx=5)

get_next_420()
update_info()
root.mainloop()
