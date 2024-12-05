import tkinter as tk
import customtkinter as ctk
from tkinter import filedialog, messagebox
import zipfile
import os
from tkinter import ttk

# Define the InfiniteGrid class for the grid functionality
class InfiniteGrid(ctk.CTkCanvas):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        self.scale_factor = 1.0
        self.max_scale_factor = 0.85
        self.min_scale_factor = 0.25
        self.grid_size = 50
        self.pan_offset_x = 0
        self.pan_offset_y = 0

        self.pan_limit_x = 5000
        self.pan_limit_y = 5000

        self.last_mouse_pos = None

        self.bind("<ButtonPress-1>", self.mouse_press)
        self.bind("<B1-Motion>", self.mouse_move)
        self.bind("<ButtonRelease-1>", self.mouse_release)
        self.bind("<MouseWheel>", self.wheel_event)

        self.draw_grid()

    def draw_grid(self):
        """Draw the grid based on current zoom and pan."""
        self.delete("grid")
        grid_size = int(self.grid_size * self.scale_factor)

        for x in range(self.pan_offset_x - self.pan_limit_x, self.pan_offset_x + self.pan_limit_x, grid_size):
            self.create_line(x, -self.pan_limit_y, x, self.pan_limit_y, tags="grid", fill="lightgrey")

        for y in range(self.pan_offset_y - self.pan_limit_y, self.pan_offset_y + self.pan_limit_y, grid_size):
            self.create_line(-self.pan_limit_x, y, self.pan_limit_x, y, tags="grid", fill="lightgrey")

    def wheel_event(self, event):
        zoom_in_factor = 1.25
        zoom_out_factor = 0.8
        zoom_factor = zoom_in_factor if event.delta > 0 else zoom_out_factor
        new_scale_factor = self.scale_factor * zoom_factor

        if self.min_scale_factor <= new_scale_factor <= self.max_scale_factor:
            self.scale_factor = new_scale_factor
            self.draw_grid()

    def mouse_press(self, event):
        self.last_mouse_pos = (event.x, event.y)
        self.config(cursor="fleur")

    def mouse_move(self, event):
        if self.last_mouse_pos:
            dx = event.x - self.last_mouse_pos[0]
            dy = event.y - self.last_mouse_pos[1]

            self.pan_offset_x = max(min(self.pan_offset_x + dx, self.pan_limit_x), -self.pan_limit_x)
            self.pan_offset_y = max(min(self.pan_offset_y + dy, self.pan_limit_y), -self.pan_limit_y)

            self.draw_grid()
            self.last_mouse_pos = (event.x, event.y)

    def mouse_release(self, event):
        self.config(cursor="arrow")
        self.last_mouse_pos = None


# Main Window class
class MainWindow(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("VSmesh: Visual Scripting Modular Extensible System for Holography")
        self.geometry("1200x800")

        # Create the top tab system (Notebook)
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True)

        # Create a frame to hold the grid and panels
        self.tabs = {}

        # Add a default first tab (visual script)
        self.add_tab("Script 1")

        # Create the menu bar
        self.create_menu()

    def add_tab(self, name):
        """Add a new tab with a unique name."""
        frame = ctk.CTkFrame(self.notebook)
        self.notebook.add(frame, text=name)

        # Create the left panel (dark panel)
        left_panel = ctk.CTkFrame(frame, width=200, height=800, corner_radius=0, fg_color="gray15")
        left_panel.grid(row=0, column=0, sticky="ns")

        # Add a read-only text box to the left panel
        left_textbox = ctk.CTkTextbox(left_panel, width=200, height=800, fg_color="gray15", state="disabled", wrap="word", border_color="white", border_width=2)
        left_textbox.pack(fill="both", expand=True)
        left_textbox.insert("1.0", "Left Panel: Functions and Variables")

        # Create the right panel (dark panel)
        right_panel = ctk.CTkFrame(frame, width=200, height=800, corner_radius=0, fg_color="gray15")
        right_panel.grid(row=0, column=2, sticky="ns")

        # Add a read-only text box to the right panel
        right_textbox = ctk.CTkTextbox(right_panel, width=200, height=800, fg_color="gray15", state="disabled", wrap="word", border_color="white", border_width=2)
        right_textbox.pack(fill="both", expand=True)
        right_textbox.insert("1.0", "Right Panel: Generated Code")

        # Create the grid (canvas) for the script
        grid_view = InfiniteGrid(frame, bg="gray20", width=800, height=800)
        grid_view.grid(row=0, column=1, sticky="nsew")

        # Store the tab reference, grid, and panels for each tab
        self.tabs[name] = {"grid": grid_view, "left_panel": left_panel, "right_panel": right_panel}

        # Configure grid column weights for resizing
        frame.grid_columnconfigure(1, weight=1)  # Main grid area
        frame.grid_rowconfigure(0, weight=1)  # Ensure grid resizes properly

    def create_menu(self):
        """Create the menu bar and add options."""
        menubar = tk.Menu(self)

        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="New Script", command=self.new_script)
        file_menu.add_command(label="Save As...", command=self.save_as)
        file_menu.add_command(label="Load", command=self.load_file)
        menubar.add_cascade(label="File", menu=file_menu)

        # Generate Code menu
        generate_menu = tk.Menu(menubar, tearoff=0)
        generate_menu.add_command(label="GDScript", command=lambda: self.generate_code("GDScript"))
        generate_menu.add_command(label="Python", command=lambda: self.generate_code("Python"))
        menubar.add_cascade(label="Generate Code", menu=generate_menu)

        self.config(menu=menubar)

    def generate_code(self, language):
        """Generate code for the selected language."""
        print(f"Generated {language} code.")

    def save_as(self):
        """Save the current state as a .vsm1 file (similar to .sb3)."""
        file_path = filedialog.asksaveasfilename(defaultextension=".vsm1", filetypes=[("VSmesh Files", "*.vsm1")])
        if file_path:
            self.save_to_vsm1(file_path)

    def save_to_vsm1(self, file_path):
        """Save the grid and any data to a .vsm1 file (ZIP format)."""
        try:
            with zipfile.ZipFile(file_path, 'w', zipfile.ZIP_DEFLATED) as vsm1_file:
                # Save each tab as a separate .vs file inside the .vsm1
                for tab_name, tab_data in self.tabs.items():
                    grid_content = f"Generated code for {tab_name}."
                    vsm1_file.writestr(f"{tab_name}.vs", grid_content)

            messagebox.showinfo("Save", "File saved successfully.")
        except Exception as e:
            messagebox.showerror("Error", f"Error saving file: {e}")

    def load_file(self):
        """Load a .vsm1 file."""
        file_path = filedialog.askopenfilename(filetypes=[("VSmesh Files", "*.vsm1")])
        if file_path:
            self.load_from_vsm1(file_path)

    def load_from_vsm1(self, file_path):
        """Load data from a .vsm1 file (ZIP format)."""
        try:
            with zipfile.ZipFile(file_path, 'r') as vsm1_file:
                # Load each script from the .vsm1 file
                for file_name in vsm1_file.namelist():
                    script_data = vsm1_file.read(file_name).decode('utf-8')
                    # Create a new tab for each script in the .vsm1 file
                    self.add_tab(file_name.replace(".vs", ""))
                    print(f"Loaded {file_name}: {script_data}")

            messagebox.showinfo("Load", "File loaded successfully.")
        except Exception as e:
            messagebox.showerror("Error", f"Error loading file: {e}")

    def new_script(self):
        """Create a new script tab."""
        self.add_tab(f"Script {len(self.tabs) + 1}")

# Run the application
if __name__ == "__main__":
    app = MainWindow()  # Create an instance of the main window
    app.mainloop()  # Start the main event loop to display the window
