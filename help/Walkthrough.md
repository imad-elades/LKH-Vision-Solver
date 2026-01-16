# 📖 LKH Vision Solver - User Guide

**Complete guide to master TSP optimization**

© 2026 iM@Des - All rights reserved

---

## 🎯 Objective

This guide walks you through using LKH Vision Solver to optimize your routes step by step, covering all features including the new v1.1.0 additions.

---

## 📁 Step 1: Prepare Your Data

### Required Format

Your Excel or CSV file must contain at minimum:

| Column | Description | Example |
|--------|-------------|---------|
| ID | Unique identifier | 1, 2, 3... or "Paris", "Lyon"... |
| Latitude | Y coordinate (degrees) | 48.8566 |
| Longitude | X coordinate (degrees) | 2.3522 |

### Tips
- ✅ Use decimal degree coordinates (WGS84)
- ✅ Avoid duplicate coordinates
- ✅ Verify lat/lon are not swapped (lat ∈ [-90, 90])

### File Location
After import, your file is copied to: `Excel/Imported/`

---

## 🖥️ Step 2: Launch the Application

```bash
cd "LKH Vision Solver"
py -3 LKH_Vision_Solver.py
```

The interface opens with 4 main sections:
1. **Import Data** - File selection and column mapping
2. **LKH Parameters** - Configuration and presets
3. **Execution** - Progress and console
4. **Results** - Output files and actions

---

## 📂 Step 3: Import Data

1. Click **📂 Select Excel/CSV file**
2. The application automatically detects columns
3. Verify/correct detection if needed:
   - **ID Column**: Identifier for each point
   - **Latitude**: Column containing latitudes
   - **Longitude**: Column containing longitudes

> 💡 The file is automatically copied to `Excel/Imported/`

---

## 🧮 Step 4: Choose Conversion Mode (v1.1.0) 🆕

After importing data, you can choose how distances are calculated:

### Option A: Haversine Matrix (Recommended for GPS)

| Feature | Description |
|---------|-------------|
| **Method** | Pre-calculates all distances using Haversine formula |
| **Precision** | Maximum accuracy for GPS coordinates |
| **EDGE_WEIGHT_TYPE** | Automatically set to EXPLICIT |
| **Best for** | Real-world GPS coordinates (latitude/longitude) |

### Option B: LKH Coordinates

| Feature | Description |
|---------|-------------|
| **Method** | Passes raw coordinates to LKH |
| **Distance Calculation** | LKH computes based on EDGE_WEIGHT_TYPE |
| **Flexibility** | Choose from GEOM, EUC_2D, GEO, etc. |
| **Best for** | Planar coordinates or custom distance types |

> 💡 **Recommendation**: Use **Haversine Matrix** for GPS coordinates (latitude/longitude in decimal degrees).

---

## ⚙️ Step 5: Configure Parameters

### Option A: Use a Preset

| Preset | Time | Quality | Usage |
|--------|------|---------|-------|
| 🚀 Fast | ~10s | Good | Testing, exploration |
| ⚖️ Balanced | ~1min | Very good | Daily use |
| 💎 Quality | ~5min | Excellent | Final solution |

### Option B: Custom Configuration

Hover over parameters with your mouse to see explanations.

**Main Parameters:**
- **RUNS**: More = better quality (recommended: 5-10)
- **MAX_TRIALS**: Trials per run (1000 standard)
- **MOVE_TYPE**: Lin-Kernighan moves (5 = best)
- **SCALE**: Always keep at 100

### Option C: Advanced Parameters (v1.1.0) 🆕

Click **"▶ Advanced parameters..."** to expand the advanced section:

| Parameter | Description | When to Change |
|-----------|-------------|----------------|
| **EDGE_WEIGHT_TYPE** | Distance calculation type | Only in Coordinates mode |
| **CANDIDATE_SET_TYPE** | Candidate construction | POPMUSIC for >10000 points |
| **MAX_CANDIDATES** | Max candidates per node | Increase for better quality |
| **INITIAL_TOUR_ALGORITHM** | Starting tour method | Usually leave default |
| **KICKS** | Number of perturbations | Increase for more exploration |
| **SEED** | Random seed | Change for different solutions |
| **TIME_LIMIT** | Max time in seconds | Set to limit long runs |

> 💡 Leave fields empty to use LKH defaults. You can type custom values directly.

---

## ▶️ Step 6: Launch Optimization

1. Click **▶ LAUNCH OPTIMIZATION**
2. Observe progress:
   - Progress bar
   - Real-time LKH console
   - Estimated time remaining

> ⚠️ You can stop at any time with **■ Stop**

---

## 📊 Step 7: Understand the Results

### Generated Files

| Location | File Type | Content |
|----------|-----------|---------|
| `LKH_data/Data/` | `.tsp` | TSP problem definition |
| `LKH_data/config/` | `.par` | LKH parameter file |
| `LKH_data/result/` | `.tour` | Raw LKH solution |
| `Excel/results/` | `*_result.xlsx` | Data + visiting order |
| `Map_view/` | `*_map.html` | Interactive map |

### File Flow Diagram

```
📥 Excel/CSV Input
       ↓
  [Conversion]
       ↓
📄 .tsp file (LKH_data/Data/)
       +
📄 .par file (LKH_data/config/)
       ↓
   [LKH.exe]
       ↓
📄 .tour file (LKH_data/result/)
       ↓
  [Processing]
       ↓
📊 Excel result    +    🗺️ HTML Map
(Excel/results/)       (Map_view/)
```

### Available Actions

- **📄 Inspect .tour**: Opens raw solution file
- **📊 Inspect Excel**: Opens result with visiting order
- **🗺️ Inspect Map**: Visualizes tour in browser
- **📁 Open folder**: Access results folder

---

## 🗺️ Reading the Map

The interactive map displays:

- 🟢 **Green marker**: Starting point
- 🔵 **Blue line**: Optimal tour path
- 📍 **Clusters**: Grouped points (click to expand)
- 📊 **Legend**: Total distance displayed

### Navigation
- Zoom: Mouse wheel
- Pan: Click + drag
- Fullscreen: Button in top right

---

## 📄 Understanding LKH Files

### .tsp File (Problem Definition)

Located in `LKH_data/Data/`, contains:
- Problem name and type
- Dimension (number of points)
- Edge weight type (EXPLICIT or coordinate-based)
- Distance matrix or node coordinates

### .par File (Parameters)

Located in `LKH_data/config/`, contains:
- Path to problem file
- Path to output file
- All LKH parameters (RUNS, MOVE_TYPE, etc.)

### .tour File (Solution)

Located in `LKH_data/result/`, contains:
- Tour length (total distance)
- Ordered list of node indices
- Can be opened in any text editor

---

## ❓ Troubleshooting

### Application won't start
```bash
pip install -r requirements.txt
```

### "Scale too large" error
- Use `SCALE = 100` (default)

### Optimization too slow
- Use the **🚀 Fast** preset
- Reduce RUNS to 1-3
- Set TIME_LIMIT in advanced parameters

### Map not displaying
- Verify `folium` is installed
- Manually open the HTML file in `Map_view/`

### Different results each time
- Set a fixed SEED in advanced parameters for reproducible results

---

## 📞 Support

**Developer**: iM@Des  
**Version**: 1.1.0

© 2026 iM@Des - All rights reserved
