# 🗺️ LKH Vision Solver

**Complete solution for Traveling Salesman Problem (TSP) optimization**

© 2026 iM@Des - All rights reserved

---

## 📋 Description

LKH Vision Solver is an intuitive graphical interface for the LKH solver (Lin-Kernighan Heuristic), one of the most powerful algorithms for solving the Traveling Salesman Problem.

### Features

- ✅ Import Excel/CSV files with geographic coordinates
- ✅ Complete LKH parameter configuration with explanations
- ✅ Presets: Fast, Balanced, Quality
- ✅ Real-time optimization tracking
- ✅ Export results to Excel
- ✅ Interactive map visualization of the tour

### New in v1.1.0 🆕

- ✅ **Conversion Mode Selector**: Haversine Matrix vs LKH Coordinates
- ✅ **Advanced LKH Parameters**: 9 new configurable parameters
- ✅ **Collapsible UI**: Advanced parameters in expandable section

---

## 🚀 Installation

### Prerequisites

- **Python 3.8+** 
- **Required Python libraries**:
  ```bash
  pip install -r requirements.txt
  ```

### Project Structure

```
LKH Vision Solver/
├── LKH_Vision_Solver.py    # Main application
├── requirements.txt
├── LKH_exe/
│   └── LKH.exe             # LKH solver
├── python_scripts/
│   ├── tsp_converter.py    # Conversion module
│   ├── visualize_tour.py   # Visualization module
│   └── run_converter.py    # CLI (optional)
├── LKH_data/
│   ├── Data/               # .tsp files
│   ├── config/             # .par files
│   └── result/             # .tour files
├── Excel/
│   ├── Imported/           # Imported Excel files
│   └── results/            # Excel results
├── icon/
│   └── icon.png            # Application icon
├── Map_view/               # HTML maps
└── help/
    ├── README.md           # This file
    └── Walkthrough.md      # User guide
```

---

## 💻 Usage

### Getting Started

```bash
cd "LKH Vision Solver"
py -3 LKH_Vision_Solver.py
```

### Steps

1. **Import**: Select your Excel/CSV file with coordinates
2. **Choose Mode**: Haversine Matrix or LKH Coordinates (v1.1.0)
3. **Configure**: Choose a preset or adjust parameters
4. **Optimize**: Launch optimization and track progress
5. **Results**: Inspect the tour, Excel file, or map

---

## 🧮 Conversion Modes (v1.1.0)

| Mode | Method | Best For |
|------|--------|----------|
| **Haversine Matrix** | Pre-calculated distances | GPS coordinates |
| **LKH Coordinates** | LKH computes distances | Planar/custom |

---

## ⚙️ LKH Parameters

### Standard Parameters

| Parameter | Description | Impact |
|-----------|-------------|--------|
| RUNS | Number of independent runs | ⬆️ Quality, ⬆️ Time |
| MOVE_TYPE | Move type (2-5) | 5 = best |
| MAX_TRIALS | Trials per run | ⬆️ Convergence |
| POPULATION_SIZE | Population size | ⬆️ Diversity |
| RECOMBINATION | Genetic method | CLARIST recommended |
| SCALE | Precision factor | 100 = standard |

### Advanced Parameters (v1.1.0) 🆕

| Parameter | Description |
|-----------|-------------|
| EDGE_WEIGHT_TYPE | Distance calculation type |
| CANDIDATE_SET_TYPE | Candidate construction method |
| MAX_CANDIDATES | Max candidates per node |
| INITIAL_TOUR_ALGORITHM | Initial tour algorithm |
| KICKS | Number of perturbations |
| KICK_TYPE | Type of kick |
| BACKTRACKING | Enable backtracking search |
| SEED | Random seed |
| TIME_LIMIT | Time limit (seconds) |

### Presets

- 🚀 **Fast**: ~10 sec - Quick tests
- ⚖️ **Balanced**: ~1 min - Ideal compromise
- 💎 **Quality**: ~5 min - Best solution

---

## 📊 Data Format

### Input File (Excel/CSV)

| ID | Latitude | Longitude |
|----|----------|-----------|
| 1 | 33.5731 | -7.5898 |
| 2 | 34.0209 | -6.8416 |
| ... | ... | ... |

### Output File (Excel)

| ID | Latitude | Longitude | visiting_order |
|----|----------|-----------|----------------|
| 1 | 33.5731 | -7.5898 | 1 |
| 2 | 34.0209 | -6.8416 | 45 |
| ... | ... | ... | ... |

---

## 📄 License

© 2026 iM@Des - All rights reserved

This software is the exclusive property of iM@Des. Any reproduction, distribution, or modification without written authorization is strictly prohibited.

---

## 📧 Contact

**Developer**: iM@Des  
**Version**: 1.1.0
