# ⏰ Time-Based Background Changer

[![Python](https://img.shields.io/badge/Python-3.x-blue.svg?style=flat-square&logo=python)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg?style=flat-square)](https://opensource.org/licenses/MIT)

## 📜 Description

Tired of the same static desktop background all day? The **Time-Based Background Changer** is a lightweight and user-friendly application that automatically changes your desktop wallpaper based on the time of day. Simply configure the time points that define your schedule and the corresponding background images for the intervals between these points. The application runs silently in the system tray, providing unobtrusive background updates.

**Key Features:**

  * **Time-Point Based Switching:** Changes wallpaper based on a sequence of user-defined time points.
  * **Customizable Schedules:** Easily add, edit, delete, and sort time points through a graphical interface.
  * **System Tray Integration:** Runs in the system tray, allowing for background operation without cluttering your taskbar.
  * **Intuitive Configuration:** A user-friendly graphical interface (GUI) is provided to configure time points and associate background images for each time interval.
  * **Persistent Configuration:** Your time points and image mappings are saved in `time_points_config.json` and `images_config.json`, respectively, and automatically loaded on startup.
  * **Windows Startup Integration:** Option to automatically start the application when you log in to Windows.
  * **Compiled Executable:** A ready-to-run `.exe` file is available for Windows users, eliminating the need for a Python installation for basic usage.
  * **Logging:** Detailed application logs are saved in `timebased_bg.log` for troubleshooting.

## 🛠️ Installation Instructions

Follow these steps to get the Time-Based Background Changer running on your system:

1.  **Clone the Repository:**

    ```bash
    git clone [https://github.com/YOUR_GITHUB_USERNAME/YOUR_REPOSITORY_NAME.git](https://github.com/YOUR_GITHUB_USERNAME/YOUR_REPOSITORY_NAME.git)
    cd YOUR_REPOSITORY_NAME
    ```

    *(Replace `YOUR_GITHUB_USERNAME` and `YOUR_REPOSITORY_NAME` with your actual GitHub details)*

2.  **Prerequisites (for running from source):**

      * **Python 3.x:** Ensure you have Python 3.x installed on your system. You can download it from [https://www.python.org/downloads/](https://www.python.org/downloads/).
      * **tkinter:** This library should come bundled with standard Python installations. The `Run.bat` script checks for its availability.
      * **Pillow (PIL Fork):** Required for image handling with the system tray icon. Install using pip:
        ```bash
        pip install Pillow
        ```
      * **pystray:** Required for creating the system tray icon. Install using pip:
        ```bash
        pip install pystray
        ```
      * **Dependencies:** Install any other required Python libraries using pip:
        ```bash
        pip install -r requirements.txt
        ```
        *(This step is automatically handled by the `Run.bat` script)*

3.  **Running the Application:**

      * **Using the Executable (`.exe`):**

          * Navigate to the `dist` folder.
          * Double-click the `TimeBasedBackground.exe` file to run the application. The application will start in the system tray.

      * **Running from Source (for development or customization):**

          * Open a terminal or command prompt in the project directory.
          * Run the main script:
            ```bash
            python main.py
            ```
          * Alternatively, you can use the provided `Run.bat` script for a convenient way to check dependencies and run the application:
            ```bash
            .\Run.bat
            ```

## ⚙️ Usage

Once the Time-Based Background Changer is running, it will appear as an icon in your system tray (usually near the clock).

1.  **Initial Configuration:** The first time you run the application, it will guide you through setting up the time points.

      * A window titled **"Initial Setup: Configure Time Points"** will appear.
      * This window allows you to **add**, **edit**, **delete**, and **sort** the time points that will define when your background changes.
      * Enter time points in **HH:MM** format (e.g., 08:00, 12:30, 23:00).
      * Use the **"+ Add Time Point"** button to add more time points.
      * Use the **"🗑️"** button next to each time point to delete it. You need at least two time points.
      * Use the **"Sort Time Points"** button to arrange the time points chronologically.
      * Click **"Save & Continue"** to save the time points and proceed to configure the background images. You can also just **"Save Time Points"** if you want to configure images later via the system tray menu.
      * If you close the time points configuration window without saving, the application will use a set of default time points.

2.  **Configure Background Images:** After setting up the time points, or by selecting **"Reconfigure Backgrounds"** from the system tray menu, a window titled **"Initial Setup: Configure Background Images"** will appear.

      * This window displays a list of time ranges based on the time points you configured. For example, if your time points are 08:00, 12:00, and 17:00, you will see ranges like "08:00 to 12:00", "12:00 to 17:00", and "17:00 to 08:00".
      * For each time range, click the **"Choose Image"** button to select the desired background image from your computer. The path to the selected image will be displayed.
      * Once you have assigned images to all the time ranges, click the **"Save Configuration"** button.
      * To close the configuration window without saving, click the **"Cancel"** button.

3.  **Automatic Background Switching:** Once the configuration is saved, the application will run in the system tray and automatically change your desktop background whenever the current time falls within a configured time interval. The background for the interval is determined by the start and end time points of that interval.

4.  **System Tray Menu:** Right-clicking on the Time-Based Background Changer icon in the system tray provides the following options:

      * **Reconfigure Backgrounds:** Opens the background image configuration window.
      * **Configure Time Points:** Opens the time point configuration window.
      * **Add to Startup:** Adds the application to your Windows startup programs, so it runs automatically when you log in.
      * **Exit:** Closes the Time-Based Background Changer application.

## 💻 Technology Stack

  * **Python:** The primary programming language.
  * **tkinter:** Used for creating the graphical user interface for configuration.
  * **json:** For reading and writing configuration data to files (`images_config.json` and `time_points_config.json`).
  * **os:** For interacting with the operating system, such as file path manipulation.
  * **sys:** For accessing system-specific parameters and functions.
  * **ctypes:** Used for interacting with Windows API to set the desktop wallpaper.
  * **datetime:** For handling time-related operations.
  * **winreg:** For adding the application to Windows startup.
  * **threading:** Used for the background task of checking the time and updating the wallpaper.
  * **logging:** For recording application activity and potential errors.
  * **pystray:** For creating and managing the system tray icon and menu.
  * **PIL (Pillow):** Used for creating a simple icon for the system tray.
  * **tempfile:** Used to create a temporary copy of the image for setting as wallpaper (to handle potential file access issues).
  * **subprocess:** (Although not directly used for wallpaper setting in this script) Often used for interacting with system commands.
  * **traceback:** For printing detailed error information during exceptions.

## 📂 Project Structure

<pre>
TimeBG/
├── dist/                      # Distribution folder containing executable
│   └── TimeBasedBackground.exe # Compiled executable application
├── main.py                    # Main application script (responsible for background changing logic and system tray)
├── reconfigure.py             # Configuration utility script (provides the GUI - based on your description, the GUI logic is now integrated into main.py)
├── requirements.txt           # Python dependencies (lists required libraries)
├── build_exe.spec             # PyInstaller specification file (configuration for creating the .exe)
├── Run.bat                    # Batch file for easy execution (checks Python and runs main.py)
└── README.md                  # Project documentation (this file)
</pre>

## ⚙️ Configuration Files

The application uses two JSON files to store its configuration:

  * **`images_config.json`:** This file stores the mapping between the time ranges (defined by the time points) and the paths to the corresponding background image files.
  * **`time_points_config.json`:** This file stores the user-defined time points that determine the intervals for background changes.

These files are typically located in the same directory as the application (`main.py` or the `TimeBasedBackground.exe`).

## 📦 `dist` Folder and `.exe` File Information

The `dist` folder contains the compiled version of the application, `TimeBasedBackground.exe`. This executable allows Windows users to run the Time-Based Background Changer without needing to have Python installed on their system.

  * **Self-Contained:** The `.exe` file bundles the Python runtime and necessary libraries, making it a standalone application.
  * **System Tray Application:** When executed, `TimeBasedBackground.exe` runs in the background and places an icon in the system tray, providing a non-intrusive experience.
  * **Configuration:** The executable reads and writes the `images_config.json` and `time_points_config.json` files in the same directory (or a related application data directory, depending on how `main.py` is implemented).
  * **Usage:** Double-clicking `TimeBasedBackground.exe` starts the application. Right-clicking the system tray icon provides options to reconfigure the backgrounds, configure time points, add to startup, or exit the application.

## 📝 Additional Notes

  * **Time Point Logic:** The application changes the background at the defined time points. The background displayed between two consecutive time points in your sorted list will be the image you associated with that specific time range during configuration. The last time point in your list will define the end of the last interval, which will then loop back to the first time point for the next interval.
  * **Running from Source vs. Executable:** Running from source (`python main.py`) is useful for development, debugging, or if you want to modify the application's behavior. The executable (`TimeBasedBackground.exe`) provides a convenient way for end-users to use the application without needing a Python environment.
  * **Error Handling:** The application includes basic error handling and logging to the `timebased_bg.log` file, which can be helpful for diagnosing issues.
  * **Future Enhancements (To-Dos):**
      * Add support for different transition effects between background changes.
      * Implement the ability to automatically download and use daily wallpapers from online sources.
      * Provide more advanced scheduling options (e.g., specific days of the week).
      * Allow users to specify a default background if no time range matches the current time.
      * Explore cross-platform compatibility for other operating systems.
  * **Known Issues:** *(If any, list them here)*

-----
