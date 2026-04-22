import tkinter as tk
import subprocess
import os
import sys

class MainLauncher:
    def __init__(self, root):
        self.root = root
        self.root.title("Nearby Detector Launcher")
        self.root.geometry("400x300")
        self.root.configure(bg="#2c3e50")

        tk.Label(self.root, text="Nearby Device Detector", fg="white", bg="#2c3e50", font=("Helvetica", 16, "bold"), pady=20).pack()

        btn_frame = tk.Frame(self.root, bg="#2c3e50")
        btn_frame.pack(expand=True)

        tk.Button(btn_frame, text="Open Full Scanner", command=lambda: self.run_file("scanner_gui.py"), width=25, height=2, bg="#3498db", fg="white", font=("Helvetica", 10, "bold")).pack(pady=10)
        tk.Button(btn_frame, text="Open Bluetooth Only", command=lambda: self.run_file("bluetooth_scanner.py"), width=25, height=2, bg="#9b59b6", fg="white", font=("Helvetica", 10, "bold")).pack(pady=10)
        tk.Button(btn_frame, text="Open WiFi Only", command=lambda: self.run_file("wifi_scanner.py"), width=25, height=2, bg="#2ecc71", fg="white", font=("Helvetica", 10, "bold")).pack(pady=10)

    def run_file(self, filename):
        file_path = os.path.join(os.path.dirname(__file__), filename)
        subprocess.Popen([sys.executable, file_path])

if __name__ == "__main__":
    root = tk.Tk()
    app = MainLauncher(root)
    root.mainloop()
