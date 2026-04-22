import asyncio
import threading
import tkinter as tk
from tkinter import ttk, messagebox
from bleak import BleakScanner

class BluetoothScannerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Bluetooth BLE Scanner")
        self.root.geometry("600x450")
        self.root.configure(bg="#f0f0f0")
        self.devices = {}
        self.setup_ui()
        threading.Thread(target=self.start_async_loop, daemon=True).start()
        self.refresh_ui_list()

    def setup_ui(self):
        header = tk.Frame(self.root, bg="#3498db", pady=10)
        header.pack(fill=tk.X)
        tk.Label(header, text="Bluetooth Scanner", fg="white", bg="#3498db", font=("Helvetica", 14, "bold")).pack()
        self.tree = ttk.Treeview(self.root, columns=("name", "address", "rssi"), show="headings")
        self.tree.heading("name", text="Device Name"); self.tree.heading("address", text="MAC Address"); self.tree.heading("rssi", text="Signal (RSSI)")
        self.tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    def start_async_loop(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        self.loop.run_until_complete(self.continuous_scan())

    async def continuous_scan(self):
        while True:
            try:
                data = await BleakScanner.discover(timeout=5.0, return_adv=True)
                for d, adv in data.values():
                    self.devices[d.address] = {"name": d.name or "Unknown", "address": d.address, "rssi": adv.rssi}
                await asyncio.sleep(2)
            except: await asyncio.sleep(5)

    def refresh_ui_list(self):
        for i in self.tree.get_children(): self.tree.delete(i)
        for a, v in sorted(self.devices.items(), key=lambda x: x[1]['rssi'], reverse=True):
            self.tree.insert("", tk.END, values=(v['name'], a, v['rssi']))
        self.root.after(2000, self.refresh_ui_list)

if __name__ == "__main__":
    root = tk.Tk()
    app = BluetoothScannerApp(root)
    root.mainloop()
