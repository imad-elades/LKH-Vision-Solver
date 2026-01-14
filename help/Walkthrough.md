# 📖 LKH Vision Solver - User Guide

**Complete guide to master TSP optimization**

© 2026 iM@Des - All rights reserved

---

## 🎯 Objective

This guide walks you through using LKH Vision Solver to optimize your routes step by step.

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

---

## 🖥️ Step 2: Launch the Application

```bash
cd "LKH Vision Solver"
py -3 LKH_Vision_Solver.py
```

The interface opens with 4 main sections.

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

## ⚙️ Step 4: Configure Parameters

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
- **SCALE**: Always keep at 100

---

## ▶️ Step 5: Launch Optimization

1. Click **▶ LAUNCH OPTIMIZATION**
2. Observe progress:
   - Progress bar
   - Real-time LKH console
   - Estimated time remaining

> ⚠️ You can stop at any time with **■ Stop**

---

## 📊 Step 6: Use the Results

### Generated Files

| Location | Content |
|----------|---------|
| `LKH_data/result/*.tour` | Raw LKH solution |
| `Excel/results/*_result.xlsx` | Data + visiting order |
| `Map_view/*_map.html` | Interactive map |

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

### Map not displaying
- Verify `folium` is installed
- Manually open the HTML file in `Map_view/`

---

## 📞 Support

**Developer**: iM@Des  
**Version**: 1.0.0

© 2026 iM@Des - All rights reserved
