# 🕒 TimeBasedBackground

## 📋 Description

TimeBasedBackground is a Windows application that automatically changes your desktop wallpaper based on the time of day. It allows you to set specific images for different time periods, creating a dynamic desktop experience that adapts to your daily schedule. The application runs quietly in the system tray, seamlessly transitioning between wallpapers at the configured times.

## ✨ Features

-   🖼️ Set different wallpapers for specific time ranges throughout the day
-   ⏰ Configure custom time points to define your own schedule
-   🔄 Automatically changes wallpaper at the specified times
-   🏃‍♂️ Runs in the system tray with minimal resource usage
-   🚀 Auto-start with Windows option
-   🛠️ Easy-to-use configuration interface

## 📥 Installation

### Option 1: Using the Executable (Recommended)

1. Download the latest release from the `dist` folder
2. Extract the ZIP file to a location of your choice
3. Run `TimeBasedBackground.exe` to start the application

### Option 2: Running from Source

1. Clone this repository or download the source code
2. Ensure you have Python 3.7+ installed
3. Install the required dependencies:
    ```
    pip install -r requirements.txt
    ```
4. Run the application:
    ```
    python main.py
    ```
    or use the provided batch file:
    ```
    Run.bat
    ```

## 🛠️ Usage

### First-Time Setup

When you run the application for the first time, it will guide you through the setup process:

1. Configure time points - Define when the wallpaper should change throughout the day
2. Set wallpaper images for each time range - Select the image to display during each time period

### Daily Use

After configuration, the application runs in the system tray:

1. Right-click the tray icon to access options:
    - Reconfigure: Change time points and wallpaper assignments
    - Exit: Close the application

The application will automatically:

-   Start with Windows (if configured)
-   Change wallpapers at the specified times
-   Monitor for configuration changes

## 💻 Technology Stack

-   **Language**: Python 3.7+
-   **GUI Framework**: Tkinter
-   **Image Processing**: Pillow (PIL Fork)
-   **System Tray Integration**: pystray
-   **Build Tool**: PyInstaller

## 📁 Project Structure

```
TimeBasedBG/
├── dist/                      # Distribution folder containing executable
│   └── TimeBasedBackground.exe # Compiled executable application
├── main.py                    # Main application script
├── reconfigure.py             # Configuration utility script
├── requirements.txt           # Python dependencies
├── build_exe.spec             # PyInstaller specification file
├── Run.bat                    # Batch file for easy execution
└── README.md                  # Project documentation
```

## 📦 Executable File (.exe) Usage

The `TimeBasedBackground.exe` file in the `dist` folder is a standalone executable created with PyInstaller. This means:

-   ✅ No Python installation required to run it
-   ✅ All dependencies are bundled inside the executable
-   ✅ Can be moved to any location on your Windows system
-   ✅ Can be added to Windows startup for automatic execution on boot

To use the executable:

1. Double-click `TimeBasedBackground.exe` to run the application
2. The app will appear in your system tray (near the clock)
3. Right-click the tray icon to access options

## 🔍 Additional Notes

### System Requirements

-   Windows 10/11
-   Approximately 20MB of disk space

### Tips

-   For best results, use images with the same resolution as your desktop
-   PNG and JPG formats are fully supported
-   Consider using morning, afternoon, evening, and night-themed wallpapers to match the time of day

### Known Issues

-   Time-based transitions happen on the minute mark, not instantly
-   Configuration changes require a restart of the application to take effect

## 🤝 Contributing

Contributions are welcome! Feel free to:

-   Report bugs or request features by creating an issue
-   Submit pull requests with improvements or fixes
-   Share your experience and suggestions

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

Created with ❤️ by [Alireza Sobhanian]
