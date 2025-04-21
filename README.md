# 🌓 TimeBasedBackground

<div align="center">
  
  ![Python](https://img.shields.io/badge/Python-3.8+-blue.svg?logo=python&logoColor=white)
  ![Pillow](https://img.shields.io/badge/Pillow-8.0.0+-yellow.svg?logo=python&logoColor=white)
  ![Pystray](https://img.shields.io/badge/Pystray-0.17.0+-green.svg?logo=python&logoColor=white)
  ![Windows](https://img.shields.io/badge/Platform-Windows-blue.svg?logo=windows&logoColor=white)
  [![License](https://img.shields.io/badge/License-MIT-purple.svg)](LICENSE)
  
</div>

## 📝 Description

TimeBasedBackground is a Windows application that automatically changes your desktop wallpaper based on the time of day. Define custom time ranges and assign specific background images to each time period for a dynamically changing desktop experience that matches your daily routine.

### ✨ Features

-   🕒 **Time-Based Wallpaper Changes**: Automatically switches wallpapers based on custom time periods
-   🔄 **Customizable Time Ranges**: Create and edit your own time points and periods
-   🖼️ **Simple Image Selection**: Easy-to-use interface for associating images with time ranges
-   🚀 **Startup Integration**: Optionally run on Windows startup
-   🔍 **System Tray Operation**: Runs quietly in your system tray with minimal resource usage
-   🛠️ **Reconfiguration Tool**: Easily update your time points and wallpaper selections anytime

## 🚀 Installation

### Option 1: Using the Executable (.exe)

1. Download the latest release from the `dist` folder:

    - `TimeBasedBackground.exe`

2. Place the executable in a permanent location on your computer.

3. Double-click the executable to run the application.

4. The first time you run the application, you'll be prompted to set up your time points and wallpaper images.

### Option 2: Running from Source

1. Clone this repository:

    ```bash
    git clone https://github.com/yourusername/TimeBasedBackground.git
    cd TimeBasedBackground
    ```

2. Ensure you have Python 3.8+ installed on your system.

3. Install required dependencies:

    ```bash
    pip install -r requirements.txt
    ```

4. Run the application using the provided batch file:

    ```bash
    Run.bat
    ```

    Or run directly with Python:

    ```bash
    python main.py
    ```

## 💻 Usage

1. **Initial Setup**:

    - The first time you run the application, you'll be guided through setting up your time points.
    - Define specific time points throughout the day (e.g., 8:30, 12:30, 18:00, 23:00).
    - For each time range (between two time points), select a wallpaper image.

2. **System Tray Operation**:

    - After setup, the application runs in your system tray (look for the clock icon).
    - Right-click the tray icon to access these options:
        - **Reconfigure**: Change your time points and wallpaper selections
        - **Exit**: Close the application

3. **Automatic Background Changes**:
    - The application will automatically change your desktop wallpaper when the current time enters a new defined time range.
4. **Reconfiguring**:
    - You can reconfigure your time points and wallpaper selections at any time by:
        - Right-clicking the system tray icon and selecting "Reconfigure"
        - Or running the `reconfigure.py` script directly

## 🔧 Technology Stack

-   **Python 3.8+**: Core programming language
-   **Tkinter**: GUI framework for the configuration interfaces
-   **Pillow (PIL)**: Image processing library
-   **Pystray**: System tray icon functionality
-   **PyInstaller**: Used to create standalone Windows executable

## 📂 Project Structure

```
TimeBasedBackground/
│
├── main.py                   # Main application code
├── reconfigure.py            # Tool for reconfiguring time points and wallpapers
├── requirements.txt          # Python dependencies
├── build_exe.spec            # PyInstaller specification file
├── Run.bat                   # Batch file to run the application from source
│
└── dist/                     # Distribution folder containing executable
    └── TimeBasedBackground.exe  # Standalone Windows executable
```

## 📦 Executable (.exe) File Usage

The `TimeBasedBackground.exe` file in the `dist` directory is a standalone Windows executable created with PyInstaller. This executable includes all necessary dependencies and can be run on any Windows system without requiring Python to be installed.

### Features of the Executable:

-   **Self-contained**: Includes all required Python libraries and dependencies
-   **Portable**: Can be moved to any location on your computer
-   **No installation required**: Simply double-click to run
-   **Automatic configuration**: Creates configuration files in the same directory as the executable
-   **System tray integration**: Runs in the background with a tray icon

### Notes:

-   When first run, the executable may trigger Windows security warnings as it's not signed. This is normal and you can safely allow it to run.
-   Configuration files (`images_config.json` and `time_points_config.json`) will be created in the same directory as the executable.

## 📋 Additional Notes

### Requirements:

-   Windows operating system (tested on Windows 10/11)
-   Administrative privileges may be required for startup integration

### Known Limitations:

-   Currently only supports Windows operating systems
-   Image paths are stored as absolute paths, so moving image files will require reconfiguration

### Future Enhancements:

-   Support for multiple monitor configurations
-   Theme-based wallpaper collections
-   Additional customization options for wallpaper display

## 🤝 Contributing

Contributions are welcome! Feel free to submit issues or pull requests.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

<div align="center">
  
  Developed with ❤️ by [Your Name]
  
</div>
