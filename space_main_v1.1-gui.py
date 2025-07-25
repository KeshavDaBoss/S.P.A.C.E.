##Added Graphical User Interface (GUI) for S.P.A.C.E. Launcher


import customtkinter as ctk
from PIL import Image
import subprocess
import os
import sys

# Self-aware file paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOGO_PATH = os.path.join(BASE_DIR, "logo.png")
ICON_PATH = os.path.join(BASE_DIR, "logo.ico")
GESTURE_SCRIPT = os.path.join(BASE_DIR, "space_main_v1.py")

# App appearance
APP_TITLE = "S.P.A.C.E."
APP_WIDTH, APP_HEIGHT = 500, 400

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

class SpaceLauncher(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title(APP_TITLE)
        self.geometry(f"{APP_WIDTH}x{APP_HEIGHT}")
        self.resizable(False, False)

        if os.name == "nt" and os.path.exists(ICON_PATH):
            try:
                self.iconbitmap(ICON_PATH)
            except Exception:
                print("Icon failed to load.")

        self.process = None

        # Logo display fix with PIL Image
        try:
            pil_image = Image.open(LOGO_PATH)
            self.logo_image = ctk.CTkImage(pil_image, size=(150, 150))
            ctk.CTkLabel(self, image=self.logo_image, text="").pack(pady=(30, 10))
        except Exception as e:
            ctk.CTkLabel(self, text="[Logo missing]", font=ctk.CTkFont(size=14)).pack(pady=(30, 10))
            print(f"Logo error: {e}")

        # App title
        ctk.CTkLabel(self, text="S.P.A.C.E.", font=ctk.CTkFont("Segoe UI", 28, "bold")).pack(pady=5)

        # Toggle
        self.toggle = ctk.CTkSwitch(
            self,
            text="Activate S.P.A.C.E.",
            command=self.toggle_space,
            font=ctk.CTkFont(size=18),
            switch_width=60,
            switch_height=30,
            progress_color="green"
        )
        self.toggle.pack(pady=40)

        # Exit button
        ctk.CTkButton(self, text="Exit Launcher", command=self.exit_launcher, corner_radius=20).pack(pady=10)

    def toggle_space(self):
        if self.toggle.get():
            self.start_space()
        else:
            self.stop_space()

    def start_space(self):
        if self.process is None:
            if not os.path.exists(GESTURE_SCRIPT):
                print("ERROR: space_main_v1.py not found.")
                return
            try:
                self.process = subprocess.Popen(
                    [sys.executable, GESTURE_SCRIPT],
                    creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0
                )
                print("S.P.A.C.E. activated.")
            except Exception as e:
                print(f"Failed to start: {e}")

    def stop_space(self):
        if self.process:
            try:
                if os.name == "nt":
                    subprocess.call(['taskkill', '/F', '/PID', str(self.process.pid)])
                else:
                    self.process.terminate()
                print("S.P.A.C.E. stopped.")
            except Exception as e:
                print(f"Failed to stop: {e}")
            self.process = None

    def exit_launcher(self):
        self.stop_space()
        self.destroy()

if __name__ == "__main__":
    app = SpaceLauncher()
    app.mainloop()
