import numpy as np
import pandas as pd
import os
from math import sqrt

GRID_ROWS = 20
GRID_COLS = 20
#test
OUTPUT_CSV = "rock_element_percentages_no_shapely.csv"
KEY_ELEMENTS = ["Si", "Al", "Fe", "Mg", "Ca"]

#test rocks
ROCK_LEGEND = {
    0: "NoData",
    1: "Granite",
    2: "Basalt",
    3: "Limestone"
}

#test rock composition
MOCK_COMPOSITION = {
    "Granite": {"Si": 30.0, "Al": 8.5, "Fe": 3.2, "Mg": 0.8, "Ca": 1.2},
    "Basalt":  {"Si": 21.0, "Al": 8.0, "Fe": 10.5, "Mg": 7.1, "Ca": 8.2},
    "Limestone":{"Si": 0.5, "Al": 0.1, "Fe": 0.2, "Mg": 0.3, "Ca": 55.0}
}
def create_mock_geology_grid(rows, cols):
    grid = np.zeros((rows, cols), dtype=int)
    #granite
    grid[5:12, 2:10] = 1
    #basalt
    grid[8:16, 9:17] = 2
    #limestone
    grid[2:9, 0:4] = 3
    return grid

#list of rivers
def create_mock_rivers():
    river1 = [(i, int(0.3*i + 2)) for i in range(0, 20)]   #list composition col,rows
    river2 = [(int(0.5*i + 3), int(18 - 0.4*i)) for i in range(0, 16)]  # other path
    return [river1, river2]

def make_catchment_mask(rows, cols, outlet_cell, radius_cells):
    mask = np.zeros((rows, cols), dtype=bool)
    orow, ocol = outlet_cell
    for r in range(rows):
        for c in range(cols):
            #Euclidean distance? in libraries DEM model of elevation
            d = sqrt((r - orow)**2 + (c - ocol)**2)
            if d <= radius_cells:
                mask[r, c] = True
    return mask

#output rock name-> number of cells 
def summarize_rocks_in_catchment(geology_grid, catchment_mask, rock_legend):
    masked = np.where(catchment_mask, geology_grid, 0)  #0 no data
    unique, counts = np.unique(masked, return_counts=True)
    summary = {}
    for code, cnt in zip(unique, counts):
        if code == 0:
            continue
        name = rock_legend.get(code, f"rock_{code}")
        summary[name] = cnt
    return summary

#FIX intersection in area not rivre
def find_river_rock_intersections(rivers, geology_grid, catchment_mask, rock_legend):
    intersected_rocks = set()
    for river in rivers:
        for (r, c) in river:
            if 0 <= r < geology_grid.shape[0] and 0 <= c < geology_grid.shape[1]:
                if not catchment_mask[r, c]:
                    continue  #ignore outside catchment
                code = int(geology_grid[r, c])
                if code == 0:
                    continue
                name = rock_legend.get(code, f"rock_{code}")
                intersected_rocks.add(name)
    return intersected_rocks

#key_elements -> % or nan - no found
def lookup_composition(rock_name, key_elements):
    rec = MOCK_COMPOSITION.get(rock_name)
    if rec is None:
        return {el: float("nan") for el in key_elements}
    return {el: rec.get(el, float("nan")) for el in key_elements}

#final table
def build_and_export_table(rock_counts, intersected_rocks, key_elements, output_csv):
    rows = []
    total_cells = sum(rock_counts.values()) if rock_counts else 0

    #data rows
    for rock, cnt in rock_counts.items():
        area_pct = (cnt / total_cells * 100) if total_cells > 0 else 0.0
        comp = lookup_composition(rock, key_elements)
        row = {
            "rock": rock,
            "area_cells": cnt,
            "area_pct": round(area_pct, 2),
            "river_intersected": (rock in intersected_rocks)
        }
        for el in key_elements:
            row[f"{el}_pct"] = comp.get(el)
        rows.append(row)

    #cr df
    header_labels = ["rock", "area_cells", "area_pct", "river_intersected"] + \
                    [f"{el}_pct" for el in key_elements]
    df = pd.DataFrame(rows, columns=header_labels)

    #legend
    description_row = ["rock", "area_cells", "area_pct", "river_intersected"] + \
                      ["key_element_pct"] * len(key_elements)
    df_description = pd.DataFrame([description_row], columns=header_labels)

    #data save?
    final_df = pd.concat([df_description, df], ignore_index=True)
    #final_df.to_csv(output_csv, index=False)

    return final_df

def main():
    geology = create_mock_geology_grid(GRID_ROWS, GRID_COLS)
    rivers = create_mock_rivers()
    outlet = (10, 6)
    radius = 6

    catchment = make_catchment_mask(GRID_ROWS, GRID_COLS, outlet, radius)

    rock_counts = summarize_rocks_in_catchment(geology, catchment, ROCK_LEGEND)
    river_rocks = find_river_rock_intersections(rivers, geology, catchment, ROCK_LEGEND)

    final_df = build_and_export_table(rock_counts, river_rocks, KEY_ELEMENTS, OUTPUT_CSV)
    print(final_df)
    print("Exported CSV:", os.path.abspath(OUTPUT_CSV))
if __name__ == "__main__":
    main()


#1 location > many localisation and compare