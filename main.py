import os
import sys
import time
import json
import ctypes
import datetime
import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
from pathlib import Path
import winreg as reg
import threading
import logging
import pystray
from PIL import Image, ImageDraw
import tempfile
import subprocess
import traceback

# Get application path for both script and frozen exe
def get_application_path():
    if getattr(sys, 'frozen', False):
        # We're running in a bundle (executable)
        return os.path.dirname(sys.executable)
    else:
        # We're running in a normal Python environment
        return os.path.dirname(os.path.abspath(__file__))

# Setup logging
app_path = get_application_path()
log_file = os.path.join(app_path, 'timebased_bg.log')
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename=log_file,
    filemode='a'
)

# Constants
CONFIG_FILE = "images_config.json"
TIME_POINTS_CONFIG_FILE = "time_points_config.json"
CHECK_INTERVAL = 60  # seconds

class TimeBasedBackground:
    def __init__(self):
        self.app_path = get_application_path()
        self.config_path = os.path.join(self.app_path, CONFIG_FILE)
        self.time_points_config_path = os.path.join(self.app_path, TIME_POINTS_CONFIG_FILE)
        logging.info(f"Config path: {self.config_path}")
        logging.info(f"Time points config path: {self.time_points_config_path}")
        self.time_ranges = []
        self.current_bg = None
        self.icon = None
        self.stop_event = threading.Event()
        self.last_config_modified = 0  # Track last modification time
        
    def load_config(self):
        """Load image configuration file if exists"""
        if os.path.exists(self.config_path):
            try:
                # Update last modified time
                self.last_config_modified = os.path.getmtime(self.config_path)
                
                with open(self.config_path, 'r') as f:
                    config = json.load(f)
                    self.time_ranges = config.get('time_ranges', [])
                logging.info(f"Loaded configuration with {len(self.time_ranges)} time ranges")
                return True
            except Exception as e:
                logging.error(f"Error loading configuration: {e}")
                return False
        else:
            logging.info("Configuration file does not exist")
            return False
    
    def load_time_points_config(self):
        """Load time points configuration file if exists"""
        if os.path.exists(self.time_points_config_path):
            try:
                with open(self.time_points_config_path, 'r') as f:
                    config = json.load(f)
                    time_points = config.get('time_points', [])
                logging.info(f"Loaded time points configuration with {len(time_points)} time points")
                return time_points
            except Exception as e:
                logging.error(f"Error loading time points configuration: {e}")
                return None
        else:
            logging.info("Time points configuration file does not exist")
            return None
    
    def save_time_points_config(self, time_points):
        """Save time points configuration to file"""
        try:
            with open(self.time_points_config_path, 'w') as f:
                json.dump({'time_points': time_points}, f, indent=4)
            logging.info("Time points configuration saved successfully")
            return True
        except Exception as e:
            logging.error(f"Error saving time points configuration: {e}")
            return False
    
    def save_config(self):
        """Save image configuration file"""
        try:
            with open(self.config_path, 'w') as f:
                json.dump({'time_ranges': self.time_ranges}, f, indent=4)
            logging.info("Configuration saved successfully")
            return True
        except Exception as e:
            logging.error(f"Error saving configuration: {e}")
            return False
    
    def add_to_startup(self):
        """Add application to Windows startup"""
        try:
            key = reg.HKEY_CURRENT_USER
            key_path = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run"
            
            # Open the key
            open_key = reg.OpenKey(key, key_path, 0, reg.KEY_ALL_ACCESS)
            
            # Get the absolute path of the executable or script
            if getattr(sys, 'frozen', False):
                # If we're running as an executable
                app_path = sys.executable
            else:
                # If we're running as a script
                app_path = os.path.abspath(__file__)
                
            # Set the key value
            reg.SetValueEx(open_key, "TimeBasedBackground", 0, reg.REG_SZ, app_path)
            reg.CloseKey(open_key)
            logging.info("Added to startup successfully")
            return True
        except Exception as e:
            logging.error(f"Error adding to startup: {e}")
            return False
    
    def set_wallpaper(self, image_path):
        """Set Windows wallpaper to the specified image"""
        if self.current_bg == image_path:
            return
            
        try:
            abs_path = os.path.abspath(image_path)
            ctypes.windll.user32.SystemParametersInfoW(20, 0, abs_path, 3)
            self.current_bg = image_path
            logging.info(f"Wallpaper set to: {image_path}")
            return True
        except Exception as e:
            logging.error(f"Error setting wallpaper: {e}")
            return False
    
    def get_current_time_range(self):
        """Get the appropriate time range for the current time"""
        now = datetime.datetime.now().time()
        
        for time_range in self.time_ranges:
            start_str = time_range["start"]
            end_str = time_range["end"]
            
            # Parse time strings into datetime.time objects
            start_hour, start_minute = map(int, start_str.split(':'))
            end_hour, end_minute = map(int, end_str.split(':'))
            
            start_time = datetime.time(start_hour, start_minute)
            end_time = datetime.time(end_hour, end_minute)
            
            # Check if current time is within range
            if start_time <= end_time:  # Normal case: start < end
                if start_time <= now <= end_time:
                    return time_range
            else:  # Overnight case: start > end (e.g., 23:00-8:30)
                if now >= start_time or now <= end_time:
                    return time_range
        
        return None
    
    def update_background(self):
        """Update background based on current time"""
        time_range = self.get_current_time_range()
        if time_range and os.path.exists(time_range["image"]):
            self.set_wallpaper(time_range["image"])
    
    def get_time_period_name(self, start, end):
        """Get a descriptive name for the time period"""
        # Morning: 5:00-12:00
        # Afternoon: 12:00-17:00
        # Evening: 17:00-21:00
        # Night: 21:00-5:00
        
        start_hour = int(start.split(':')[0])
        end_hour = int(end.split(':')[0])
        
        if 5 <= start_hour < 12:
            if 12 <= end_hour < 17:
                return "Morning to Afternoon"
            elif end_hour < 12:
                return "Morning"
        elif 12 <= start_hour < 17:
            if 17 <= end_hour < 21:
                return "Afternoon to Evening"
            elif end_hour < 17:
                return "Afternoon"
        elif 17 <= start_hour < 21:
            if 21 <= end_hour < 24 or 0 <= end_hour < 5:
                return "Evening to Night"
            elif end_hour < 21:
                return "Evening"
        elif 21 <= start_hour < 24 or 0 <= start_hour < 5:
            if 5 <= end_hour < 12:
                return "Night to Morning"
            elif end_hour < 5 or end_hour >= 21:
                return "Night"
                
        return f"{start} to {end}"
    
    def setup_time_points(self):
        """Setup time points before configuring time ranges"""
        try:
            # Check if we have existing time points configuration
            saved_time_points = self.load_time_points_config()
            
            # Default time points - these will be editable
            time_points = saved_time_points if saved_time_points else [
                "8:30", "9:30", "10:30", "11:30", "12:30", "14:00", 
                "14:30", "15:30", "16:00", "18:00", "19:00", 
                "20:00", "21:00", "23:00"
            ]
            
            # Set up root window - using grid layout for better control
            root = tk.Tk()
            root.title("Initial Setup: Configure Time Points")
            root.geometry("600x600")  # Increase height to ensure buttons are visible
            root.configure(bg="#f0f0f0")  # Light gray background
            
            # Color scheme
            HEADER_BG = "#2c3e50"  # Dark blue
            HEADER_FG = "#ecf0f1"  # White
            BUTTON_BG = "#3498db"  # Blue
            BUTTON_ACTIVE_BG = "#2980b9"  # Darker blue
            BUTTON_FG = "white"
            SAVE_BUTTON_BG = "#27ae60"  # Green
            SAVE_BUTTON_ACTIVE_BG = "#219955"  # Darker green
            DELETE_BUTTON_BG = "#e74c3c"  # Red
            DELETE_BUTTON_ACTIVE_BG = "#c0392b"  # Darker red
            ROW_BG_1 = "#ecf0f1"  # Light gray
            ROW_BG_2 = "#bdc3c7"  # Slightly darker gray
            
            # Use grid layout for better control
            root.grid_columnconfigure(0, weight=1)
            root.grid_rowconfigure(2, weight=1)  # Make the main content area expandable
            
            # Top frame for title and description
            top_frame = tk.Frame(root, bg="#f0f0f0", padx=20, pady=10)
            top_frame.grid(row=0, column=0, sticky="ew")
            
            # Add title
            title_label = tk.Label(
                top_frame, 
                text="Initial Setup: Configure Time Points", 
                font=("Arial", 16, "bold"),
                bg="#f0f0f0",
                fg=HEADER_BG,
                pady=10
            )
            title_label.pack(fill=tk.X)
            
            # Add subtitle
            subtitle_label = tk.Label(
                top_frame, 
                text="Configure time points for background changes. Add, edit, or remove time points as needed. The application will change your desktop background between consecutive time points.", 
                font=("Arial", 10),
                bg="#f0f0f0",
                fg="#555555",
                wraplength=550,
                justify=tk.LEFT
            )
            subtitle_label.pack(fill=tk.X, pady=(0, 15))
            
            # Header frame
            header_frame = tk.Frame(root, bg=HEADER_BG, padx=10, pady=5)
            header_frame.grid(row=1, column=0, sticky="ew", padx=20)
            
            # Header Labels
            tk.Label(header_frame, text="Time Point", width=20, 
                    font=("Arial", 11, "bold"), bg=HEADER_BG, fg=HEADER_FG).pack(side=tk.LEFT)
            
            tk.Label(header_frame, text="Action", width=15, 
                    font=("Arial", 11, "bold"), bg=HEADER_BG, fg=HEADER_FG).pack(side=tk.LEFT)
            
            # Main content frame with scrollbar
            content_frame = tk.Frame(root, bg="#f0f0f0", padx=20)
            content_frame.grid(row=2, column=0, sticky="nsew")
            
            content_frame.grid_columnconfigure(0, weight=1)
            content_frame.grid_rowconfigure(0, weight=1)
            
            # Create a canvas for scrolling in the content frame
            canvas = tk.Canvas(content_frame, bg="#f0f0f0", highlightthickness=0)
            scrollbar = tk.Scrollbar(content_frame, orient="vertical", command=canvas.yview)
            
            # Configure the canvas
            canvas.configure(yscrollcommand=scrollbar.set)
            
            # Pack the scrollbar and canvas
            scrollbar.grid(row=0, column=1, sticky="ns")
            canvas.grid(row=0, column=0, sticky="nsew")
            
            # Create a frame inside the canvas for entries
            entries_frame = tk.Frame(canvas, bg="#f0f0f0")
            canvas_window = canvas.create_window((0, 0), window=entries_frame, anchor="nw")
            
            # Configure the scrolling
            def on_frame_configure(event):
                canvas.configure(scrollregion=canvas.bbox("all"))
                
            # Configure the canvas window to stretch horizontally
            def on_canvas_configure(event):
                canvas.itemconfig(canvas_window, width=event.width)
                
            # Bind events for scrolling
            entries_frame.bind("<Configure>", on_frame_configure)
            canvas.bind("<Configure>", on_canvas_configure)
            
            # Enable mousewheel scrolling
            def on_mousewheel(event):
                canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
            
            canvas.bind_all("<MouseWheel>", on_mousewheel)
            
            # Store time points entries and validation variable
            time_entries = []
            time_stringvars = []
            
            # Validation function for time entry (HH:MM format)
            def validate_time(value, stvar, entry):
                if value == "":
                    return True
                
                # Check for proper format (HH:MM)
                if len(value) > 5:
                    return False
                
                # Allow incomplete entry during typing
                parts = value.split(':')
                if len(parts) > 2:
                    return False
                
                # Validate hours and minutes if completed
                if len(parts) == 2:
                    # Hours validation (0-23)
                    if parts[0] and not parts[0].isdigit():
                        return False
                    if parts[0] and int(parts[0]) > 23:
                        return False
                    
                    # Minutes validation (0-59)
                    if parts[1] and not parts[1].isdigit():
                        return False
                    if parts[1] and int(parts[1]) > 59:
                        return False
                elif value and not value.isdigit() and value != ':':
                    return False
                
                return True
            
            # Format time entry correctly when focus is lost
            def format_time(event, stringvar):
                value = stringvar.get().strip()
                if not value:
                    return
                
                parts = value.split(':')
                
                # Handle case where user entered just hours without colon
                if len(parts) == 1 and parts[0].isdigit() and len(parts[0]) <= 2:
                    stringvar.set(f"{int(parts[0]):02d}:00")
                    return
                
                # Handle incomplete entries
                if len(parts) < 2:
                    stringvar.set("00:00")
                    return
                
                # Format hours and minutes with leading zeros
                if parts[0] == '':
                    hours = 0
                else:
                    hours = int(parts[0])
                
                if parts[1] == '':
                    minutes = 0
                else:
                    minutes = int(parts[1])
                
                # Set the formatted time back to the entry
                stringvar.set(f"{hours:02d}:{minutes:02d}")
            
            # Function to update UI with current time points
            def update_time_points_ui():
                # Clear existing entries
                for widget in entries_frame.winfo_children():
                    widget.destroy()
                
                time_entries.clear()
                time_stringvars.clear()
                
                # Add time point entries
                for i, time_point in enumerate(time_points):
                    # Alternate background colors for rows
                    bg_color = ROW_BG_1 if i % 2 == 0 else ROW_BG_2
                    
                    row_frame = tk.Frame(entries_frame, bg=bg_color, pady=8, padx=5)
                    row_frame.pack(fill=tk.X, pady=2)
                    
                    # Time entry
                    time_var = tk.StringVar(value=time_point)
                    time_stringvars.append(time_var)
                    
                    # Validate command
                    validate_cmd = (root.register(
                        lambda val, sv=time_var, en=None: validate_time(val, sv, en)
                    ), '%P')
                    
                    time_entry = tk.Entry(
                        row_frame, 
                        textvariable=time_var, 
                        width=20,
                        font=("Arial", 10),
                        validate="key", 
                        validatecommand=validate_cmd
                    )
                    time_entry.bind("<FocusOut>", lambda event, sv=time_var: format_time(event, sv))
                    time_entry.pack(side=tk.LEFT, padx=5)
                    time_entries.append(time_entry)
                    
                    # Delete button
                    delete_button = tk.Button(
                        row_frame,
                        text="🗑️",
                        command=lambda idx=i: delete_time_point(idx),
                        bg=DELETE_BUTTON_BG,
                        activebackground=DELETE_BUTTON_ACTIVE_BG,
                        fg=BUTTON_FG,
                        font=("Arial", 10, "bold"),
                        width=3,
                        relief=tk.RAISED,
                        bd=2
                    )
                    delete_button.pack(side=tk.LEFT, padx=10)
            
            # Function to delete a time point
            def delete_time_point(index):
                if len(time_points) <= 2:
                    messagebox.showwarning(
                        "Cannot Delete", 
                        "You need at least 2 time points for the application to work."
                    )
                    return
                
                del time_points[index]
                update_time_points_ui()
                
                # Update canvas scrollregion
                root.update_idletasks()
                canvas.configure(scrollregion=canvas.bbox("all"))
            
            # Function to add a new time point
            def add_time_point():
                # Add a default new time point
                time_points.append("12:00")
                update_time_points_ui()
                
                # Focus on the new entry for immediate editing
                if time_entries:
                    time_entries[-1].focus_set()
                    time_entries[-1].select_range(0, 'end')
                
                # Update canvas scrollregion
                root.update_idletasks()
                canvas.configure(scrollregion=canvas.bbox("all"))
                
                # Scroll to the bottom
                canvas.yview_moveto(1.0)
            
            # Function to sort time points
            def sort_time_points():
                # Get current values from entries and validate
                for i, string_var in enumerate(time_stringvars):
                    time_points[i] = string_var.get()
                
                # Sort time points
                try:
                    time_points.sort(key=lambda x: 
                        int(x.split(':')[0]) * 60 + int(x.split(':')[1]) 
                        if ':' in x and len(x.split(':')) == 2 else 0
                    )
                    update_time_points_ui()
                except Exception as e:
                    messagebox.showerror("Error", f"Error sorting time points: {e}")
            
            # Function to validate and save all time points
            def validate_and_save():
                # Get time points from entries
                updated_time_points = []
                invalid_entries = []
                
                for i, string_var in enumerate(time_stringvars):
                    time_value = string_var.get().strip()
                    
                    # Basic validation
                    if not time_value:
                        invalid_entries.append(i)
                        continue
                    
                    # Format check for HH:MM
                    parts = time_value.split(':')
                    if len(parts) != 2 or not parts[0].isdigit() or not parts[1].isdigit():
                        invalid_entries.append(i)
                        continue
                    
                    # Range check
                    try:
                        hours = int(parts[0])
                        minutes = int(parts[1])
                        
                        if hours < 0 or hours > 23 or minutes < 0 or minutes > 59:
                            invalid_entries.append(i)
                            continue
                        
                        # Format to ensure consistency
                        formatted_time = f"{hours:02d}:{minutes:02d}"
                        updated_time_points.append(formatted_time)
                    except ValueError:
                        invalid_entries.append(i)
                
                # Highlight invalid entries
                if invalid_entries:
                    for idx in invalid_entries:
                        time_entries[idx].config(background="#ffcccc")  # Light red background
                    
                    messagebox.showerror(
                        "Invalid Time Format", 
                        "Some time points have invalid format. Please use HH:MM format (00:00 to 23:59)."
                    )
                    return None
                
                # Check for duplicates
                if len(updated_time_points) != len(set(updated_time_points)):
                    messagebox.showerror(
                        "Duplicate Times", 
                        "There are duplicate time points. Please make each time point unique."
                    )
                    return None
                
                # Make sure we have at least 2 time points
                if len(updated_time_points) < 2:
                    messagebox.showerror(
                        "Insufficient Time Points", 
                        "You need at least 2 time points for the application to work."
                    )
                    return None
                
                # Sort the time points before returning
                try:
                    updated_time_points.sort(key=lambda x: 
                        int(x.split(':')[0]) * 60 + int(x.split(':')[1])
                    )
                    return updated_time_points
                except Exception as e:
                    messagebox.showerror("Error", f"Error sorting time points: {e}")
                    return None
            
            # Initialize the UI with time points
            update_time_points_ui()
            
            # Action buttons panel at row 3 (below the scrolling area)
            action_panel = tk.Frame(root, bg="#f0f0f0", padx=20, pady=10)
            action_panel.grid(row=3, column=0, sticky="ew")
            
            # Add new time point button
            add_button = tk.Button(
                action_panel,
                text="+ Add Time Point",
                command=add_time_point,
                bg=BUTTON_BG,
                activebackground=BUTTON_ACTIVE_BG,
                fg=BUTTON_FG,
                font=("Arial", 10, "bold"),
                padx=10,
                pady=3,
                relief=tk.RAISED,
                bd=2
            )
            add_button.pack(side=tk.LEFT)
            
            sort_button = tk.Button(
                action_panel,
                text="Sort Time Points",
                command=sort_time_points,
                bg=BUTTON_BG,
                activebackground=BUTTON_ACTIVE_BG,
                fg=BUTTON_FG,
                font=("Arial", 10, "bold"),
                padx=10,
                pady=3,
                relief=tk.RAISED,
                bd=2
            )
            sort_button.pack(side=tk.LEFT, padx=10)
            
            # Bottom frame for save buttons (guaranteed to be at the bottom)
            bottom_frame = tk.Frame(root, bg="#f0f0f0", padx=20, pady=15)
            bottom_frame.grid(row=4, column=0, sticky="ew")
            
            # Variables to store the result
            result_time_points = None
            
            def save_time_points():
                time_points_to_save = validate_and_save()
                if time_points_to_save:
                    # Save time points configuration
                    if self.save_time_points_config(time_points_to_save):
                        messagebox.showinfo("Success", "Time points saved successfully!")
                    else:
                        messagebox.showerror("Error", "Failed to save time points configuration!")
            
            def save_and_continue():
                nonlocal result_time_points
                result_time_points = validate_and_save()
                if result_time_points:
                    # Save time points configuration
                    self.save_time_points_config(result_time_points)
                    root.quit()
                    root.destroy()
            
            # Make sure window closes properly
            def on_close():
                nonlocal result_time_points
                if messagebox.askyesno("Exit", "Are you sure you want to exit? Changes will be lost."):
                    result_time_points = None
                    root.quit()
                    root.destroy()
            
            root.protocol("WM_DELETE_WINDOW", on_close)
            
            # Create the save buttons
            save_points_button = tk.Button(
                bottom_frame,
                text="Save Time Points",
                command=save_time_points,
                bg=BUTTON_BG,
                activebackground=BUTTON_ACTIVE_BG,
                fg="white",
                font=("Arial", 11, "bold"),
                padx=15,
                pady=5,
                relief=tk.RAISED,
                bd=2
            )
            save_points_button.pack(side=tk.RIGHT, padx=10)
            
            save_continue_button = tk.Button(
                bottom_frame,
                text="Save & Continue",
                command=save_and_continue,
                bg=SAVE_BUTTON_BG,
                activebackground=SAVE_BUTTON_ACTIVE_BG,
                fg="white",
                font=("Arial", 11, "bold"),
                padx=15,
                pady=5,
                relief=tk.RAISED,
                bd=2
            )
            save_continue_button.pack(side=tk.RIGHT)
            
            # Center window on screen
            root.update_idletasks()
            width = root.winfo_width()
            height = root.winfo_height()
            x = (root.winfo_screenwidth() // 2) - (width // 2)
            y = (root.winfo_screenheight() // 2) - (height // 2)
            root.geometry('{}x{}+{}+{}'.format(width, height, x, y))
            
            # Focus on the window
            root.attributes('-topmost', True)
            root.update()
            root.attributes('-topmost', False)
            
            # Configure the scroll region for proper scrolling
            root.update_idletasks()
            canvas.configure(scrollregion=canvas.bbox("all"))
            
            root.mainloop()
            
            # Return the user-defined time points
            return result_time_points
            
        except Exception as e:
            logging.error(f"Error in time points setup: {e}")
            traceback.print_exc()
            messagebox.showerror("Error", f"An error occurred: {e}")
            return None
    
    def setup_time_ranges(self):
        """Setup time ranges from user input"""
        try:
            # Get time points from the time points setup page
            # Pass existing time points to setup_time_points if available
            time_points = self.setup_time_points()
            
            # If user canceled the time points setup or an error occurred
            if not time_points:
                # Use default time points
                time_points = [
                    "8:30", "9:30", "10:30", "11:30", "12:30", "14:00", 
                    "14:30", "15:30", "16:00", "18:00", "19:00", 
                    "20:00", "21:00", "23:00"
                ]
                logging.info("Using default time points")
            else:
                logging.info(f"Using user-defined time points: {time_points}")
                
                # Always save time points to config
                self.save_time_points_config(time_points)
            
            # Create time ranges
            ranges = []
            for i in range(len(time_points)):
                start = time_points[i]
                end = time_points[(i + 1) % len(time_points)]
                ranges.append((start, end))
            
            # Set up root window
            root = tk.Tk()
            root.title("Initial Setup: Configure Background Images")
            root.geometry("700x600")
            root.configure(bg="#f0f0f0")  # Light gray background
            
            # Color scheme
            HEADER_BG = "#2c3e50"  # Dark blue
            HEADER_FG = "#ecf0f1"  # White
            BUTTON_BG = "#3498db"  # Blue
            BUTTON_ACTIVE_BG = "#2980b9"  # Darker blue
            BUTTON_FG = "white"
            SAVE_BUTTON_BG = "#27ae60"  # Green
            SAVE_BUTTON_ACTIVE_BG = "#219955"  # Darker green
            ROW_BG_1 = "#ecf0f1"  # Light gray
            ROW_BG_2 = "#bdc3c7"  # Slightly darker gray
            
            # Create main frame
            main_frame = tk.Frame(root, bg="#f0f0f0", padx=20, pady=20)
            main_frame.pack(fill=tk.BOTH, expand=True)
            
            # Add title
            title_label = tk.Label(
                main_frame, 
                text="Initial Setup: Configure Background Images", 
                font=("Arial", 16, "bold"),
                bg="#f0f0f0",
                fg=HEADER_BG,
                pady=10
            )
            title_label.pack(fill=tk.X)
            
            # Add subtitle
            subtitle_label = tk.Label(
                main_frame, 
                text="Please select images for each time range. The application will automatically change your desktop background based on the current time.", 
                font=("Arial", 10),
                bg="#f0f0f0",
                fg="#555555",
                wraplength=650,
                justify=tk.LEFT
            )
            subtitle_label.pack(fill=tk.X, pady=(0, 15))
            
            # Create list header
            header_frame = tk.Frame(main_frame, bg=HEADER_BG, padx=10, pady=5)
            header_frame.pack(fill=tk.X, pady=(10, 0))
            
            # Header Labels
            tk.Label(header_frame, text="Time Range", width=20, 
                    font=("Arial", 11, "bold"), bg=HEADER_BG, fg=HEADER_FG).pack(side=tk.LEFT)
            
            tk.Label(header_frame, text="Image Path", width=40, 
                    font=("Arial", 11, "bold"), bg=HEADER_BG, fg=HEADER_FG).pack(side=tk.LEFT, padx=5)
            
            tk.Label(header_frame, text="Action", width=12, 
                    font=("Arial", 11, "bold"), bg=HEADER_BG, fg=HEADER_FG).pack(side=tk.LEFT)
            
            # Create a frame to hold the canvas and scrollbar
            scroll_frame = tk.Frame(main_frame, bg="#f0f0f0")
            scroll_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
            
            # Create a canvas for scrolling
            canvas = tk.Canvas(scroll_frame, bg="#f0f0f0", highlightthickness=0)
            scrollbar = tk.Scrollbar(scroll_frame, orient="vertical", command=canvas.yview)
            
            # Configure the canvas
            canvas.configure(yscrollcommand=scrollbar.set)
            
            # Pack the scrollbar and canvas
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            
            # Create a frame inside the canvas for entries
            entries_frame = tk.Frame(canvas, bg="#f0f0f0")
            
            # Add the entries frame to the canvas
            canvas_window = canvas.create_window((0, 0), window=entries_frame, anchor="nw")
            
            # Configure the scrolling
            def on_frame_configure(event):
                canvas.configure(scrollregion=canvas.bbox("all"))
            
            # Configure the canvas window to stretch horizontally
            def on_canvas_configure(event):
                canvas.itemconfig(canvas_window, width=event.width)
            
            # Bind events for scrolling
            entries_frame.bind("<Configure>", on_frame_configure)
            canvas.bind("<Configure>", on_canvas_configure)
            
            # Enable mousewheel scrolling
            def on_mousewheel(event):
                canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
            
            canvas.bind_all("<MouseWheel>", on_mousewheel)
            
            # Bind additional events for better scrolling
            canvas.bind("<Enter>", lambda e: canvas.bind_all("<MouseWheel>", on_mousewheel))
            canvas.bind("<Leave>", lambda e: canvas.unbind_all("<MouseWheel>"))
            
            # Store path variables
            path_vars = {}
            buttons = {}
            
            # Function to browse for an image
            def browse_image(index):
                try:
                    filename = filedialog.askopenfilename(
                        title=f"Select Image for {ranges[index][0]} to {ranges[index][1]}",
                        filetypes=(("Image files", "*.jpg;*.jpeg;*.png;*.bmp"), ("All files", "*.*"))
                    )
                    if filename:
                        path_vars[index].set(filename)
                        # Update button text
                        if not buttons[index]["text"] == "Change":
                            buttons[index].config(text="Change")
                except Exception as e:
                    logging.error(f"Error browsing for image: {e}")
                    messagebox.showerror("Error", f"Failed to select image: {e}")
            
            # Add time range entries
            for i, (start, end) in enumerate(ranges):
                # Alternate background colors for rows
                bg_color = ROW_BG_1 if i % 2 == 0 else ROW_BG_2
                
                row_frame = tk.Frame(entries_frame, bg=bg_color, pady=8, padx=5)
                row_frame.pack(fill=tk.X, pady=2)
                
                # Time range label
                time_label = tk.Label(
                    row_frame, 
                    text=f"{start} to {end}", 
                    width=20,
                    font=("Arial", 10),
                    bg=bg_color
                )
                time_label.pack(side=tk.LEFT)
                
                # Path variable and entry
                path_var = tk.StringVar()
                path_vars[i] = path_var
                
                path_entry = tk.Entry(
                    row_frame, 
                    textvariable=path_var, 
                    width=40, 
                    readonlybackground="white"
                )
                path_entry.configure(state="readonly")
                path_entry.pack(side=tk.LEFT, padx=5)
                
                # Browse button
                browse_button = tk.Button(
                    row_frame,
                    text="Choose",
                    command=lambda idx=i: browse_image(idx),
                    width=10,
                    bg=BUTTON_BG,
                    activebackground=BUTTON_ACTIVE_BG,
                    fg=BUTTON_FG,
                    font=("Arial", 9, "bold"),
                    relief=tk.RAISED,
                    bd=2
                )
                buttons[i] = browse_button
                browse_button.pack(side=tk.LEFT)
            
            # Button frame
            button_frame = tk.Frame(main_frame, bg="#f0f0f0", pady=15)
            button_frame.pack(fill=tk.X)
            
            def save_config():
                try:
                    # Check if at least one image is selected
                    has_image = False
                    for i in range(len(ranges)):
                        if path_vars[i].get().strip():
                            has_image = True
                            break
                    
                    if not has_image:
                        messagebox.showwarning(
                            "No Images Selected", 
                            "Please select at least one image for a time range."
                        )
                        return
                    
                    # Save configuration
                    self.time_ranges = []
                    for i, (start, end) in enumerate(ranges):
                        image_path = path_vars[i].get()
                        if image_path:
                            self.time_ranges.append({
                                "start": start,
                                "end": end,
                                "image": image_path
                            })
                    
                    if self.save_config():
                        root.quit()
                        root.destroy()
                    else:
                        messagebox.showerror("Error", "Failed to save configuration!")
                except Exception as e:
                    logging.error(f"Error saving configuration: {e}")
                    messagebox.showerror("Error", f"Error saving configuration: {e}")
                    
            # Make sure window closes properly
            def on_close():
                try:
                    root.quit()
                    root.destroy()
                except:
                    pass
                
            root.protocol("WM_DELETE_WINDOW", on_close)
            
            # Save button
            save_button = tk.Button(
                button_frame,
                text="Save Configuration & Start",
                command=save_config,
                bg=SAVE_BUTTON_BG,
                activebackground=SAVE_BUTTON_ACTIVE_BG,
                fg="white",
                font=("Arial", 11, "bold"),
                padx=15,
                pady=5,
                relief=tk.RAISED,
                bd=2
            )
            save_button.pack(side=tk.RIGHT)
            
            # Center window on screen
            root.update_idletasks()
            width = root.winfo_width()
            height = root.winfo_height()
            x = (root.winfo_screenwidth() // 2) - (width // 2)
            y = (root.winfo_screenheight() // 2) - (height // 2)
            root.geometry('{}x{}+{}+{}'.format(width, height, x, y))
            
            # Focus on the window
            root.attributes('-topmost', True)
            root.update()
            root.attributes('-topmost', False)
            
            # Configure the scroll region for proper scrolling
            root.update_idletasks()
            canvas.configure(scrollregion=canvas.bbox("all"))
            
            root.mainloop()
            
        except Exception as e:
            logging.error(f"Error in setup UI: {e}")
            traceback.print_exc()
            messagebox.showerror("Error", f"An error occurred: {e}")
    
    def check_config_updated(self):
        """Check if configuration file has been modified and reload if needed"""
        if os.path.exists(self.config_path):
            current_modified = os.path.getmtime(self.config_path)
            if current_modified > self.last_config_modified:
                logging.info("Configuration file has been modified, reloading...")
                self.load_config()
                # Force background update after config reload
                self.update_background()
                return True
        return False
    
    def background_monitor(self):
        """Monitor time and update background in a separate thread"""
        while not self.stop_event.is_set():
            try:
                # Check if config has been updated
                self.check_config_updated()
                
                # Update background based on current time
                self.update_background()
                
                # Sleep in smaller increments to check for stop event more frequently
                for _ in range(CHECK_INTERVAL):
                    if self.stop_event.is_set():
                        break
                    time.sleep(1)
            except Exception as e:
                logging.error(f"Error in background monitor: {e}")
                time.sleep(5)  # Short sleep on error
    
    def create_icon_image(self):
        """Create an icon for the system tray"""
        # Create a simple clock icon
        width = 64
        height = 64
        color1 = (0, 114, 206)  # Blue
        color2 = (255, 255, 255)  # White
        
        image = Image.new('RGB', (width, height), color2)
        dc = ImageDraw.Draw(image)
        
        # Draw clock circle
        dc.ellipse((4, 4, width-4, height-4), fill=color1)
        dc.ellipse((8, 8, width-8, height-8), fill=color2)
        
        # Draw clock hands
        now = datetime.datetime.now()
        
        # Hour hand
        hour_angle = (now.hour % 12 + now.minute / 60) * 30
        hour_x = width/2 + 15 * -1 * (0.4 * float(datetime.datetime.now().strftime('%I')))
        hour_y = height/2 + 15 * -1
        dc.line((width/2, height/2, hour_x, hour_y), fill=color1, width=4)
        
        # Minute hand
        minute_angle = now.minute * 6
        minute_x = width/2 + 20 * -1 * (0.4 * float(datetime.datetime.now().strftime('%M')))
        minute_y = height/2 + 20 * -1
        dc.line((width/2, height/2, minute_x, minute_y), fill=color1, width=3)
        
        return image
        
    def setup_tray_icon(self):
        """Setup system tray icon"""
        image = self.create_icon_image()
        
        # Save to temp file - needed for executable mode
        temp_icon = os.path.join(tempfile.gettempdir(), "time_based_bg_icon.png")
        image.save(temp_icon)
        
        # Define tray icon menu
        menu = (
            pystray.MenuItem('Status: Running', lambda: None, enabled=False),
            pystray.MenuItem('Reconfigure', self.open_reconfigure),
            pystray.MenuItem('Exit', self.exit_app)
        )
        
        # Create and run the icon
        self.icon = pystray.Icon("TimeBasedBackground")
        self.icon.icon = Image.open(temp_icon)
        self.icon.menu = pystray.Menu(*menu)
        self.icon.title = "Time-Based Background Changer"
        
        # Start the icon
        self.icon.run_detached()
        logging.info("System tray icon created")
    
    def open_reconfigure(self):
        """Open the reconfiguration tool"""
        try:
            logging.info("Launching reconfiguration tool")
            
            # Check if running as executable
            if getattr(sys, 'frozen', False):
                # We're running in a bundle
                # In a PyInstaller onefile bundle, we need to use the executable directly
                executable_path = sys.executable
                logging.info(f"Launching reconfiguration from frozen executable: {executable_path}")
                subprocess.Popen([executable_path, "--reconfigure"], 
                                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP)
            else:
                # We're running in a normal Python environment
                reconfigure_script = os.path.join(self.app_path, 'reconfigure.py')
                python_exec = sys.executable
                logging.info(f"Launching reconfiguration from script: {python_exec} {reconfigure_script}")
                subprocess.Popen([python_exec, reconfigure_script], 
                                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP)
            
        except Exception as e:
            logging.error(f"Error launching reconfiguration tool: {e}")
            messagebox.showerror("Error", f"Failed to open reconfiguration tool: {e}")
    
    def exit_app(self):
        """Exit the application gracefully"""
        logging.info("Application exit requested")
        if self.icon:
            self.icon.stop()
        self.stop_event.set()
        sys.exit(0)
    
    def run(self):
        """Main application entry point"""
        try:
            # Try to add to startup
            self.add_to_startup()
            
            # Check for various configuration states
            has_images_config = os.path.exists(self.config_path)
            has_time_points_config = os.path.exists(self.time_points_config_path)
            
            logging.info(f"Configuration status - Images config: {has_images_config}, Time points config: {has_time_points_config}")
            
            # Case 1: Images config exists, but no time points config
            # Action: Remove images config and run as first-time setup
            if has_images_config and not has_time_points_config:
                logging.info("Images config exists but no time points config. Removing images config and running as first-time setup.")
                try:
                    os.remove(self.config_path)
                    has_images_config = False
                except Exception as e:
                    logging.error(f"Error removing images config: {e}")
            
            # Case 2: Both configs exist - run normally
            if has_images_config and has_time_points_config:
                logging.info("Both configuration files exist. Running normally.")
                self.load_config()
                
            # Case 3: Time points config exists but no images config
            # Case 4: Neither config exists
            # Action: Show setup pages
            elif not has_images_config:
                logging.info("Starting setup process.")
                
                # First step: Configure the time points (will save to file if successful)
                self.setup_time_ranges()  # This internally calls setup_time_points first
                
                # Try to load the config after setup
                if not self.load_config():
                    logging.error("Configuration still not found after setup, exiting")
                    messagebox.showerror("Error", "Failed to create configuration. Application will exit.")
                    sys.exit(1)
            
            # Update the background immediately
            self.update_background()
            
            # Setup system tray icon
            self.setup_tray_icon()
            
            # Start the background monitor in a separate thread
            monitor_thread = threading.Thread(target=self.background_monitor, daemon=True)
            monitor_thread.start()
            
            # Print a message to the console
            print("\nApplication is running in the background with a system tray icon.")
            print("Look for the clock icon in your system tray (near the clock in taskbar).")
            print("Right-click the icon for options.")
            print("\nConsole window will hide in 5 seconds...")
            
            # Hide console window after a delay to allow reading the messages
            def hide_console():
                time.sleep(5)  # Give user time to read messages
                hwnd = ctypes.windll.kernel32.GetConsoleWindow()
                if hwnd != 0:
                    # SW_HIDE = 0
                    ctypes.windll.user32.ShowWindow(hwnd, 0)
                    logging.info("Console window hidden")
                    
            # Start thread to hide console after delay
            hide_thread = threading.Thread(target=hide_console, daemon=True)
            hide_thread.start()
            
            # Keep the main thread alive to handle keyboard interrupts
            try:
                while not self.stop_event.is_set():
                    time.sleep(1)
            except KeyboardInterrupt:
                self.exit_app()
            
        except Exception as e:
            logging.error(f"Error in main application: {e}")
            print(f"Error: {e}")
            input("Press Enter to exit...")

if __name__ == "__main__":
    # Check if we're being called with the --reconfigure argument
    if len(sys.argv) > 1 and sys.argv[1] == "--reconfigure":
        # Import and run the reconfiguration tool
        try:
            from reconfigure import ReconfigureTool
            reconfigure_tool = ReconfigureTool()
            reconfigure_tool.run_gui()
            sys.exit(0)
        except Exception as e:
            logging.error(f"Error launching reconfiguration: {e}")
            messagebox.showerror("Error", f"Failed to launch reconfiguration: {e}")
            sys.exit(1)
    else:
        # Run the main application
        app = TimeBasedBackground()
        app.run() 