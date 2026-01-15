import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import numpy as np
import tkinter as tk
from tkinter import filedialog, messagebox
import sys
import re
from tkinter import ttk
import cv2
import os

class MapReader:
    def __init__(self, image_path):
        try:
            self.image = mpimg.imread(image_path)
            self.height, self.width = self.image.shape[:2]
        except Exception as e:
            print(f"ERROR: Could not load image- {str(e)}")
            sys.exit(1)
        
        self.custom_legend = {}
        self.fig, self.ax = plt.subplots(figsize=(12, 8))
        self.ax.imshow(self.image)
        self.ax.set_title("LEGEND: click on color buttoms")
        self.ax.axis('on')
        self.fig.canvas.manager.set_window_title("Geological Map - Legend")
        
        plt.show(block=False)
        print("1. Click on each color swach LEGEND")
        print("2. Type rock name →PRESS ENTER")
        print("Write in console or press middle mouse button to finish")
        
        self.train_legend()
        self.finish_training()
    
    def get_pixel_color(self, x, y):
        """Get color at (x, y) in image coordinates"""
        x, y = int(round(x)), int(round(y))
        if 0 <= x < self.width and 0 <= y < self.height:
            pixel = self.image[y, x]
            if pixel.max() <= 1.0:
                pixel = (pixel * 255).astype(int)
            return tuple(pixel[:3])
        return None
    
    def train_legend(self):
        """User clicks on legend colors to define rock types"""
        while True:
            print("\nClick on a color swatch in the LEGEND (not river!)")
            print("Press anywhere and write STOP to finish")
            pts = plt.ginput(n=1, timeout=-1)
            
            if not pts:
                break
                
            x, y = pts[0]
            self.ax.plot(x, y, 'rx', markersize=12, mew=2)
            self.fig.canvas.draw()
            
            color = self.get_pixel_color(x, y)
            if color is None:
                print("ERROR: Clicked outside map area. Try again.")
                continue
                
            print(f"\nCOLOR DETECTED: {color}")
            name = input("Enter rock name (or 'STOP' to finish): ").strip()
            
            if name.upper() == "STOP":
                print("Finishing...")
                break
                
            if name:
                self.custom_legend[color] = name
                print(f"✅ Saved: {color} → {name}")
            else:
                print("⚠️ Rock name cannot be empty. Skipping.")
    
    def finish_training(self):
        print("\n" + "="*60)
        print("LEGEND TRAINING COMPLETE")
        print(f"Total rock types identified: {len(self.custom_legend)}")
        
        print("\nVERIFIED LEGEND DATA:")
        for color, rock in self.custom_legend.items():
            print(f"  {color} → {rock}")
        
        print("\n" + "="*60)
        print("PROCEED TO STEP 2 (river analysis) when ready")

class ValidationTable:
    def __init__(self, legend, title="Legend Validation"):
        """Create a table for validating legend data using ttk.Treeview"""
        self.legend = legend
        self.root = tk.Tk()
        self.root.title(title)
        self.root.geometry("700x400")
        
        #create Treeview
        self.tree = ttk.Treeview(self.root, columns=("Color", "Rock Name"), show="headings")
        self.tree.heading("Color", text="Color (R, G, B)")
        self.tree.heading("Rock Name", text="Rock Name")
        self.tree.pack(fill="both", expand=True, padx=10, pady=10)
        
        #insert data into Treeview
        for color, rock in legend.items():
            self.tree.insert("", "end", values=(f"({color[0]}, {color[1]}, {color[2]})", rock))
        
        #possible eidt - to FIX IT NOT WORKING
        self.tree.bind("<Double-1>", self.on_double_click)
        
        #add buttons
        btn_frame = tk.Frame(self.root)
        btn_frame.pack(pady=10)
        
        tk.Button(
            btn_frame, 
            text="Confirm & Proceed", 
            command=self.confirm,
            bg="#4CAF50", 
            fg="white",
            padx=10
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            btn_frame, 
            text="Fix Color", 
            command=self.fix_color,
            bg="#FF9800", 
            fg="white",
            padx=10
        ).pack(side=tk.LEFT, padx=5)
        
        self.root.mainloop()
    
    def on_double_click(self, event):
        # NEED TO FIX IT
        item = self.tree.identify_row(event.y)
        column = self.tree.identify_column(event.x)
        
        if item and column != "#1":  # Only allow editing Rock Name column
            self.edit_cell(item, column)
    
    def edit_cell(self, item, column):
        col_idx = int(column[1:]) - 1
        current_value = self.tree.item(item, "values")[col_idx]
        
        #menu
        entry = tk.Entry(self.tree, width=20)
        entry.insert(0, current_value)
        entry.focus()
        entry.bind("<Return>", lambda e: self.save_edit(item, col_idx, entry.get()))
        entry.bind("<FocusOut>", lambda e: self.save_edit(item, col_idx, entry.get()))
        
        #position entry
        x, y, width, height = self.tree.bbox(item, column)
        entry.place(x=x, y=y, width=width, height=height)
    
    def save_edit(self, item, col_idx, new_value):
        values = list(self.tree.item(item, "values"))
        values[col_idx] = new_value
        self.tree.item(item, values=values)
    
    def confirm(self):
        new_legend = {}
        for item in self.tree.get_children():
            color_str, rock_name = self.tree.item(item, "values")
            try:
                r, g, b = map(int, re.findall(r'\d+', color_str))
                new_legend[(r, g, b)] = rock_name
            except:
                continue
        
        self.legend = new_legend
        self.root.destroy()
    
    def fix_color(self):
        messagebox.showinfo(
            "Fix Color",
            "To correct a color:\n\n"
            "1.Go back to the legend training step\n"
            "2.Click on the correct color swatch in the legend\n"
            "3.Enter the rock name\n"
            "4.Press 'STOP' to finish\n\n"
            "Note: Colors are determined by the map image. You cannot edit the color value directly."
        )

def select_file_window():
    root = tk.Tk()
    root.withdraw()
    path = filedialog.askopenfilename(
        title="Select Geological Map",
        filetypes=[
            ("TIFF Files", "*.tif *.tiff"),
            ("Image Files", "*.jpg *.jpeg *.png *.bmp")
        ]
    )
    root.destroy()
    return path

class RiverAnalyzer:
    """FInd river by loooking for blue pixels in raster map (R<100, G<100, B>150)"""
    def __init__(self, image, legend):
        self.image = image
        self.legend = legend
        self.height, self.width = image.shape[:2]
        self.river_mask = None
        self.adjacent_rocks = set()
        
        self.image_8bit = (image * 255).astype(np.uint8) if image.max() <= 1.0 else image
        
        if self.image_8bit.ndim == 2:
            self.image_8bit = np.stack([self.image_8bit]*3, axis=-1)
        elif self.image_8bit.shape[2] > 3:
            self.image_8bit = self.image_8bit[..., :3]
    
    def detect_river(self):
        """Identify river pixels by scanning for blue (R<100, G<100, B>150)"""
        #create a mask of zeros (same size as image)
        mask = np.zeros((self.height, self.width), dtype=np.uint8)
        
        for i in range(self.height):
            for j in range(self.width):
                r, g, b = self.image_8bit[i, j]
                #check if pixel is blue (B dominant, R/G low)
                if b > 150 and r < 100 and g < 100:
                    mask[i, j] = 255
        
        #connect river segments
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
        self.river_mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
        
        return self.river_mask
    
    def find_adjacent_rocks(self):
        """Find rock types adjacent to river features"""
        if self.river_mask is None:
            self.detect_river()
        
        #process neighbors for all river pixels - like cnn alli pixels next to
        for i in range(1, self.height-1):
            for j in range(1, self.width-1):
                if self.river_mask[i, j] > 0:
                    #check 8 neighbors pixels
                    for di in (-1, 0, 1):
                        for dj in (-1, 0, 1):
                            if di == 0 and dj == 0:
                                continue
                            ni, nj = i + di, j + dj
                            if self.river_mask[ni, nj] == 0:  #there is not river
                                color = tuple(self.image_8bit[ni, nj])
                                if color in self.legend:
                                    self.adjacent_rocks.add(self.legend[color])
        
        return self.adjacent_rocks
    
    def report_results(self):
        """Display river analysis results"""
        print("RIVER ANALYSIS COMPLETE")
        print("~River features detected by direct blue pixel scan (B>150, R<100, G<100)~")
        
        if self.adjacent_rocks:
            print(f"Rivers are adjacent to these rock types:")
            for rock in sorted(self.adjacent_rocks):
                print(f"  - {rock}")
        else:
            print("No rock types found adjacent to rivers. Possible causes:")
            print("1. River color not detected (adjust thresholds)")
            print("2. River not connected to any rock features")
            print("3. River features too small for detection")
        print("_"*60)

class RockDistanceTable:
    """Calculates rock distances from river and creates a table of results (within 50m threshold)"""
    def __init__(self, image, river_mask, legend, scale_m_per_pixel=1.0, max_distance_m=50.0):
        """
        image: Loaded map image (numpy array)
        river_mask: River mask from RiverAnalyzer (0-255)
        legend: Custom rock legend dictionary (color -> rock name)
        scale_m_per_pixel: Conversion factor (1 pixel = ? meters)
        max_distance_m: Maximum distance to include (meters)
        """
        self.image = image
        self.river_mask = river_mask
        self.legend = legend
        self.height, self.width = image.shape[:2]
        self.scale_m_per_pixel = scale_m_per_pixel
        self.max_distance_m = max_distance_m
        
        #convert river_mask to binary -> distance transform
        river_binary = (river_mask > 0).astype(np.uint8)
        
        #compute distance transform
        self.distance_transform = cv2.distanceTransform(
            river_binary, 
            cv2.DIST_L2, 
            5
        )
        
        #store rock distances
        self.rock_distances = {}
        
        #all pixels
        for i in range(self.height):
            for j in range(self.width):
                #skip river pixels
                if river_mask[i, j] > 0:
                    continue
                
                #get pixel color
                pixel_color = tuple(image[i, j][:3])
                
                #check if this is a rock in our legend
                if pixel_color in legend:
                    rock_name = legend[pixel_color]
                    distance_pixel = self.distance_transform[i, j]
                    
                    #store distance in pixels (for later conversion)
                    if rock_name not in self.rock_distances:
                        self.rock_distances[rock_name] = []
                    
                    self.rock_distances[rock_name].append(distance_pixel)
    
    def generate_table(self):
        """Generate formatted table of rocks within max_distance_m from river"""
        table = []
        table.append("ROCK DISTANCE ANALYSIS (within {} meters, scale: {} m/pixel)".format(self.max_distance_m, self.scale_m_per_pixel))
        table.append("Rock name and distance from river (meters):")
        
        #convert pixel distances to meters and filter
        filtered_rock_distances = {}
        for rock_name, distances_pixel in self.rock_distances.items():
            for d_pixel in distances_pixel:
                d_m = d_pixel * self.scale_m_per_pixel
                if d_m <= self.max_distance_m:
                    if rock_name not in filtered_rock_distances:
                        filtered_rock_distances[rock_name] = []
                    filtered_rock_distances[rock_name].append(d_m)
        
        if not filtered_rock_distances:
            table.append("No rocks found within {} meters of the river.".format(self.max_distance_m))
            return table
        
        #sort by rock name
        rock_names = sorted(filtered_rock_distances.keys())
        
        #add header
        table.append("Rock Name\tMin Distance (m)\tAvg Distance (m)\tCount")
        table.append("-"*60)
        
        #add data rows
        for rock_name in rock_names:
            distances = filtered_rock_distances[rock_name]
            min_dist = min(distances)
            avg_dist = sum(distances) / len(distances)
            count = len(distances)
            
            table.append(f"{rock_name}\t{min_dist:.2f}\t{avg_dist:.2f}\t{count}")
        
        table.append("="*60)
        return table
    
    def print_table(self):
        for line in self.generate_table():
            print(line)

def get_map_scale():
    """Get map scale input from user (meters per pixel)"""
    print("ENTER MAP SCALE (meters per pixel)")
    print("Example: 1 pixel = 10 meters → enter 10.0")
    print("If unsure, press Enter for default (1.0)")
    print("="*60)
    
    while True:
        scale_input = input("Map scale (m/pixel): ").strip()
        if scale_input == "":
            return 1.0
        try:
            scale = float(scale_input)
            if scale > 0:
                return scale
            else:
                print("ERROR: Scale must be positive. Try again.")
        except ValueError:
            print("ERROR: Invalid input. Enter a number.")

if __name__ == "__main__":
    print("=== GEOLOGICAL MAP LEGEND ===")
    print("1. Select a TIFF map with a legend")
    print("2. Click on each legend color block")
    print("3. Type the corresponding rock name")
    print("4. Write STOP when done\n")
    
    path = select_file_window()
    
    if not path:
        print("No file selected. Exiting.")
        sys.exit(0)
    
    print(f"\nLoading map: {path}")
    print("Click on the legend colors one by one...\n")
    
    app = MapReader(path)
    plt.show()
    
    #after legend training completes, show validation table
    print("Starting legend validation")
    
    val_table = ValidationTable(app.custom_legend)
    
    print("Legend validation complete.Processing map...")
    
    #NEW RIVER ANALYSIS STEP (ADDED HERE)
    print("\n" + "~"*60)
    print("Starting river analysis")
    
    river_analyzer = RiverAnalyzer(app.image, app.custom_legend)
    river_analyzer.detect_river()
    adjacent_rocks = river_analyzer.find_adjacent_rocks()
    river_analyzer.report_results()
    
    print("Processing complete. Final legend at new window:")
    for color, rock in app.custom_legend.items():
        print(f"  {color} → {rock}")
    print("="*60)
    
    # = to fix it ===>
    print("Enter map scale (meters per pixel)")
    print("Example: 1 pixel = 10 meters → enter 10.0")
    print("Press Enter for default (1.0)")
    scale = get_map_scale()
    
    print("Starting Rock Distance Analysis (with scale: {} m/pixel)".format(scale))
    
    #RockDistanceTable instance using river_mask from RiverAnalyzer - still to fix it
    rock_distance_table = RockDistanceTable(
        app.image, 
        river_analyzer.river_mask, 
        app.custom_legend,
        scale_m_per_pixel=scale
    )
    rock_distance_table.print_table()
