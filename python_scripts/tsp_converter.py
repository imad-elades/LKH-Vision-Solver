# -*- coding: utf-8 -*-
"""
TSP Converter Tool - Conversion Excel/CSV ↔ LKH TSP Format
============================================================
Uses EXPLICIT distance matrix with Haversine formula for maximum precision.
Scaling factor of 10,000 to preserve 4 decimal places in distances.

Author: TSP Converter Tool
Version: 1.0.0
"""

import pandas as pd
import numpy as np
from math import radians, sin, cos, sqrt, atan2
from typing import Optional, List, Tuple
import os


# =============================================================================
# CONSTANTS
# =============================================================================
EARTH_RADIUS_KM = 6371.008  # Earth's mean radius in kilometers
DEFAULT_SCALE = 1000000     # Scale factor for distance (preserves 4 decimals)


# =============================================================================
# HAVERSINE DISTANCE CALCULATION
# =============================================================================
def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate the great-circle distance between two points on Earth.
    Uses Haversine formula with float64 precision.
    
    Args:
        lat1, lon1: Latitude and longitude of point 1 (in decimal degrees)
        lat2, lon2: Latitude and longitude of point 2 (in decimal degrees)
    
    Returns:
        Distance in kilometers (float64)
    """
    # Convert to radians
    lat1_rad = radians(lat1)
    lat2_rad = radians(lat2)
    delta_lat = radians(lat2 - lat1)
    delta_lon = radians(lon2 - lon1)
    
    # Haversine formula
    a = sin(delta_lat / 2) ** 2 + cos(lat1_rad) * cos(lat2_rad) * sin(delta_lon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    
    return EARTH_RADIUS_KM * c


# =============================================================================
# EXCEL TO TSP CONVERTER
# =============================================================================
class ExcelToTSPConverter:
    """
    Convert Excel/CSV files with geographic coordinates to LKH TSP format.
    Uses EXPLICIT distance matrix for maximum precision.
    """
    
    def __init__(self, 
                 input_path: str,
                 id_col: str = 'commune',
                 lat_col: str = 'latitude', 
                 lon_col: str = 'longitude',
                 scale: int = DEFAULT_SCALE):
        """
        Initialize converter with input file.
        
        Args:
            input_path: Path to Excel (.xlsx) or CSV file
            id_col: Name of the ID/name column
            lat_col: Name of the latitude column
            lon_col: Name of the longitude column
            scale: Scaling factor for distances (default: 10000)
        """
        self.input_path = input_path
        self.id_col = id_col
        self.lat_col = lat_col
        self.lon_col = lon_col
        self.scale = scale
        self.df = None
        self.distance_matrix = None
        self._load_data()
    
    def _load_data(self):
        """Load data from Excel or CSV file."""
        ext = os.path.splitext(self.input_path)[1].lower()
        
        if ext == '.xlsx' or ext == '.xls':
            self.df = pd.read_excel(self.input_path)
        elif ext == '.csv':
            self.df = pd.read_csv(self.input_path)
        else:
            raise ValueError(f"Unsupported file format: {ext}. Use .xlsx, .xls, or .csv")
        
        # Validate required columns
        missing_cols = []
        for col_name, col_label in [(self.id_col, 'ID'), 
                                     (self.lat_col, 'Latitude'), 
                                     (self.lon_col, 'Longitude')]:
            if col_name not in self.df.columns:
                missing_cols.append(f"{col_label} ('{col_name}')")
        
        if missing_cols:
            available = self.df.columns.tolist()
            raise ValueError(
                f"Missing columns: {', '.join(missing_cols)}\n"
                f"Available columns: {available}"
            )
        
        print(f"[INFO] Loaded {len(self.df)} points from '{self.input_path}'")
        print(f"[INFO] Columns: {self.df.columns.tolist()}")
    
    def compute_distance_matrix(self) -> np.ndarray:
        """
        Compute full distance matrix using Haversine formula.
        Distances are scaled by self.scale factor.
        
        Returns:
            Distance matrix as numpy array (int64 after scaling)
        """
        n = len(self.df)
        print(f"[INFO] Computing {n}x{n} distance matrix...")
        
        lats = self.df[self.lat_col].values.astype(np.float64)
        lons = self.df[self.lon_col].values.astype(np.float64)
        
        # Initialize matrix
        self.distance_matrix = np.zeros((n, n), dtype=np.int64)
        
        # Compute upper triangle and mirror
        total = n * (n - 1) // 2
        count = 0
        last_percent = 0
        
        for i in range(n):
            for j in range(i + 1, n):
                dist = haversine_distance(lats[i], lons[i], lats[j], lons[j])
                scaled_dist = int(round(dist * self.scale))
                self.distance_matrix[i, j] = scaled_dist
                self.distance_matrix[j, i] = scaled_dist
                
                count += 1
                percent = int(count * 100 / total)
                if percent >= last_percent + 10:
                    print(f"[INFO] Progress: {percent}%")
                    last_percent = percent
        
        print(f"[INFO] Distance matrix computed. Scale factor: {self.scale}")
        return self.distance_matrix
    
    def generate_tsp_file(self, output_path: str, problem_name: Optional[str] = None):
        """
        Generate TSP file in TSPLIB format with EXPLICIT distance matrix.
        
        Args:
            output_path: Path for output .tsp file
            problem_name: Name for the problem (default: derived from filename)
        """
        if self.distance_matrix is None:
            self.compute_distance_matrix()
        
        n = len(self.df)
        if problem_name is None:
            problem_name = os.path.splitext(os.path.basename(output_path))[0]
        
        print(f"[INFO] Generating TSP file: {output_path}")
        
        with open(output_path, 'w', encoding='utf-8') as f:
            # Header section
            f.write(f"NAME : {problem_name}\n")
            f.write(f"COMMENT : Generated by TSP Converter (scale={self.scale})\n")
            f.write(f"TYPE : TSP\n")
            f.write(f"DIMENSION : {n}\n")
            f.write(f"EDGE_WEIGHT_TYPE : EXPLICIT\n")
            f.write(f"EDGE_WEIGHT_FORMAT : FULL_MATRIX\n")
            f.write(f"EDGE_WEIGHT_SECTION\n")
            
            # Write full distance matrix
            for i in range(n):
                row = ' '.join(str(self.distance_matrix[i, j]) for j in range(n))
                f.write(row + '\n')
            
            f.write("EOF\n")
        
        print(f"[INFO] TSP file generated: {output_path}")
        return output_path
    
    def generate_tsp_file_coords(self, output_path: str, edge_weight_type: str = 'GEOM',
                                  problem_name: Optional[str] = None):
        """
        Generate TSP file with coordinates (no distance matrix).
        LKH will calculate distances internally based on EDGE_WEIGHT_TYPE.
        
        Supported EDGE_WEIGHT_TYPES:
            - GEOM: Geographic coordinates (lat, lon in decimal degrees)
            - GEO: Geographic coordinates (DDD.MM format)
            - EUC_2D: Euclidean 2D coordinates
            - EUC_3D: Euclidean 3D coordinates
            - ATT: Pseudo-Euclidean (ATT distance)
            - CEIL_2D: Euclidean 2D with ceiling
        
        Args:
            output_path: Path for output .tsp file
            edge_weight_type: Type of edge weight calculation (default: GEOM)
            problem_name: Name for the problem (default: derived from filename)
        """
        n = len(self.df)
        if problem_name is None:
            problem_name = os.path.splitext(os.path.basename(output_path))[0]
        
        print(f"[INFO] Generating TSP file with coordinates: {output_path}")
        print(f"[INFO] Edge weight type: {edge_weight_type}")
        
        with open(output_path, 'w', encoding='utf-8') as f:
            # Header section
            f.write(f"NAME : {problem_name}\n")
            f.write(f"COMMENT : Generated by TSP Converter (coords mode)\n")
            f.write(f"TYPE : TSP\n")
            f.write(f"DIMENSION : {n}\n")
            f.write(f"EDGE_WEIGHT_TYPE : {edge_weight_type}\n")
            f.write(f"NODE_COORD_SECTION\n")
            
            # Write node coordinates
            # Format: node_id x_coord y_coord
            # For GEOM/GEO: x = latitude, y = longitude
            for idx, row in self.df.iterrows():
                node_id = idx + 1  # 1-indexed
                lat = row[self.lat_col]
                lon = row[self.lon_col]
                f.write(f"{node_id} {lat} {lon}\n")
            
            f.write("EOF\n")
        
        print(f"[INFO] TSP file generated (coords mode): {output_path}")
        return output_path
    
    def generate_par_file(self, output_path: str, tsp_path: str, 
                          runs: int = 10, 
                          move_type: int = 5,
                          population_size: int = 3,
                          max_trials: int = 1000,
                          tour_file: Optional[str] = None):
        """
        Generate parameter file for LKH.
        
        Args:
            output_path: Path for output .par file
            tsp_path: Path to the .tsp problem file
            runs: Number of runs
            move_type: LKH move type (2-5)
            population_size: Population size for genetic algorithm
            max_trials: Maximum trials per run
            tour_file: Path for output tour file
        """
        if tour_file is None:
            tour_file = os.path.splitext(output_path)[0] + '.tour'
        
        print(f"[INFO] Generating PAR file: {output_path}")
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(f"PROBLEM_FILE = {tsp_path}\n")
            f.write(f"MOVE_TYPE = {move_type}\n")
            f.write(f"PATCHING_C = 3\n")
            f.write(f"PATCHING_A = 2\n")
            f.write(f"RUNS = {runs}\n")
            f.write(f"MAX_TRIALS = {max_trials}\n")
            if population_size > 1:
                f.write(f"POPULATION_SIZE = {population_size}\n")
                f.write(f"RECOMBINATION = CLARIST\n")
            f.write(f"TOUR_FILE = {tour_file}\n")
        
        print(f"[INFO] PAR file generated: {output_path}")
        return output_path
    
    def convert(self, output_dir: str, problem_name: Optional[str] = None) -> Tuple[str, str]:
        """
        Perform full conversion: Excel → TSP + PAR.
        
        Args:
            output_dir: Directory for output files
            problem_name: Name for the problem files
        
        Returns:
            Tuple of (tsp_path, par_path)
        """
        if problem_name is None:
            problem_name = os.path.splitext(os.path.basename(self.input_path))[0]
            problem_name = problem_name.replace(' ', '_')
        
        os.makedirs(output_dir, exist_ok=True)
        
        tsp_path = os.path.join(output_dir, f"{problem_name}.tsp")
        par_path = os.path.join(output_dir, f"{problem_name}.par")
        
        self.compute_distance_matrix()
        self.generate_tsp_file(tsp_path, problem_name)
        self.generate_par_file(par_path, tsp_path)
        
        return tsp_path, par_path


# =============================================================================
# TOUR TO EXCEL CONVERTER
# =============================================================================
class TourToExcelConverter:
    """
    Convert LKH .tour output file to Excel/CSV format.
    Matches tour order with original data.
    """
    
    def __init__(self, tour_path: str, original_data_path: str,
                 id_col: str = 'commune',
                 lat_col: str = 'latitude',
                 lon_col: str = 'longitude'):
        """
        Initialize converter with tour and original data files.
        
        Args:
            tour_path: Path to LKH output .tour file
            original_data_path: Path to original Excel/CSV data
            id_col: Name of the ID column
            lat_col: Name of the latitude column
            lon_col: Name of the longitude column
        """
        self.tour_path = tour_path
        self.original_data_path = original_data_path
        self.id_col = id_col
        self.lat_col = lat_col
        self.lon_col = lon_col
        self.tour_order = None
        self.original_df = None
        self._load_data()
    
    def _load_data(self):
        """Load original data and parse tour file."""
        # Load original data
        ext = os.path.splitext(self.original_data_path)[1].lower()
        if ext == '.xlsx' or ext == '.xls':
            self.original_df = pd.read_excel(self.original_data_path)
        elif ext == '.csv':
            self.original_df = pd.read_csv(self.original_data_path)
        else:
            raise ValueError(f"Unsupported format: {ext}")
        
        # Parse tour file
        self._parse_tour()
    
    def _parse_tour(self):
        """Parse LKH tour file to extract visiting order."""
        self.tour_order = []
        in_tour_section = False
        
        with open(self.tour_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                
                if line == 'TOUR_SECTION':
                    in_tour_section = True
                    continue
                
                if line in ['-1', 'EOF', '']:
                    if in_tour_section and self.tour_order:
                        break
                    continue
                
                if in_tour_section:
                    try:
                        node_id = int(line)
                        self.tour_order.append(node_id)
                    except ValueError:
                        continue
        
        print(f"[INFO] Parsed tour with {len(self.tour_order)} nodes")
    
    def generate_output(self, output_path: str, output_format: str = 'xlsx'):
        """
        Generate output Excel/CSV file with visiting order.
        
        Args:
            output_path: Path for output file
            output_format: 'xlsx' or 'csv'
        """
        # Create output dataframe
        n = len(self.original_df)
        result_df = self.original_df.copy()
        
        # Add visiting order column
        order_col = 'visiting_order'
        result_df[order_col] = 0
        
        # Map tour order to original data
        for visit_position, node_id in enumerate(self.tour_order, start=1):
            # node_id is 1-indexed in LKH
            idx = node_id - 1
            if 0 <= idx < n:
                result_df.loc[idx, order_col] = visit_position
        
        # Sort by visiting order for export
        result_sorted = result_df.sort_values(by=order_col)
        
        print(f"[INFO] Generating output: {output_path}")
        
        if output_format.lower() == 'csv':
            result_sorted.to_csv(output_path, index=False)
        else:
            result_sorted.to_excel(output_path, index=False)
        
        print(f"[INFO] Output generated: {output_path}")
        
        # Also generate a response-style file (just ID and order)
        response_path = output_path.replace('.xlsx', '_response.xlsx').replace('.csv', '_response.csv')
        response_df = result_df[[self.id_col, order_col]].copy()
        
        if output_format.lower() == 'csv':
            response_df.to_csv(response_path, index=False)
        else:
            response_df.to_excel(response_path, index=False)
        
        print(f"[INFO] Response file generated: {response_path}")
        
        return output_path, response_path


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================
def detect_columns(df: pd.DataFrame) -> Tuple[str, str, str]:
    """
    Auto-detect ID, latitude, and longitude columns from DataFrame.
    
    Returns:
        Tuple of (id_col, lat_col, lon_col)
    """
    columns_lower = {col.lower(): col for col in df.columns}
    
    # Common patterns for latitude
    lat_patterns = ['latitude', 'lat', 'y', 'coord_y', 'lat_deg']
    lon_patterns = ['longitude', 'lon', 'long', 'x', 'coord_x', 'lon_deg', 'lng']
    id_patterns = ['id', 'commune', 'name', 'city', 'node', 'point', 'index']
    
    lat_col = None
    lon_col = None
    id_col = None
    
    for pattern in lat_patterns:
        if pattern in columns_lower:
            lat_col = columns_lower[pattern]
            break
    
    for pattern in lon_patterns:
        if pattern in columns_lower:
            lon_col = columns_lower[pattern]
            break
    
    for pattern in id_patterns:
        if pattern in columns_lower:
            id_col = columns_lower[pattern]
            break
    
    # If no ID column found, use first column
    if id_col is None and len(df.columns) > 0:
        id_col = df.columns[0]
    
    return id_col, lat_col, lon_col


if __name__ == '__main__':
    print("TSP Converter Module")
    print("Use run_converter.py for command-line interface")
