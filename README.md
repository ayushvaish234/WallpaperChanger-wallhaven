# WallpaperChanger-Wallhaven 

**Wallhaven Wallpaper Changer** is a lightweight Windows utility that automatically fetches high-quality wallpapers from [wallhaven.cc](https://wallhaven.cc) and sets them as your desktop background at a custom interval.

🔗 **Download the latest release:**  
[wallhaven-wallpaper-changer v1.0](https://github.com/ayushvaish234/wallhaven-wallpaper-changer/releases/tag/v1.0)

## Features

- Automatically changes your wallpaper at a selected time interval
- Choose between SFW and NSFW content
- Avoids repeating wallpapers
- Runs silently in system tray with tray menu options
- Starts automatically with Windows

## How to Use

1. **Download the EXE** from the [releases page](https://github.com/ayushvaish234/wallhaven-wallpaper-changer/releases).
2. Run the `.exe` file.
3. A small window will appear:
   - Select **category**: `SFW` or `NSFW`
   - Select **interval** for changing wallpapers
   - Click **Start**
4. The app will minimize to the system tray and run in the background.
5. Right-click the tray icon to:
   - Skip to next wallpaper manually
   - Quit the app

## Requirements

- Windows 10/11
- Internet connection

## How It Works

- Uses Wallhaven API to fetch high-quality wallpapers based on selected filters
- Downloads them to your `user-name/Wallpapers` folder
- Applies them using Windows API (`SystemParametersInfoW`)
- Uses `pystray` and `tkinter` for GUI and tray functionality
- Adds itself to startup using a Windows shortcut

## License

This project is licensed under the **Attribution License** — You may use and modify the code, but please credit the author: [Ayush Vaish](https://github.com/ayushvaish234).
