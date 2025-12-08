# ETH
Map minerals occurrences from OpenMindat using Python and packets and geologicalmaps of rivers. Let's find key elements of rivers!

This project demonstrates how many key elements from rocks you can find in river by:
1. Code using Python
1. Fetching key elements on OpenMindat API (https://quexiang.github.io/OpenMindat/)
3. Add any data - raster maps

   PseudoCOde created at 6.11.2025 added 25.11
   

## How to run
Select File: It opens a pop-up window so that you can choose your map image (.jpg or .png) from your computer.

Phase 1: Training (Teaching)
The map opens.
You click on a color in the map's legend.
You put the name of that rock in the console, for instance, "Granite", and then press Enter.

The program "learns" that color = that rock

Click once more to finish, and type "EXIT".

Refresh: This option removes the blue "X" marks from the screen in preparation for an analysis.
Phase 2: Analysis:

You click anywhere on the main map.
The program looks at the color you clicked.

In progress It mathematically - using Euclidean distance - compares it with colors taught in Phase 1. It will print in the console the name of the nearest matching rock.
```bash
