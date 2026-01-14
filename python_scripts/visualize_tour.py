# -*- coding: utf-8 -*-
"""
TSP Tour Visualization Script
==============================
Displays the TSP tour on an interactive map with total distance calculation.

Usage:
    py -3 visualize_tour.py <tour_file> <data_file> [--output map.html]
"""

import pandas as pd
import folium
from folium import plugins
import argparse
import os
import sys
from math import radians, sin, cos, sqrt, atan2

# Earth's mean radius in kilometers
EARTH_RADIUS_KM = 6371.0


def haversine_distance(lat1, lon1, lat2, lon2):
    """Calculate great-circle distance between two points (in km)."""
    lat1_rad = radians(lat1)
    lat2_rad = radians(lat2)
    delta_lat = radians(lat2 - lat1)
    delta_lon = radians(lon2 - lon1)
    
    a = sin(delta_lat / 2) ** 2 + cos(lat1_rad) * cos(lat2_rad) * sin(delta_lon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    
    return EARTH_RADIUS_KM * c


def parse_tour_file(tour_path):
    """Parse LKH tour file to get visiting order."""
    tour_order = []
    in_tour_section = False
    tour_length = None
    
    with open(tour_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            
            # Extract tour length from comment
            if line.startswith('COMMENT : Length ='):
                try:
                    tour_length = int(line.split('=')[1].strip())
                except:
                    pass
            
            if line == 'TOUR_SECTION':
                in_tour_section = True
                continue
            
            if line in ['-1', 'EOF', '']:
                if in_tour_section and tour_order:
                    break
                continue
            
            if in_tour_section:
                try:
                    node_id = int(line)
                    tour_order.append(node_id)
                except ValueError:
                    continue
    
    return tour_order, tour_length


def load_data(data_path, id_col='commune', lat_col='Y-coordinate', lon_col='X-coordinate'):
    """Load data from Excel or CSV file."""
    ext = os.path.splitext(data_path)[1].lower()
    
    if ext in ['.xlsx', '.xls']:
        df = pd.read_excel(data_path)
    elif ext == '.csv':
        df = pd.read_csv(data_path)
    else:
        raise ValueError(f"Unsupported file format: {ext}")
    
    # Auto-detect columns if not found
    if lat_col not in df.columns:
        for col in df.columns:
            if 'lat' in col.lower() or col.lower() == 'y' or 'y-coord' in col.lower():
                lat_col = col
                break
    
    if lon_col not in df.columns:
        for col in df.columns:
            if 'lon' in col.lower() or col.lower() == 'x' or 'x-coord' in col.lower():
                lon_col = col
                break
    
    return df, id_col, lat_col, lon_col


def create_tour_map(df, tour_order, id_col, lat_col, lon_col, output_path, scale=100):
    """Create an interactive map with the tour path."""
    
    # Get coordinates in tour order
    tour_coords = []
    tour_ids = []
    
    for node_id in tour_order:
        idx = node_id - 1  # LKH uses 1-indexed
        if 0 <= idx < len(df):
            lat = df.iloc[idx][lat_col]
            lon = df.iloc[idx][lon_col]
            commune_id = df.iloc[idx][id_col]
            tour_coords.append((lat, lon))
            tour_ids.append(commune_id)
    
    # Close the loop
    if tour_coords:
        tour_coords.append(tour_coords[0])
        tour_ids.append(tour_ids[0])
    
    # Calculate total distance
    total_distance = 0.0
    for i in range(len(tour_coords) - 1):
        lat1, lon1 = tour_coords[i]
        lat2, lon2 = tour_coords[i + 1]
        total_distance += haversine_distance(lat1, lon1, lat2, lon2)
    
    print(f"\n{'='*60}")
    print(f"RÉSULTATS TSP - VISUALISATION CARTE")
    print(f"{'='*60}")
    print(f"\nNombre de communes: {len(tour_order)}")
    print(f"Distance totale: {total_distance:,.2f} km")
    print(f"Distance moyenne entre points: {total_distance / len(tour_order):,.2f} km")
    
    # Calculate map center
    center_lat = sum(c[0] for c in tour_coords[:-1]) / len(tour_coords[:-1])
    center_lon = sum(c[1] for c in tour_coords[:-1]) / len(tour_coords[:-1])
    
    # Create map
    m = folium.Map(
        location=[center_lat, center_lon],
        zoom_start=6,
        tiles='OpenStreetMap'
    )
    
    # Add title
    title_html = f'''
    <div style="position: fixed; 
                top: 10px; left: 50px; width: 400px; 
                background-color: white; 
                border: 2px solid #333;
                z-index: 9999; 
                padding: 10px;
                border-radius: 10px;
                box-shadow: 2px 2px 10px rgba(0,0,0,0.3);">
        <h3 style="margin: 0; color: #333;">🗺️ Tour TSP Optimisé</h3>
        <p style="margin: 5px 0; font-size: 14px;">
            <b>Communes:</b> {len(tour_order)}<br>
            <b>Distance totale:</b> {total_distance:,.2f} km
        </p>
    </div>
    '''
    m.get_root().html.add_child(folium.Element(title_html))
    
    # Add tour path as a polyline
    path_coords = [(lat, lon) for lat, lon in tour_coords]
    
    # Add the main tour line
    folium.PolyLine(
        path_coords,
        weight=2,
        color='#0066CC',
        opacity=0.8,
        tooltip=f"Distance totale: {total_distance:,.2f} km"
    ).add_to(m)
    
    # Add markers for key points (start, some intermediate, end)
    # Start point (green)
    folium.Marker(
        tour_coords[0],
        popup=f"<b>DÉPART</b><br>Commune: {tour_ids[0]}<br>Position: 1",
        icon=folium.Icon(color='green', icon='play')
    ).add_to(m)
    
    # Add intermediate markers (every N points for visibility)
    n_markers = min(50, len(tour_order))  # Limit markers for performance
    step = max(1, len(tour_order) // n_markers)
    
    # Create a marker cluster for all points
    marker_cluster = plugins.MarkerCluster(name='Communes').add_to(m)
    
    for i, (coord, commune_id) in enumerate(zip(tour_coords[:-1], tour_ids[:-1])):
        # Add to cluster
        folium.CircleMarker(
            location=coord,
            radius=4,
            color='#0066CC',
            fill=True,
            fill_color='#3388ff',
            fill_opacity=0.7,
            popup=f"Commune: {commune_id}<br>Position: {i+1}"
        ).add_to(marker_cluster)
    
    # Add layer control
    folium.LayerControl().add_to(m)
    
    # Add fullscreen button
    plugins.Fullscreen().add_to(m)
    
    # Save map
    m.save(output_path)
    print(f"\nCarte générée: {os.path.abspath(output_path)}")
    print(f"\nOuvrez le fichier HTML dans votre navigateur pour voir la carte interactive!")
    
    return total_distance


def main():
    parser = argparse.ArgumentParser(
        description='Visualize TSP tour on an interactive map',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  py -3 visualize_tour.py solution.tour data.xlsx
  py -3 visualize_tour.py solution.tour data.xlsx --output my_map.html
        """
    )
    
    parser.add_argument('tour_file', help='LKH tour file (.tour)')
    parser.add_argument('data_file', help='Original data file (Excel/CSV)')
    parser.add_argument('--output', '-o', default='tour_map.html', help='Output HTML file')
    parser.add_argument('--id-col', default='commune', help='ID column name')
    parser.add_argument('--lat-col', default='Y-coordinate', help='Latitude column name')
    parser.add_argument('--lon-col', default='X-coordinate', help='Longitude column name')
    parser.add_argument('--scale', type=int, default=100, help='Distance scale factor used')
    
    args = parser.parse_args()
    
    # Parse tour file
    print(f"Lecture du fichier tour: {args.tour_file}")
    tour_order, lkh_length = parse_tour_file(args.tour_file)
    print(f"  → {len(tour_order)} nœuds trouvés")
    
    if lkh_length:
        print(f"  → Distance LKH: {lkh_length} (= {lkh_length / args.scale:,.2f} km avec scale={args.scale})")
    
    # Load data
    print(f"\nChargement des données: {args.data_file}")
    df, id_col, lat_col, lon_col = load_data(
        args.data_file, 
        args.id_col, 
        args.lat_col, 
        args.lon_col
    )
    print(f"  → {len(df)} lignes chargées")
    print(f"  → Colonnes: ID={id_col}, Lat={lat_col}, Lon={lon_col}")
    
    # Create map
    print(f"\nGénération de la carte...")
    total_distance = create_tour_map(
        df, tour_order, 
        id_col, lat_col, lon_col,
        args.output, 
        args.scale
    )


if __name__ == '__main__':
    main()
