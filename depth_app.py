import serial
import serial.tools.list_ports
import tkinter as tk
from tkinter import ttk, messagebox
import threading
import os
import sys

OUTPUT_FILE = "depth.txt"
OUTPUT_FORMAT = "Βάθος: {:.2f} m"

class DepthApp:
    def __init__(self):
        self.running = False
        self.serial_conn = None

        self.root = tk.Tk()
        self.root.title("Depth Counter v1.0")
        self.root.geometry("320x280")
        self.root.resizable(False, False)

        tk.Label(self.root, text="COM Port:", font=("Arial", 11)).pack(pady=(15,2))
        self.port_var = tk.StringVar()
        self.port_combo = ttk.Combobox(self.root, textvariable=self.port_var, width=20)
        self.port_combo['values'] = self.get_ports()
        if self.port_combo['values']:
            self.port_combo.current(0)
        self.port_combo.pack()

        tk.Button(self.root, text="🔄 Ανανέωση Ports",
                  command=self.refresh_ports).pack(pady=4)

        tk.Button(self.root, text="↺ Μηδενισμός βάθους",
                  command=self.reset_depth,
                  bg="#FF8C00", fg="white", font=("Arial", 10)).pack(pady=4)

        self.btn = tk.Button(self.root, text="▶ ΕΝΑΡΞΗ",
                             command=self.toggle,
                             bg="#228B22", fg="white",
                             font=("Arial", 12, "bold"), width=18)
        self.btn.pack(pady=8)

        self.depth_label = tk.Label(self.root, text="--- m",
                                    font=("Arial", 22, "bold"), fg="#003580")
        self.depth_label.pack(pady=4)

        self.status_label = tk.Label(self.root, text="● Σε αναμονή",
                                     font=("Arial", 9), fg="gray")
        self.status_label.pack()

        self.write_to_file("---")
        self.root.mainloop()

    def get_ports(self):
        return [p.device for p in serial.tools.list_ports.comports()]

    def refresh_ports(self):
        self.port_combo['values'] = self.get_ports()

    def reset_depth(self):
        if self.serial_conn and self.serial_conn.is_open:
            self.serial_conn.write(b'R')

    def toggle(self):
        if not self.running:
            self.start()
        else:
            self.stop()

    def start(self):
        port = self.port_var.get()
        if not port:
            messagebox.showerror("Σφάλμα", "Επίλεξε COM port!")
            return
        try:
            self.serial_conn = serial.Serial(port, 9600, timeout=1)
            self.running = True
            self.btn.config(text="⏹ ΔΙΑΚΟΠΗ", bg="#8B0000")
            self.status_label.config(text=f"● Συνδεδεμένο σε {port}", fg="green")
            threading.Thread(target=self.read_loop, daemon=True).start()
        except Exception as e:
            messagebox.showerror("Σφάλμα σύνδεσης", str(e))

    def stop(self):
        self.running = False
        if self.serial_conn:
            self.serial_conn.close()
        self.btn.config(text="▶ ΕΝΑΡΞΗ", bg="#228B22")
        self.status_label.config(text="● Αποσυνδέθηκε", fg="gray")
        self.write_to_file("---")

    def read_loop(self):
        while self.running:
            try:
                line = self.serial_conn.readline().decode('utf-8').strip()
                if line:
                    depth = float(line)
                    text = OUTPUT_FORMAT.format(depth)
                    self.write_to_file(text)
                    self.root.after(0, self.depth_label.config, {"text": f"{depth:.2f} m"})
            except:
                pass

    def write_to_file(self, text):
        path = os.path.join(
            os.path.dirname(sys.executable)
            if getattr(sys, 'frozen', False)
            else os.path.dirname(os.path.abspath(__file__)),
            OUTPUT_FILE)
        with open(path, 'w', encoding='utf-8') as f:
            f.write(text)

if __name__ == "__main__":
    DepthApp()