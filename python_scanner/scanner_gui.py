import asyncio
import threading
import tkinter as tk
from tkinter import ttk, messagebox
from bleak import BleakScanner
import time

class BluetoothScannerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Nearby Detector (Python)")
        self.root.geometry("700x550")
        self.root.configure(bg="#f0f0f0")

        self.devices = {}
        self.is_scanning = True

        self.setup_ui()
        
        self.scan_thread = threading.Thread(target=self.start_async_loop, daemon=True)
        self.scan_thread.start()
        self.refresh_ui_list()

    def setup_ui(self):
        header_frame = tk.Frame(self.root, bg="#2c3e50", pady=10)
        header_frame.pack(fill=tk.X)
        
        self.status_label = tk.Label(header_frame, text="Initializing...", fg="white", bg="#2c3e50", font=("Helvetica", 12, "bold"))
        self.status_label.pack()

        self.count_label = tk.Label(self.root, text="Devices found: 0", bg="#f0f0f0")
        self.count_label.pack()

        list_frame = tk.Frame(self.root, bg="#f0f0f0", padx=10, pady=10)
        list_frame.pack(fill=tk.BOTH, expand=True)

        columns = ("name", "type", "address", "rssi")
        self.tree = ttk.Treeview(list_frame, columns=columns, show="headings")
        self.tree.heading("name", text="Device Name")
        self.tree.heading("type", text="Type")
        self.tree.heading("address", text="Identifier")
        self.tree.heading("rssi", text="Signal (RSSI)")
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.tree.bind("<<TreeviewSelect>>", self.on_device_select)

        self.action_frame = tk.Frame(self.root, bg="#ecf0f1", pady=10)
        self.action_frame.pack(fill=tk.X, padx=10, pady=10)

        self.detail_label = tk.Label(self.action_frame, text="Select a device", bg="#ecf0f1")
        self.detail_label.pack(side=tk.LEFT, padx=10)

        self.connect_btn = tk.Button(self.action_frame, text="Connect", command=self.on_connect_click, bg="#3498db", fg="white", state=tk.DISABLED)
        self.connect_btn.pack(side=tk.RIGHT, padx=10)

    def on_device_select(self, event):
        sel = self.tree.selection()
        if not sel: return
        item = self.tree.item(sel)
        name, dtype, addr, rssi = item["values"]
        
        dist = self.estimate_distance(int(rssi))
        self.detail_label.config(text=f"{name} | {dtype} | {rssi} dBm | ~{dist:.2f}m")
        self.connect_btn.config(state=tk.NORMAL if dtype == "Bluetooth" else tk.DISABLED)

    def estimate_distance(self, rssi):
        if rssi == 0: return -1.0
        return 10 ** ((-59 - rssi) / (10 * 2.5))

    def on_connect_click(self):
        sel = self.tree.selection()
        if not sel: return
        addr = self.tree.item(sel)["values"][2]
        if hasattr(self, 'loop') and self.loop.is_running():
            asyncio.run_coroutine_threadsafe(self.connect_to_device(addr), self.loop)

    async def connect_to_device(self, address):
        from bleak import BleakClient
        try:
            async with BleakClient(address, timeout=10.0) as client:
                if client.is_connected:
                    self.root.after(0, lambda: messagebox.showinfo("Success", f"Connected to {address}"))
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Error", str(e)))

    def start_async_loop(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        self.loop.run_until_complete(self.continuous_scan())

    async def continuous_scan(self):
        while self.is_scanning:
            try:
                self.root.after(0, lambda: self.status_label.config(text="Scanning..."))
                data = await BleakScanner.discover(timeout=5.0, return_adv=True)
                for d, adv in data.values():
                    self.devices[d.address] = {"name": d.name or "Unknown", "address": d.address, "rssi": adv.rssi, "type": "Bluetooth"}
                self.scan_wifi()
                await asyncio.sleep(5)
            except: await asyncio.sleep(5)

    def scan_wifi(self):
        import subprocess, re
        try:
            out = subprocess.check_output("netsh wlan show networks mode=bssid", shell=True).decode('utf-8', errors='ignore')
            nets = re.findall(r"SSID \d+ : (.*?)\r\n.*?Signal\s+: (\d+)%", out, re.DOTALL)
            for s, sig in nets:
                rssi = (int(sig) / 2) - 100
                self.devices[f"wifi_{s}"] = {"name": s or "Hidden", "address": "WiFi", "rssi": int(rssi), "type": "WiFi"}
        except: pass

    def refresh_ui_list(self):
        for i in self.tree.get_children(): self.tree.delete(i)
        for k, v in self.devices.items():
            self.tree.insert("", tk.END, values=(v['name'], v['type'], v['address'], v['rssi']))
        self.count_label.config(text=f"Devices found: {len(self.devices)}")
        self.root.after(2000, self.refresh_ui_list)

if __name__ == "__main__":
    root = tk.Tk()
    app = BluetoothScannerApp(root)
    root.mainloop()
