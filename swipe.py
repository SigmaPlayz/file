import tkinter as tk
from tkinter import messagebox, scrolledtext, ttk, font
import sys
import os
import time
import urllib.request
import threading # For running download in a separate thread
import subprocess # Added for launching the game file

# --- Configuration ---
GAME_NAME = "TurboCraft"
GAME_VERSION = "1.1"
DEVELOPER = "TurboDev"
LAUNCHER_TITLE = f"{GAME_NAME} Launcher - {DEVELOPER}"
GAME_DOWNLOAD_URL = "https://github.com/sigmaplayz/file/raw/main/client.py"
BG_IMAGE_DOWNLOAD_URL = "https://github.com/sigmaplayz/file/raw/main/bg.jpg" # Download URL for background image

# Define the base directory for TurboCraft within the user's home directory
# This will resolve to C:\Users\username\TurboCraft on Windows,
# and /home/username/TurboCraft on Linux, or /Users/username/TurboCraft on macOS.
TURBOCRAFT_BASE_DIR = os.path.join(os.path.expanduser('~'), "TurboCraft")
ASSETS_SUBDIR = "assets" # New constant for the assets subdirectory

GAME_FILE_NAME = "client.py" # Expected name of the downloaded game file
BG_IMAGE_FILE_NAME = "bg.jpg" # Expected name of the downloaded background image

# --- Custom Button Class for better aesthetics ---
class CustomButton(tk.Canvas):
    def __init__(self, parent, text, command, font_size=16, bg_color="#7289da", text_color="#ffffff", hover_color="#677bc4", **kwargs):
        super().__init__(parent, highlightthickness=0, relief="flat", **kwargs)
        self.text = text
        self.command = command
        self.bg_color = bg_color
        self.text_color = text_color
        self.hover_color = hover_color
        self.font_size = font_size
        self.border_radius = 10 # Rounded corners

        self.bind("<Configure>", self._draw_button)
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        self.bind("<Button-1>", self._on_click)

        self.configure(bg=parent.cget('bg')) # Match parent background

    def _draw_button(self, event=None):
        self.delete("all")
        width = self.winfo_width()
        height = self.winfo_height()

        # Draw rounded rectangle background
        self.create_arc((0, 0, self.border_radius*2, self.border_radius*2), start=90, extent=90, fill=self.bg_color, outline=self.bg_color)
        self.create_arc((width - self.border_radius*2, 0, width, self.border_radius*2), start=0, extent=90, fill=self.bg_color, outline=self.bg_color)
        self.create_arc((width - self.border_radius*2, height - self.border_radius*2, width, height), start=270, extent=90, fill=self.bg_color, outline=self.bg_color)
        self.create_arc((0, height - self.border_radius*2, self.border_radius*2, height), start=180, extent=90, fill=self.bg_color, outline=self.bg_color)

        self.create_rectangle(self.border_radius, 0, width - self.border_radius, height, fill=self.bg_color, outline=self.bg_color)
        self.create_rectangle(0, self.border_radius, width, height - self.border_radius, fill=self.bg_color, outline=self.bg_color)

        # Draw text
        self.create_text(
            width / 2, height / 2,
            text=self.text,
            fill=self.text_color,
            font=("Inter", self.font_size, "bold"),
            anchor="center"
        )

    def _on_enter(self, event):
        self.config(cursor="hand2")
        self.bg_color_original = self.bg_color
        self.bg_color = self.hover_color
        self._draw_button()

    def _on_leave(self, event):
        self.config(cursor="")
        self.bg_color = self.bg_color_original
        self._draw_button()

    def _on_click(self, event):
        if self.command:
            self.command()

# --- Main Launcher Application ---
class TurboCraftLauncher(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(LAUNCHER_TITLE)
        self.geometry("800x600")
        self.resizable(False, False)

        # Variables to track game process and timer
        self.game_process = None
        self.game_start_time = None
        self.timer_id = None # To store the ID of the after() call for the timer

        # Configure grid weights for responsive layout
        self.grid_rowconfigure(0, weight=0) # Header
        self.grid_rowconfigure(1, weight=1) # Main content
        self.grid_rowconfigure(2, weight=0) # Footer/buttons
        self.grid_columnconfigure(0, weight=1)

        self.game_versions = ["1.1"] # Available versions
        self.selected_version = tk.StringVar(self)
        self.selected_version.set(GAME_VERSION) # Default to 1.1

        self.create_widgets()

    def create_widgets(self):
        # --- Header Frame ---
        header_frame = tk.Frame(self, bg="#1a1a1d", padx=20, pady=15) # Darker header
        header_frame.grid(row=0, column=0, sticky="ew")
        header_frame.grid_columnconfigure(0, weight=1)
        header_frame.grid_columnconfigure(1, weight=0) # For version selector

        # Game Title
        game_title_label = tk.Label(
            header_frame,
            text=GAME_NAME,
            font=("Inter", 36, "bold"),
            fg="#e0e0e0", # Lighter text
            bg="#1a1a1d"
        )
        game_title_label.grid(row=0, column=0, sticky="w")

        # Version and Developer Info
        info_label = tk.Label(
            header_frame,
            text=f"Developed by {DEVELOPER}",
            font=("Inter", 12),
            fg="#909090",
            bg="#1a1a1d"
        )
        info_label.grid(row=1, column=0, sticky="w")

        # Version Selector
        version_label = tk.Label(
            header_frame,
            text="Version:",
            font=("Inter", 10),
            fg="#e0e0e0",
            bg="#1a1a1d"
        )
        version_label.grid(row=0, column=1, sticky="e", padx=(0, 5))

        version_menu = tk.OptionMenu(header_frame, self.selected_version, *self.game_versions)
        version_menu.config(
            font=("Inter", 10),
            bg="#3a3a40",
            fg="#ffffff",
            activebackground="#4a4a50",
            activeforeground="#ffffff",
            relief="flat",
            borderwidth=0,
            indicatoron=0 # Hide default indicator
        )
        version_menu["menu"].config(
            font=("Inter", 10),
            bg="#3a3a40",
            fg="#ffffff",
            activebackground="#5a5a60",
            activeforeground="#ffffff",
            relief="flat"
        )
        version_menu.grid(row=1, column=1, sticky="e")


        # --- Main Content Frame ---
        main_content_frame = tk.Frame(self, bg="#25252a", padx=20, pady=20) # Slightly lighter main content
        main_content_frame.grid(row=1, column=0, sticky="nsew")
        main_content_frame.grid_columnconfigure(0, weight=1)
        main_content_frame.grid_rowconfigure(1, weight=1) # News area

        # News Section
        news_label = tk.Label(
            main_content_frame,
            text="Latest TurboCraft News",
            font=("Inter", 18, "bold"),
            fg="#e0e0e0",
            bg="#25252a",
            anchor="w"
        )
        news_label.grid(row=0, column=0, sticky="ew", pady=(0, 10))

        self.news_text_area = scrolledtext.ScrolledText(
            main_content_frame,
            wrap=tk.WORD,
            font=("Inter", 10),
            bg="#1a1a1d", # Darker background for news
            fg="#cccccc",
            height=10,
            relief="flat",
            borderwidth=0,
            insertbackground="#ffffff",
            padx=10,
            pady=10
        )
        self.news_text_area.grid(row=1, column=0, sticky="nsew", pady=(0, 20))
        self.news_text_area.insert(tk.END, self.get_news_content())
        self.news_text_area.config(state=tk.DISABLED)

        # Progress Bar for loading
        self.progress_bar = ttk.Progressbar(
            main_content_frame,
            orient="horizontal",
            length=400,
            mode="determinate",
            style="TProgressbar" # Apply custom style
        )
        self.progress_bar.grid(row=2, column=0, pady=(10, 0), sticky="ew")
        self.progress_label = tk.Label(
            main_content_frame,
            text="",
            font=("Inter", 10),
            fg="#cccccc",
            bg="#25252a"
        )
        self.progress_label.grid(row=3, column=0, pady=(5, 0), sticky="ew")

        # Game Timer Label
        self.game_timer_label = tk.Label(
            main_content_frame,
            text="Game not running.",
            font=("Inter", 10, "bold"),
            fg="#4CAF50", # Green color for timer
            bg="#25252a"
        )
        self.game_timer_label.grid(row=4, column=0, pady=(5, 0), sticky="ew")


        # Style for the progress bar
        style = ttk.Style()
        style.theme_use('clam') # Use 'clam' theme as a base for customization
        style.configure(
            "TProgressbar",
            background="#4CAF50", # Green progress color
            troughcolor="#3a3a40", # Darker trough
            bordercolor="#25252a",
            lightcolor="#4CAF50",
            darkcolor="#4CAF50"
        )
        style.map(
            "TProgressbar",
            background=[('active', '#66BB6A')]
        )


        # --- Action Buttons Frame ---
        button_frame = tk.Frame(self, bg="#1a1a1d", padx=20, pady=15)
        button_frame.grid(row=2, column=0, sticky="ew")
        button_frame.grid_columnconfigure(0, weight=1)
        button_frame.grid_columnconfigure(1, weight=1)
        button_frame.grid_columnconfigure(2, weight=1)

        # Play Button using CustomButton
        self.play_button_canvas = CustomButton(
            button_frame,
            text="PLAY TURBOCRAFT",
            command=self.start_game_process, # Changed command to start a new process
            font_size=16,
            bg_color="#4CAF50", # Vibrant green for play
            hover_color="#66BB6A",
            width=250, # Fixed width for custom button
            height=50
        )
        self.play_button_canvas.grid(row=0, column=1, pady=10, sticky="ew", padx=10)

        # Settings Button using CustomButton
        self.settings_button_canvas = CustomButton(
            button_frame,
            text="Settings",
            command=self.open_settings,
            font_size=12,
            bg_color="#5a5a60", # Medium grey
            hover_color="#6a6a70",
            width=120,
            height=40
        )
        self.settings_button_canvas.grid(row=0, column=0, pady=10, sticky="w", padx=10)

        # Exit Button using CustomButton
        self.exit_button_canvas = CustomButton(
            button_frame,
            text="Exit",
            command=self.quit_launcher,
            font_size=12,
            bg_color="#e53935", # Red for exit
            hover_color="#f44336",
            width=100,
            height=40
        )
        self.exit_button_canvas.grid(row=0, column=2, pady=10, sticky="e", padx=10)

    def get_news_content(self):
        """
        Fetches or generates news content.
        """
        return (
            "Welcome, Turbo! The TurboCraft 1.1 update is here!\n\n"
            "**New Features in 1.1:**\n"
            "- Added World Generation\n"
            "- Just Nothing More Only Player Movement And Some Basic Things in 1.1\n"
            "- Expect Something Good In 1.2\n"
        )

    def start_game_process(self):
        """
        Starts the game launch process in a separate thread to keep GUI responsive.
        """
        self.play_button_canvas.config(state="disabled")
        self.settings_button_canvas.config(state="disabled")
        self.exit_button_canvas.config(state="disabled")
        
        # Start the actual launch/download logic in a new thread
        threading.Thread(target=self._launch_game_logic).start()

    def _launch_game_logic(self):
        """
        Contains the core logic for downloading, verifying, and launching the game.
        Runs in a separate thread.
        """
        # Define the full paths for the game files
        game_file_path = os.path.join(TURBOCRAFT_BASE_DIR, GAME_FILE_NAME)
        
        # Define the full path for the assets directory and the background image
        assets_dir_path = os.path.join(TURBOCRAFT_BASE_DIR, ASSETS_SUBDIR)
        bg_image_file_path = os.path.join(assets_dir_path, BG_IMAGE_FILE_NAME)

        try:
            # Step 1: Simulate initial checks
            self.update_progress("Checking for updates...", 5)
            time.sleep(0.2)

            # Ensure the TurboCraft base directory exists
            os.makedirs(TURBOCRAFT_BASE_DIR, exist_ok=True)
            # Ensure the assets subdirectory exists
            os.makedirs(assets_dir_path, exist_ok=True)

            # Step 2: Download or verify client.py
            if os.path.exists(game_file_path):
                self.update_progress("Client file found locally!", 15)
                time.sleep(0.2)
            else:
                self.update_progress("Client file not found. Downloading...", 15)
                try:
                    urllib.request.urlretrieve(GAME_DOWNLOAD_URL, game_file_path, reporthook=lambda count, block_size, total_size: self._download_progress_hook(count, block_size, total_size, start_percent=15, end_percent=45))
                    self.update_progress("Client download complete!", 45)
                    time.sleep(0.2)
                    if not os.path.exists(game_file_path):
                        messagebox.showerror("Download Error", f"Failed to save {GAME_FILE_NAME} at {game_file_path}. Please try again.")
                        self.reset_launcher_state()
                        return
                except Exception as e:
                    messagebox.showerror("Download Error", f"Failed to download client.py: {e}\nPlease check your internet connection and try again.")
                    self.reset_launcher_state()
                    return

            # Step 3: Download or verify bg.jpg in the assets directory
            if os.path.exists(bg_image_file_path):
                self.update_progress("Background image found locally!", 55)
                time.sleep(0.2)
            else:
                self.update_progress("Background image not found. Downloading...", 55)
                try:
                    urllib.request.urlretrieve(BG_IMAGE_DOWNLOAD_URL, bg_image_file_path, reporthook=lambda count, block_size, total_size: self._download_progress_hook(count, block_size, total_size, start_percent=55, end_percent=85))
                    self.update_progress("Background image download complete!", 85)
                    time.sleep(0.2)
                    if not os.path.exists(bg_image_file_path):
                        messagebox.showerror("Download Error", f"Failed to save {BG_IMAGE_FILE_NAME} at {bg_image_file_path}. Please try again.")
                        self.reset_launcher_state()
                        return
                except Exception as e:
                    messagebox.showerror("Download Error", f"Failed to download bg.jpg: {e}\nPlease check your internet connection and try again.")
                    self.reset_launcher_state()
                    return

            # Step 4: Verify game file integrity (basic check)
            self.update_progress("Verifying game files integrity...", 90)
            # In a real scenario, you might add a checksum verification here for both files
            time.sleep(0.5)

            # Step 5: Launch the game file
            self.update_progress("Starting TurboCraft...", 95)
            try:
                # Execute the downloaded Python script using the current Python interpreter
                self.game_process = subprocess.Popen([sys.executable, game_file_path])
                self.game_start_time = time.time() # Record start time
                self._start_game_timer() # Start the timer updates

                self.update_progress("Launch successful!", 100)
                time.sleep(1) # Give a moment for the game to start

                print(f"--- Launched {GAME_NAME} v{self.selected_version.get()} ---")

            except FileNotFoundError:
                messagebox.showerror("Launch Error", f"Python interpreter or game file '{GAME_FILE_NAME}' not found. Ensure Python is in your PATH and the file exists.")
            except Exception as e:
                messagebox.showerror("Launch Error", f"Failed to launch game: {e}")
            
        except Exception as e:
            messagebox.showerror("Launcher Error", f"An unexpected error occurred during launch process: {e}")
        finally:
            # Note: reset_launcher_state is now called by _start_game_timer when game exits
            # Or if an error occurs before launch.
            pass # No direct call here, controlled by _start_game_timer or error handling above

    def _start_game_timer(self):
        """
        Updates the game session timer and checks if the game process is still running.
        """
        if self.game_process and self.game_process.poll() is None: # Check if game is still running
            elapsed_time = time.time() - self.game_start_time
            hours, remainder = divmod(int(elapsed_time), 3600)
            minutes, seconds = divmod(remainder, 60)
            timer_text = f"Game running: {hours:02}:{minutes:02}:{seconds:02}"
            self.game_timer_label.config(text=timer_text)
            self.timer_id = self.after(1000, self._start_game_timer) # Update every 1 second
        else:
            # Game process has exited
            if self.timer_id:
                self.after_cancel(self.timer_id)
                self.timer_id = None
            self.game_timer_label.config(text="Game not running.")
            self.reset_launcher_state() # Reset launcher state if game exited

    def _download_progress_hook(self, count, block_size, total_size, start_percent, end_percent):
        """
        Callback function for urlretrieve to update download progress for a specific segment.
        """
        if total_size > 0:
            percent_of_segment = int(count * block_size * 100 / total_size)
        else:
            percent_of_segment = 0 # Handle cases where total_size is 0 (e.g., small files)

        # Map the segment's progress (0-100) to the overall progress bar range
        overall_progress = start_percent + (percent_of_segment * (end_percent - start_percent) / 100)
        
        self.update_progress(f"Downloading: {int(percent_of_segment)}%", overall_progress)

    def update_progress(self, text, value):
        """
        Updates the progress bar and label from any thread.
        """
        self.after(0, lambda: self._update_progress_gui(text, value))

    def _update_progress_gui(self, text, value):
        """
        Actual GUI update for progress bar and label. Must be called from main thread.
        """
        self.progress_label.config(text=text)
        self.progress_bar["value"] = value
        self.update_idletasks()

    def reset_launcher_state(self):
        """
        Resets the launcher GUI state after game launch or error.
        """
        # Ensure any running timer is stopped if this is called directly (e.g., on an error)
        if self.timer_id:
            self.after_cancel(self.timer_id)
            self.timer_id = None
        self.game_process = None
        self.game_start_time = None
        self.game_timer_label.config(text="Game not running.") # Reset timer display

        self.after(0, lambda: self._reset_launcher_gui())

    def _reset_launcher_gui(self):
        """
        Actual GUI reset. Must be called from main thread.
        """
        self.progress_bar["value"] = 0
        self.progress_label.config(text="")
        self.play_button_canvas.config(state="normal")
        self.settings_button_canvas.config(state="normal")
        self.exit_button_canvas.config(state="normal")

    def open_settings(self):
        """
        Opens a placeholder settings window.
        """
        settings_window = tk.Toplevel(self)
        settings_window.title("TurboCraft Settings")
        settings_window.geometry("400x350") # Slightly larger
        settings_window.transient(self)
        settings_window.grab_set()

        settings_window.grid_columnconfigure(0, weight=1)
        settings_window.grid_rowconfigure(0, weight=1)

        settings_frame = tk.Frame(settings_window, bg="#25252a", padx=20, pady=20)
        settings_frame.grid(row=0, column=0, sticky="nsew")
        settings_frame.grid_columnconfigure(0, weight=1)

        tk.Label(
            settings_frame,
            text="Game Settings",
            font=("Inter", 20, "bold"),
            fg="#e0e0e0",
            bg="#25252a"
        ).pack(pady=(0, 20))

        tk.Label(
            settings_frame,
            text="Customize your TurboCraft experience here!",
            font=("Inter", 12),
            fg="#cccccc",
            bg="#25252a",
            wraplength=350,
            justify="center"
        ).pack(pady=(0, 10))

        tk.Label(
            settings_frame,
            text="Soon........ Coming In 1.5 Version",
            font=("Inter", 10),
            fg="#909090",
            bg="#25252a",
            wraplength=350,
            justify="center"
        ).pack(pady=(0, 20))

        close_button_canvas = CustomButton(
            settings_frame,
            text="Close",
            command=settings_window.destroy,
            font_size=12,
            bg_color="#7289da",
            hover_color="#677bc4",
            width=100,
            height=40
        )
        close_button_canvas.pack(pady=10)

        # Center the settings window
        self.update_idletasks()
        x = self.winfo_x() + (self.winfo_width() // 2) - (settings_window.winfo_width() // 2)
        y = self.winfo_y() + (self.winfo_height() // 2) - (settings_window.winfo_height() // 2)
        settings_window.geometry(f"+{x}+{y}")


    def quit_launcher(self):
        """
        Exits the launcher application.
        """
        # Using CustomButton for confirmation dialog
        if messagebox.askyesno("Exit Launcher", "Are you sure you want to exit the TurboCraft Launcher?"):
            self.destroy()

# --- Run the Launcher ---
if __name__ == "__main__":
    app = TurboCraftLauncher()
    app.mainloop()
