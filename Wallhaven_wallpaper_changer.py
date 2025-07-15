import os
import sys
import time
import ctypes
import threading
import logging
import requests
from urllib.parse import urlencode
from pathlib import Path

from PIL import Image
import pystray
from pystray import MenuItem as item

import winshell
from win32com.client import Dispatch
from tkinter import Tk, Label, Button, StringVar, OptionMenu

# Setup logging
logging.basicConfig(filename='wallpaper_changer.log', level=logging.DEBUG)

API_URL = "https://wallhaven.cc/api/v1/search"
SAVE_DIR = Path.home() / "Wallpapers"
SAVE_DIR.mkdir(exist_ok=True)

INTERVAL_OPTIONS = {
    "1 Minute": 60,
    "10 Minutes": 600,
    "1 Hour": 3600,
    "8 Hours": 28800,
    "24 Hours": 86400
}

running = False
category = "sfw"
interval_seconds = 600
icon = None
used_wallpapers = set()

def fetch_wallpaper_url():
    purity = "100" if category == "sfw" else "010"
    params = {
        "purity": purity,
        "sorting": "random",
        "topRange": "1M",
        "order": "desc",
        "atleast": "1920x1080",
        "page": 1
    }
    try:
        response = requests.get(f"{API_URL}?{urlencode(params)}", timeout=10)
        data = response.json()
        for wall in data.get('data', []):
            url = wall['path']
            if url.endswith(".jpg") or url.endswith(".png"):
                if url not in used_wallpapers:
                    used_wallpapers.add(url)
                    return url
    except Exception as e:
        logging.error("Error fetching wallpaper", exc_info=True)
    return None

def download_wallpaper(url):
    filename = url.split("/")[-1]
    path = SAVE_DIR / filename
    if not path.exists():
        try:
            r = requests.get(url, stream=True, timeout=20)
            with open(path, 'wb') as f:
                for chunk in r.iter_content(1024):
                    f.write(chunk)
        except Exception as e:
            logging.error("Download failed", exc_info=True)
            return None
    return path

def set_wallpaper(path):
    try:
        ctypes.windll.user32.SystemParametersInfoW(20, 0, str(path), 3)
    except Exception as e:
        logging.error("Failed to set wallpaper", exc_info=True)

def add_to_startup():
    try:
        startup = winshell.startup()
        shortcut_path = os.path.join(startup, "WallpaperChanger.lnk")
        target = sys.executable if getattr(sys, 'frozen', False) else os.path.abspath(__file__)

        if not os.path.exists(shortcut_path):
            shell = Dispatch('WScript.Shell')
            shortcut = shell.CreateShortCut(shortcut_path)
            shortcut.Targetpath = target
            shortcut.WorkingDirectory = os.path.dirname(target)
            shortcut.IconLocation = target
            shortcut.save()
    except Exception as e:
        logging.error("Failed to add to startup", exc_info=True)

def wallpaper_loop():
    global running
    while running:
        url = fetch_wallpaper_url()
        if url:
            path = download_wallpaper(url)
            if path:
                set_wallpaper(path)
        time.sleep(interval_seconds)

def skip_wallpaper(icon=None, item=None):
    logging.info("Manual skip requested.")
    url = fetch_wallpaper_url()
    if url:
        path = download_wallpaper(url)
        if path:
            set_wallpaper(path)

def on_quit(icon, item):
    global running
    running = False
    icon.stop()

def create_tray():
    global icon
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    icon_path = os.path.join(base_path, "icon.png")

    if not os.path.exists(icon_path):
        logging.warning(f"icon.png not found at: {icon_path}")
        return

    image = Image.open(icon_path)
    menu = (
        item('Skip Wallpaper', skip_wallpaper),
        item('Quit', on_quit)
    )
    icon = pystray.Icon("WallpaperChanger", image, "Wallpaper Changer", menu)
    icon.run()

def start_app_loop():
    global running
    running = True
    threading.Thread(target=wallpaper_loop, daemon=True).start()
    create_tray()

def open_gui():
    def start():
        global category, interval_seconds
        category = "sfw" if cat_var.get() == "SFW" else "nsfw"
        interval_seconds = INTERVAL_OPTIONS[interval_var.get()]
        root.destroy()
        add_to_startup()
        start_app_loop()

    root = Tk()
    icon_path = os.path.join(getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__))), "icon.ico")
    if os.path.exists(icon_path):
        root.iconbitmap(icon_path)

    root.title("Wallhaven Wallpaper Changer")
    root.geometry("300x200")
    root.resizable(False, False)

    # Center the window
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x = int((screen_width / 2) - (300 / 2))
    y = int((screen_height / 2) - (200 / 2))
    root.geometry(f"300x200+{x}+{y}")

    # Styling
    label_font = ("Helvetica", 11)
    dropdown_font = ("Helvetica", 10)

    Label(root, text="Choose Category:", font=label_font).pack(pady=(15, 5))
    cat_var = StringVar(root)
    cat_var.set("SFW")
    OptionMenu(root, cat_var, "SFW", "NSFW").pack()

    Label(root, text="Change Interval:", font=label_font).pack(pady=(10, 5))
    interval_var = StringVar(root)
    interval_var.set("10 Minutes")
    OptionMenu(root, interval_var, *INTERVAL_OPTIONS.keys()).pack()

    Button(root, text="Start", font=("Helvetica", 12, "bold"), command=start).pack(pady=15)

    root.mainloop()


if __name__ == "__main__":
    open_gui()
