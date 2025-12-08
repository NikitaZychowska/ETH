import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import numpy as np
import tkinter as tk
from tkinter import filedialog
import sys

#put map file in the same folder-later I will crate pop up window for that
MAP_PATH = '/home/nikita/Projects/ETH/map geo.jpg'

class MapReader:
    def __init__(self, image_path):
        try:
            self.image = mpimg.imread(image_path)
            self.height, self.width = self.image.shape[:2]
        except FileNotFoundError:
            print(f"ERROR: Could not find file {image_path}")
            return

        # this dictionary will store your custom legend
        #format: {(R, G, B): "Rock Name"}
        self.custom_legend = {}

        self.fig, self.ax = plt.subplots(figsize=(10, 8))
        self.ax.imshow(self.image)
        self.ax.set_title("TRAINING MODE: Please check the Console")
        self.ax.axis('on')
        
        #show window, but allow code to continue running (block=False)
        plt.show(block=False)
        
        #start the training
        self.train_legend()

        #after training,start to Analysis mode
        self.start_analysis()

    def get_pixel_color(self, x, y):
        """Helper to safely get color from image"""
        x, y = int(x), int(y)
        if 0 <= x < self.width and 0 <= y < self.height:
            pixel = self.image[y, x]
            # Convert to 0-255 integers
            if pixel.max() <= 1.0:
                pixel = (pixel * 255).astype(int)
            return tuple(pixel[:3]) #return (R, G, B)
        return None

    def train_legend(self):
        """
        This function asks the user to click on the legend to learn the colors.
        """
        print("\n" + "="*40)
        print("PHASE 1: CREATE THE LEGEND")
        print("="*40)
        print("We need to teach the computer what your colors mean.")
        
        while True:
            print("\nOption A: Click on a color box in the map LEGEND.")
            print("Option B: Click the Middle Mouse Button (or press Enter in console) to finish.")
            print("Waiting for click...")
            
            #ginput(1) waits for 1 click from the user
            #timeout=-1 means wait forever until click
            pts = plt.ginput(n=1, timeout=-1)
            
            #if user clicked middle mouse button or pressed stop, pts will be empty
            if not pts:
                break
                
            x, y = pts[0]
            
           #show wheere x
            self.ax.plot(x, y, 'bx', markersize=10)
            self.fig.canvas.draw()
            
            #downloand color
            color = self.get_pixel_color(x, y)
            print(f"Color: {color}")

            name = input("Write rock name (or write STOP or EXIT to finish): ")
            
            # Sprawdzenie wyjścia
            if name.strip().upper() in ["STOP", "EXIT"]:
                print("End learning of map")
                break
            
            if name.strip() != "":
                self.custom_legend[color] = name
                print(f"Saved: {name}")

        print("\n" + "="*40)
        print("PHASE 2: ANALYSIS READY")
        print(f"Learned {len(self.custom_legend)} rock types.")
        print("="*40)

    def start_analysis(self):
        """
        Switches to normal mode where clicking identifies rocks.
        """
        self.ax.clear() 
        self.ax.imshow(self.image)
        self.ax.set_title("PHASE 2:Analize")
        self.ax.axis('on')
        self.fig.canvas.draw()
        
        #connect the standard click event
        self.cid = self.fig.canvas.mpl_connect('button_press_event', self.onclick)
        
        #keep window open
        plt.show()

    def onclick(self, event):
        """Standard analysis click"""
        if event.inaxes != self.ax: return

        x, y = int(event.xdata), int(event.ydata)
        
        #draw red dot
        self.ax.plot(x, y, 'ro', markersize=5)
        self.fig.canvas.draw()

        #identify rock
        clicked_color = self.get_pixel_color(x, y)
        if clicked_color:
            self.identify_rock(clicked_color)

    def identify_rock(self, target_rgb):
        """Find closest match in our NEW custom legend"""
        r, g, b = target_rgb
        min_dist = float('inf')
        best_name = "Unknown"

        for legend_rgb, name in self.custom_legend.items():
            lr, lg, lb = legend_rgb
            dist = np.sqrt((r-lr)**2 + (g-lg)**2 + (b-lb)**2)
            
            if dist < min_dist:
                min_dist = dist
                best_name = name
        
        print("-" * 30)
        print(f"Color: {target_rgb}")
        if min_dist < 60: #tolerance
            print(f"RESULT: {best_name.upper()}")
        else:
            print("RESULT: No matching color found in your legend.")
        print("-" * 30)

def select_file_window():
    root = tk.Tk()
    root.withdraw()
    path = filedialog.askopenfilename(title="Wybierz mapę", filetypes=[("Obrazy", "*.jpg *.png *.jpeg")])
    root.destroy()
    return path

if __name__ == "__main__":
    path = select_file_window()
    if path:
        app = MapReader(path)