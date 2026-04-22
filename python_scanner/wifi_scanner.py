import tkinter as tk
from tkinter import ttk
import subprocess, re, threading, time

class WifiScannerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("WiFi Network Scanner")
        self.root.geometry("600x450")
        self.root.configure(bg="#f0f0f0")
        self.networks = {}
        self.setup_ui()
        threading.Thread(target=self.continuous_scan, daemon=True).start()
        self.refresh_ui_list()

    def setup_ui(self):
        header = tk.Frame(self.root, bg="#2ecc71", pady=10)
        header.pack(fill=tk.X)
        tk.Label(header, text="WiFi Scanner", fg="white", bg="#2ecc71", font=("Helvetica", 14, "bold")).pack()
        self.tree = ttk.Treeview(self.root, columns=("ssid", "signal"), show="headings")
        self.tree.heading("ssid", text="Network Name (SSID)"); self.tree.heading("signal", text="Signal Strength")
        self.tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    def continuous_scan(self):
        while True:
            try:
                out = subprocess.check_output("netsh wlan show networks mode=bssid", shell=True).decode('utf-8', errors='ignore')
                found = re.findall(r"SSID \d+ : (.*?)\r\n.*?Signal\s+: (\d+)%", out, re.DOTALL)
                for ssid, signal in found: self.networks[ssid or "Hidden"] = signal + "%"
                time.sleep(5)
            except: time.sleep(5)

    def refresh_ui_list(self):
        for i in self.tree.get_children(): self.tree.delete(i)
        for s, sig in self.networks.items(): self.tree.insert("", tk.END, values=(s, sig))
        self.root.after(2000, self.refresh_ui_list)

if __name__ == "__main__":
    root = tk.Tk()
    app = WifiScannerApp(root)
    root.mainloop()
