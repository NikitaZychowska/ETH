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

    #def start_analysis(self):
 
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
