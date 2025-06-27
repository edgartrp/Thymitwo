import threading
import time
import numpy as np
import ultra_map
import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt

# --- Fonction de mise  jour des donnes ---
class ScannerThread(threading.Thread):
    def __init__(self, update_callback, interval=0.5):
        super().__init__(daemon=True)
        self.update_callback = update_callback
        self.interval = interval

    def run(self):
        while True:
            readings = ultra_map.scan_environment()  # [(angle, dist_mm), ...]
            angles = np.deg2rad([a for a, _ in readings])
            dists  = [d/1000 for _, d in readings]  # convertir en mtres
            self.update_callback(angles, dists)
            time.sleep(self.interval)

# --- GUI principale ---
class RadarGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Radar Ultrason  Robot")
        
        # Cration de la figure polaire
        self.fig = plt.Figure(figsize=(5,5))
        self.ax  = self.fig.add_subplot(111, projection='polar')
        self.ax.set_theta_zero_location("N")
        self.ax.set_theta_direction(-1)
        self.ax.set_rlim(0, 2)  # jusqu' 2 m
        
        # Canvas Matplotlib dans Tk
        self.canvas = FigureCanvasTkAgg(self.fig, master=root)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # Dmarrage du thread de scan
        ScannerThread(self.update_plot, interval=0.2).start()

    def update_plot(self, angles, distances):
        # Cette mthode est appele dans le thread de scan
        # Pour scurit, on passe par 'after' de Tkinter
        def redraw():
            self.ax.clear()
            self.ax.set_theta_zero_location("N")
            self.ax.set_theta_direction(-1)
            self.ax.set_rlim(0, 2)
            self.ax.scatter(angles, distances)
            self.ax.set_title("Position des obstacles (m)")
            self.canvas.draw()
        self.root.after(0, redraw)

if __name__ == "__main__":
    root = tk.Tk()
    app = RadarGUI(root)
    root.mainloop()
