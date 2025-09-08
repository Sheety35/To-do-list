import tkinter as tk
import os

class ToDoApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("📝 Swipeable To-Do List")
        self.configure(bg="white")
        self.resizable(False, False)
        
        # ... (window geometry setup is fine here) ...
        self.window_width = 320
        self.window_height = 500
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x_offset = screen_width - self.window_width
        y_offset = screen_height - self.window_height - 50
        self.geometry(f"{self.window_width}x{self.window_height}+{x_offset}+{y_offset}")

        # --- MOVED THIS SECTION UP ---
        # Define the save location and file paths FIRST
        self.save_directory = os.path.join(os.path.expanduser("~"), "Desktop") 
        os.makedirs(self.save_directory, exist_ok=True) # Create if it doesn't exist

        self.task_files = {
            "office": os.path.join(self.save_directory, "office_tasks.txt"),
            "personal": os.path.join(self.save_directory, "personal_tasks.txt")
        }
        # --- END OF MOVED SECTION ---

        self.current_page = "office"  # default
        self.task_data = {"office": [], "personal": []}

        # NOTE: The redundant, incorrect definition of self.task_files has been removed.

        self.bind("<Left>", lambda e: self.switch_page("office"))
        self.bind("<Right>", lambda e: self.switch_page("personal"))

        # Now, these calls will use the correct file paths
        self.build_ui()
        self.load_tasks()
        self.update_tasks()

        # Save tasks on closing app
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Swipe detection variables
        self.start_x = None
        self.start_y = None
        # Bind mouse press and release events for swipe detection
        self.bind("<ButtonPress-1>", self.on_press)
        self.bind("<ButtonRelease-1>", self.on_release)

    def build_ui(self):
        # Header
        self.header = tk.Label(self, text="", font=("Helvetica", 20, "bold"), bg="white")
        self.header.pack(pady=10)

        # Entry
        self.entry = tk.Entry(self, font=("Segoe UI", 12))
        self.entry.pack(padx=10, pady=(0, 10), fill="x")
        self.entry.bind("<Return>", lambda e: self.add_task())

        self.add_btn = tk.Button(self, text="Add Task", command=self.add_task,
                                 bg="#4CAF50", fg="white", font=("Segoe UI", 12, "bold"))
        self.add_btn.pack(padx=10, pady=(0, 10), fill="x")

        # Scrollable task area
        self.task_frame = tk.Frame(self, bg="white")
        self.task_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        self.canvas = tk.Canvas(self.task_frame, bg="white", highlightthickness=0)
        self.scrollbar = tk.Scrollbar(self.task_frame, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas, bg="white")

        self.scrollable_frame.bind(
            "<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

    def switch_page(self, page):
        if page not in self.task_data:
            return
        self.save_tasks()  # Save before switching
        self.current_page = page
        self.load_tasks()
        self.update_tasks()

    def add_task(self):
        task_text = self.entry.get().strip()
        if task_text:
            self.task_data[self.current_page].append((task_text, False))
            self.entry.delete(0, tk.END)
            self.update_tasks()
            self.save_tasks()

    def toggle_task(self, index):
        task, completed = self.task_data[self.current_page][index]
        self.task_data[self.current_page][index] = (task, not completed)
        self.update_tasks()
        self.save_tasks()

    def delete_task(self, index):
        del self.task_data[self.current_page][index]
        self.update_tasks()
        self.save_tasks()

    def update_tasks(self):
        # Clear UI
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        # Update header
        self.header.config(text=f"{self.current_page.capitalize()} Tasks")

        for idx, (task, completed) in enumerate(self.task_data[self.current_page]):
            row = tk.Frame(self.scrollable_frame, bg="white")
            row.pack(fill="x", pady=3)

            circle_text = "●" if completed else "◯"
            circle_color = "#4CAF50" if completed else "gray"

            dot = tk.Button(row, text=circle_text, font=("Helvetica", 14),
                            fg=circle_color, bg="white", bd=0,
                            command=lambda i=idx: self.toggle_task(i))
            dot.pack(side="left")

            label_bg = "#d4f4dd" if completed else "white"
            label = tk.Label(row, text=task, font=("Segoe UI", 12), bg=label_bg,
                             fg="black", anchor="w")
            label.pack(side="left", fill="x", expand=True, padx=10)

            del_btn = tk.Button(row, text="🗑", font=("Segoe UI", 10),
                                bg="#ff4d4d", fg="white",
                                command=lambda i=idx: self.delete_task(i))
            del_btn.pack(side="right", padx=5)

    def load_tasks(self):
        file = self.task_files[self.current_page]
        self.task_data[self.current_page] = []
        if os.path.exists(file):
            with open(file, "r", encoding="utf-8") as f:
                lines = f.readlines()
            for line in lines:
                line = line.strip()
                if "|" in line:
                    text, completed_str = line.split("|", 1)
                    completed = completed_str == "True"
                    self.task_data[self.current_page].append((text, completed))

    def save_tasks(self):
        file = self.task_files[self.current_page]
        with open(file, "w", encoding="utf-8") as f:
            for task, completed in self.task_data[self.current_page]:
                f.write(f"{task}|{completed}\n")

    def on_press(self, event):
        self.start_x = event.x_root  # Use root coords for absolute screen position
        self.start_y = event.y_root

    def on_release(self, event):
        if self.start_x is None or self.start_y is None:
            return

        dx = event.x_root - self.start_x
        dy = event.y_root - self.start_y

        # You can uncomment these to debug swipe distances in your terminal
        # print(f"Swipe dx: {dx}, dy: {dy}")

        # Horizontal swipe (left/right)
        if abs(dx) > 50 and abs(dx) > abs(dy):
            if dx > 0:
                # Swipe right → switch to office page
                self.switch_page("office")
            else:
                # Swipe left → switch to personal page
                self.switch_page("personal")

        # Vertical swipe (down) to close app
        elif dy > 100 and abs(dy) > abs(dx):
            self.on_closing()

        # Reset start coords
        self.start_x = None
        self.start_y = None

    def on_closing(self):
        self.save_tasks()  # Save before closing
        self.destroy()

if __name__ == "__main__":
    app = ToDoApp()
    app.mainloop()
