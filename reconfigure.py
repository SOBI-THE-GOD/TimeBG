import os
import sys
import json
import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
import traceback
import ctypes  # Added for hiding console window

# Get application path for both script and frozen exe
def get_application_path():
    if getattr(sys, 'frozen', False):
        # We're running in a bundle (executable)
        return os.path.dirname(sys.executable)
    else:
        # We're running in a normal Python environment
        return os.path.dirname(os.path.abspath(__file__))
        
CONFIG_FILE = "images_config.json"
TIME_POINTS_CONFIG_FILE = "time_points_config.json"

class ReconfigureTool:
    def __init__(self):
        self.app_path = get_application_path()
        self.config_path = os.path.join(self.app_path, CONFIG_FILE)
        self.time_points_config_path = os.path.join(self.app_path, TIME_POINTS_CONFIG_FILE)
        print(f"Config path: {self.config_path}")
        print(f"Time points config path: {self.time_points_config_path}")
        self.time_ranges = []
        self.load_existing_config()
        
    def load_existing_config(self):
        """Load existing configuration if available"""
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r') as f:
                    config = json.load(f)
                    self.time_ranges = config.get('time_ranges', [])
                print(f"Loaded configuration with {len(self.time_ranges)} time ranges")
                return True
            except Exception as e:
                print(f"Error loading configuration: {e}")
                return False
        else:
            print("Configuration file does not exist. A new one will be created.")
            # Define default time points
            self.create_default_time_ranges()
            return False
    
    def load_time_points_config(self):
        """Load time points configuration file if exists"""
        if os.path.exists(self.time_points_config_path):
            try:
                with open(self.time_points_config_path, 'r') as f:
                    config = json.load(f)
                    time_points = config.get('time_points', [])
                print(f"Loaded time points configuration with {len(time_points)} time points")
                return time_points
            except Exception as e:
                print(f"Error loading time points configuration: {e}")
                return None
        else:
            print("Time points configuration file does not exist")
            return None
    
    def create_default_time_ranges(self):
        """Create default time ranges if no config exists"""
        # Try to load time points from config file
        time_points = self.load_time_points_config()
        
        # If no time points config, use defaults
        if not time_points:
            time_points = [
                "8:30", "9:30", "10:30", "11:30", "12:30", "14:00", 
                "14:30", "15:30", "16:00", "18:00", "19:00", 
                "20:00", "21:00", "23:00"
            ]
        
        for i in range(len(time_points)):
            start = time_points[i]
            end = time_points[(i + 1) % len(time_points)]
            self.time_ranges.append({
                "start": start,
                "end": end,
                "image": ""
            })
    
    def save_config(self):
        """Save image configuration file"""
        try:
            # Make sure we have valid data
            if not self.time_ranges:
                print("Error: No time ranges to save!")
                return False
                
            # Ensure the config has valid data
            valid_entries = False
            for entry in self.time_ranges:
                if entry.get("image") and os.path.exists(entry.get("image")):
                    valid_entries = True
                    break
                    
            if not valid_entries:
                print("Error: No valid image paths found in configuration!")
                return False
                
            with open(self.config_path, 'w') as f:
                json.dump({'time_ranges': self.time_ranges}, f, indent=4)
            print(f"Configuration saved successfully to {self.config_path}")
            return True
        except Exception as e:
            print(f"Error saving configuration: {e}")
            traceback.print_exc()
            return False
    
    def configure_time_points(self):
        """Open the time points configuration window"""
        # Import the main module to access the TimeBasedBackground class
        try:
            import main
            app = main.TimeBasedBackground()
            
            # Show the time points setup interface
            time_points = app.setup_time_points()
            
            # If user successfully configured time points
            if time_points:
                # Save the time points
                app.save_time_points_config(time_points)
                
                # Recreate time ranges with the new time points
                new_time_ranges = []
                for i in range(len(time_points)):
                    start = time_points[i]
                    end = time_points[(i + 1) % len(time_points)]
                    
                    # Find existing images for this time range
                    image_path = ""
                    for tr in self.time_ranges:
                        if tr["start"] == start and tr["end"] == end:
                            image_path = tr.get("image", "")
                            break
                    
                    new_time_ranges.append({
                        "start": start,
                        "end": end,
                        "image": image_path
                    })
                
                # Update time ranges and redraw UI
                self.time_ranges = new_time_ranges
                
                # Reload the UI
                messagebox.showinfo("Success", "Time points updated successfully. The UI will now reload.")
                self.root.destroy()
                self.run_gui()
            
        except Exception as e:
            print(f"Error configuring time points: {e}")
            traceback.print_exc()
            messagebox.showerror("Error", f"Failed to configure time points: {e}")
    
    def run_gui(self):
        """Run the GUI to reconfigure time ranges"""
        try:
            # Set up root window
            self.root = tk.Tk()
            root = self.root
            root.title("Configure Background Images")
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
            CANCEL_BUTTON_BG = "#e74c3c"  # Red
            CANCEL_BUTTON_ACTIVE_BG = "#c0392b"  # Darker red
            ROW_BG_1 = "#ecf0f1"  # Light gray
            ROW_BG_2 = "#bdc3c7"  # Slightly darker gray
            
            # Add menu bar
            menubar = tk.Menu(root)
            root.config(menu=menubar)
            
            # Add Options menu
            options_menu = tk.Menu(menubar, tearoff=0)
            menubar.add_cascade(label="Options", menu=options_menu)
            options_menu.add_command(label="Configure Time Points", command=self.configure_time_points)
            
            # Create main frame
            main_frame = tk.Frame(root, bg="#f0f0f0", padx=20, pady=20)
            main_frame.pack(fill=tk.BOTH, expand=True)
            
            # Add title
            title_label = tk.Label(
                main_frame, 
                text="Configure Background Images for Time Ranges", 
                font=("Arial", 16, "bold"),
                bg="#f0f0f0",
                fg=HEADER_BG,
                pady=10
            )
            title_label.pack(fill=tk.X)
            
            # Create list header
            header_frame = tk.Frame(main_frame, bg=HEADER_BG, padx=10, pady=5)
            header_frame.pack(fill=tk.X, pady=(10, 0))
            
            # Header Labels
            header_time = tk.Label(
                header_frame, 
                text="Time Range", 
                width=20, 
                font=("Arial", 11, "bold"), 
                bg=HEADER_BG, 
                fg=HEADER_FG
            )
            header_time.pack(side=tk.LEFT)
            
            header_path = tk.Label(
                header_frame, 
                text="Image Path", 
                width=40, 
                font=("Arial", 11, "bold"), 
                bg=HEADER_BG, 
                fg=HEADER_FG
            )
            header_path.pack(side=tk.LEFT, padx=5)
            
            header_action = tk.Label(
                header_frame, 
                text="Action", 
                width=12, 
                font=("Arial", 11, "bold"), 
                bg=HEADER_BG, 
                fg=HEADER_FG
            )
            header_action.pack(side=tk.LEFT)
            
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
            
            # Store path variables and buttons
            path_vars = {}
            buttons = {}
            
            # Function to browse for an image
            def browse_image(index):
                try:
                    filename = filedialog.askopenfilename(
                        title=f"Select Image for {self.time_ranges[index]['start']} to {self.time_ranges[index]['end']}",
                        filetypes=(("Image files", "*.jpg;*.jpeg;*.png;*.bmp"), ("All files", "*.*"))
                    )
                    if filename:
                        path_vars[index].set(filename)
                        buttons[index].config(text="Change")
                except Exception as e:
                    print(f"Error browsing for image: {e}")
                    messagebox.showerror("Error", f"Failed to select image: {e}")
            
            # Add time range entries
            for i, time_range in enumerate(self.time_ranges):
                # Alternate background colors for rows
                bg_color = ROW_BG_1 if i % 2 == 0 else ROW_BG_2
                
                row_frame = tk.Frame(entries_frame, bg=bg_color, pady=8, padx=5)
                row_frame.pack(fill=tk.X, pady=2)
                
                # Time range label
                time_label = tk.Label(
                    row_frame, 
                    text=f"{time_range['start']} to {time_range['end']}", 
                    width=20,
                    font=("Arial", 10),
                    bg=bg_color
                )
                time_label.pack(side=tk.LEFT)
                
                # Path variable and entry
                path_var = tk.StringVar(value=time_range.get("image", ""))
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
                button_text = "Change" if time_range.get("image") else "Choose"
                browse_button = tk.Button(
                    row_frame,
                    text=button_text,
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
            
            # Save function
            def save_config():
                try:
                    # Check if at least one image is selected
                    has_image = False
                    for i in range(len(self.time_ranges)):
                        if path_vars[i].get().strip():
                            has_image = True
                            break
                    
                    if not has_image:
                        messagebox.showwarning(
                            "No Images Selected", 
                            "Please select at least one image for a time range."
                        )
                        return
                    
                    # Update time ranges with selected images
                    for i, time_range in enumerate(self.time_ranges):
                        time_range["image"] = path_vars[i].get()
                    
                    # Save to file
                    if self.save_config():
                        messagebox.showinfo("Success", "Configuration saved successfully!\n\nThe changes will be applied automatically.")
                        
                        # Hide console window
                        hwnd = ctypes.windll.kernel32.GetConsoleWindow()
                        if hwnd != 0:
                            ctypes.windll.user32.ShowWindow(hwnd, 0)  # SW_HIDE = 0
                            
                        root.quit()
                        root.destroy()
                    else:
                        messagebox.showerror("Error", "Failed to save configuration!")
                except Exception as e:
                    print(f"Error saving configuration: {e}")
                    messagebox.showerror("Error", f"Error saving configuration: {e}")
            
            # Cancel function
            def cancel():
                try:
                    if messagebox.askyesno("Confirm Cancel", "Are you sure you want to cancel? Changes will not be saved."):
                        # Hide console window
                        hwnd = ctypes.windll.kernel32.GetConsoleWindow()
                        if hwnd != 0:
                            ctypes.windll.user32.ShowWindow(hwnd, 0)  # SW_HIDE = 0
                            
                        root.quit()
                        root.destroy()
                except Exception as e:
                    print(f"Error canceling: {e}")
                    root.destroy()
            
            # Make sure window closes properly
            def on_close():
                try:
                    # Hide console window
                    hwnd = ctypes.windll.kernel32.GetConsoleWindow()
                    if hwnd != 0:
                        ctypes.windll.user32.ShowWindow(hwnd, 0)  # SW_HIDE = 0
                        
                    root.quit()
                    root.destroy()
                except:
                    pass
                
            root.protocol("WM_DELETE_WINDOW", on_close)
            
            # Save button
            save_button = tk.Button(
                button_frame,
                text="Save Configuration",
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
            
            # Cancel button
            cancel_button = tk.Button(
                button_frame,
                text="Cancel",
                command=cancel,
                bg=CANCEL_BUTTON_BG,
                activebackground=CANCEL_BUTTON_ACTIVE_BG,
                fg="white",
                font=("Arial", 11, "bold"),
                padx=15,
                pady=5,
                relief=tk.RAISED,
                bd=2
            )
            cancel_button.pack(side=tk.RIGHT, padx=10)
            
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
            print(f"Error in reconfiguration GUI: {e}")
            traceback.print_exc()
            messagebox.showerror("Error", f"An error occurred: {e}")

if __name__ == "__main__":
    tool = ReconfigureTool()
    tool.run_gui() 