# 🗺️ LKH Vision Solver

[![Python 3.8+](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/License-Proprietary-red.svg)](#license)
[![Version](https://img.shields.io/badge/Version-1.0.0-green.svg)](#)

**Complete graphical solution for Traveling Salesman Problem (TSP) optimization**

© 2026 iM@Des - All rights reserved

---

## ✨ Features

- 📁 **Import** Excel/CSV files with geographic coordinates
- ⚙️ **Configure** LKH parameters with interactive tooltips
- 🚀 **Presets**: Fast (~10s), Balanced (~1min), Quality (~5min)
- 📊 **Real-time tracking** of optimization progress
- 📈 **Export** results to Excel with visiting order
- 🗺️ **Interactive map** visualization using Folium

---

## 📸 Screenshots

*Coming soon*

---

## 🚀 Quick Start

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Run the application

```bash
py -3 LKH_Vision_Solver.py
```

---

## 📋 Requirements

- Python 3.8 or higher
- Windows OS (LKH.exe included)
- Dependencies: `pandas`, `openpyxl`, `numpy`, `Pillow`, `folium`

---

## 📁 Project Structure

```
LKH-Vision-Solver/
├── LKH_Vision_Solver.py    # Main application (entry point)
├── requirements.txt        # Python dependencies
├── LKH_exe/               # LKH solver executable
├── python_scripts/        # Core modules
├── LKH_data/              # TSP/PAR/TOUR files
├── Excel/                 # Input/Output Excel files
├── icon/                  # Application icon
├── Map_view/              # Generated HTML maps
└── help/                  # Documentation
```

---

## 📊 Input Data Format

Your Excel/CSV file should contain:

| ID | Latitude | Longitude |
|----|----------|-----------|
| 1 | 33.5731 | -7.5898 |
| 2 | 34.0209 | -6.8416 |
| ... | ... | ... |

---

## ⚙️ LKH Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| RUNS | 10 | Number of optimization runs |
| MOVE_TYPE | 5 | Lin-Kernighan move type (2-5) |
| MAX_TRIALS | 1000 | Maximum trials per run |
| POPULATION_SIZE | 3 | Genetic algorithm population |
| RECOMBINATION | CLARIST | Recombination method |

---

## 📖 Documentation

- [README](help/README.md) - Full documentation
- [Walkthrough](help/Walkthrough.md) - Step-by-step user guide

---

## 📄 License

© 2026 iM@Des - All rights reserved

This software is proprietary. Unauthorized reproduction, distribution, or modification is strictly prohibited.

---

## 👤 Author

**iM@Des**

---

*Built with ❤️ for TSP optimization*
