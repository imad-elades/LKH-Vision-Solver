# -*- coding: utf-8 -*-
"""
LKH Vision Solver - Interface Graphique TSP
=============================================
Solution complète pour l'optimisation du problème du voyageur de commerce.

© 2026 iM@Des - Tous droits réservés

Usage:
    py -3 LKH_Vision_Solver.py
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
import subprocess
import os
import sys
import time
import webbrowser
import shutil
from datetime import datetime
from PIL import Image, ImageTk

# ============================================================================
# PATHS CONFIGURATION
# ============================================================================
# Get the directory where this script is located
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Define all paths relative to BASE_DIR
PATHS = {
    'scripts': os.path.join(BASE_DIR, 'python_scripts'),
    'lkh_exe': os.path.join(BASE_DIR, 'LKH_exe', 'LKH.exe'),
    'data': os.path.join(BASE_DIR, 'LKH_data', 'Data'),
    'config': os.path.join(BASE_DIR, 'LKH_data', 'config'),
    'result': os.path.join(BASE_DIR, 'LKH_data', 'result'),
    'excel_imported': os.path.join(BASE_DIR, 'Excel', 'Imported'),
    'excel_results': os.path.join(BASE_DIR, 'Excel', 'results'),
    'icon': os.path.join(BASE_DIR, 'icon', 'icon.png'),
    'map_view': os.path.join(BASE_DIR, 'Map_view'),
    'help': os.path.join(BASE_DIR, 'help')
}

# Add python_scripts to path for imports
sys.path.insert(0, PATHS['scripts'])

# Import modules from python_scripts
try:
    from tsp_converter import ExcelToTSPConverter, TourToExcelConverter, haversine_distance
    import visualize_tour as viz
except ImportError as e:
    print(f"Erreur d'import: {e}")
    print(f"Vérifiez que les scripts sont dans: {PATHS['scripts']}")

# Import pandas
import pandas as pd


# =============================================================================
# CONSTANTS & STYLING
# =============================================================================
APP_TITLE = "🗺️ LKH Vision Solver"
APP_VERSION = "1.0.0"
COPYRIGHT = "© 2026 iM@Des - Tous droits réservés"
DEVELOPER = "iM@Des"

# Colors - Dark premium theme
COLORS = {
    'bg': '#1a1a2e',
    'bg_light': '#16213e',
    'accent': '#0f3460',
    'primary': '#e94560',
    'secondary': '#533483',
    'success': '#00d9a5',
    'warning': '#ffc107',
    'text': '#eaeaea',
    'text_muted': '#888888',
    'border': '#0f3460'
}

# LKH Parameters with descriptions
LKH_PARAMS = {
    'RUNS': {
        'default': 10,
        'min': 1,
        'max': 100,
        'description': "Nombre d'exécutions indépendantes",
        'impact': "⬆️ Plus = meilleure qualité mais plus lent",
        'example': "Pour 1000 points : 5-10 runs recommandés"
    },
    'MOVE_TYPE': {
        'default': 5,
        'options': [2, 3, 4, 5],
        'description': "Type de mouvement Lin-Kernighan (2-opt à 5-opt)",
        'impact': "5 = exploration maximale, 2 = rapide",
        'example': "5-opt détecte des améliorations que 2-opt rate"
    },
    'MAX_TRIALS': {
        'default': 1000,
        'min': 100,
        'max': 10000,
        'description': "Nombre maximum d'essais par run",
        'impact': "⬆️ Plus = meilleure convergence",
        'example': "1000 suffisant pour < 5000 points"
    },
    'POPULATION_SIZE': {
        'default': 3,
        'min': 1,
        'max': 50,
        'description': "Taille de la population (algorithme génétique)",
        'impact': "⬆️ Plus = plus de diversité génétique",
        'example': "3-5 est un bon compromis"
    },
    'RECOMBINATION': {
        'default': 'CLARIST',
        'options': ['IPT', 'GPX2', 'CLARIST'],
        'description': "Méthode de recombinaison génétique",
        'impact': "CLARIST = état de l'art, GPX2 = rapide",
        'example': "CLARIST recommandé pour qualité max"
    },
    'PATCHING_C': {
        'default': 3,
        'min': 1,
        'max': 5,
        'description': "Paramètre de correction de cycle",
        'impact': "Rarement modifié, 3 = standard",
        'example': "Laisser à 3 sauf expertise"
    },
    'PATCHING_A': {
        'default': 2,
        'min': 1,
        'max': 5,
        'description': "Paramètre d'amplification",
        'impact': "Rarement modifié, 2 = standard",
        'example': "Laisser à 2 sauf expertise"
    },
    'SCALE': {
        'default': 100,
        'min': 1,
        'max': 1000,
        'description': "Facteur de mise à l'échelle des distances",
        'impact': "100 = précision au 1/100 km",
        'example': "100 pour éviter dépassement LKH"
    }
}

# Presets
PRESETS = {
    'rapid': {
        'name': '🚀 Rapide',
        'RUNS': 1,
        'MOVE_TYPE': 5,
        'MAX_TRIALS': 500,
        'POPULATION_SIZE': 1,
        'RECOMBINATION': 'CLARIST',
        'PATCHING_C': 3,
        'PATCHING_A': 2,
        'description': "~10 sec - Pour tests rapides"
    },
    'balanced': {
        'name': '⚖️ Équilibré',
        'RUNS': 5,
        'MOVE_TYPE': 5,
        'MAX_TRIALS': 1000,
        'POPULATION_SIZE': 3,
        'RECOMBINATION': 'CLARIST',
        'PATCHING_C': 3,
        'PATCHING_A': 2,
        'description': "~1 min - Bon compromis qualité/temps"
    },
    'quality': {
        'name': '💎 Qualité',
        'RUNS': 10,
        'MOVE_TYPE': 5,
        'MAX_TRIALS': 2000,
        'POPULATION_SIZE': 5,
        'RECOMBINATION': 'CLARIST',
        'PATCHING_C': 3,
        'PATCHING_A': 2,
        'description': "~5 min - Meilleure qualité"
    }
}


# =============================================================================
# MAIN GUI CLASS
# =============================================================================
class LKHVisionSolver:
    def __init__(self, root):
        self.root = root
        self.root.title(APP_TITLE)
        self.root.geometry("950x850")
        self.root.minsize(850, 750)
        self.root.configure(bg=COLORS['bg'])
        
        # Set icon
        self._set_icon()
        
        # Variables
        self.file_path = tk.StringVar()
        self.id_col = tk.StringVar(value='commune')
        self.lat_col = tk.StringVar(value='Y-coordinate')
        self.lon_col = tk.StringVar(value='X-coordinate')
        self.columns = []
        
        # Parameter variables
        self.params = {}
        for param, info in LKH_PARAMS.items():
            if param == 'RECOMBINATION':
                self.params[param] = tk.StringVar(value=info['default'])
            else:
                self.params[param] = tk.IntVar(value=info['default'])
        
        # State variables
        self.is_running = False
        self.process = None
        self.start_time = None
        
        # Result paths
        self.tsp_path = None
        self.par_path = None
        self.tour_path = None
        self.excel_path = None
        self.map_path = None
        self.total_distance = None
        
        # Setup UI
        self._setup_styles()
        self._create_ui()
        
    def _set_icon(self):
        """Set application icon."""
        try:
            if os.path.exists(PATHS['icon']):
                icon = Image.open(PATHS['icon'])
                icon = icon.resize((32, 32), Image.Resampling.LANCZOS)
                self.icon_photo = ImageTk.PhotoImage(icon)
                self.root.iconphoto(True, self.icon_photo)
        except Exception as e:
            print(f"Impossible de charger l'icône: {e}")
        
    def _setup_styles(self):
        """Configure ttk styles."""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure styles
        style.configure('TFrame', background=COLORS['bg'])
        style.configure('Card.TFrame', background=COLORS['bg_light'])
        style.configure('TLabel', background=COLORS['bg'], foreground=COLORS['text'], font=('Segoe UI', 10))
        style.configure('Header.TLabel', font=('Segoe UI', 12, 'bold'), foreground=COLORS['primary'])
        style.configure('Title.TLabel', font=('Segoe UI', 18, 'bold'), foreground=COLORS['text'])
        style.configure('Muted.TLabel', foreground=COLORS['text_muted'], font=('Segoe UI', 9))
        style.configure('Success.TLabel', foreground=COLORS['success'], font=('Segoe UI', 12, 'bold'))
        style.configure('Copyright.TLabel', foreground=COLORS['text_muted'], font=('Segoe UI', 8))
        
        style.configure('TButton', font=('Segoe UI', 10), padding=8)
        style.configure('Primary.TButton', font=('Segoe UI', 12, 'bold'))
        style.configure('Accent.TButton', font=('Segoe UI', 10))
        
        style.configure('TCombobox', font=('Segoe UI', 10))
        style.configure('TSpinbox', font=('Segoe UI', 10))
        
        style.configure('Horizontal.TProgressbar', thickness=25)
        
    def _create_ui(self):
        """Create the main UI layout."""
        # Main container with padding
        main_frame = ttk.Frame(self.root, padding=15, style='TFrame')
        main_frame.pack(fill='both', expand=True)
        
        # Configure grid weights for responsiveness
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        # Title bar
        self._create_title_bar(main_frame)
        
        # Content area (scrollable) using grid for better resize
        content_frame = ttk.Frame(main_frame, style='TFrame')
        content_frame.pack(fill='both', expand=True, pady=(10, 0))
        content_frame.columnconfigure(0, weight=1)
        content_frame.rowconfigure(0, weight=1)
        
        canvas = tk.Canvas(content_frame, bg=COLORS['bg'], highlightthickness=0)
        scrollbar = ttk.Scrollbar(content_frame, orient="vertical", command=canvas.yview)
        self.scrollable_frame = ttk.Frame(canvas, style='TFrame')
        
        # Create window in canvas
        self.canvas_window = canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        
        # Bind configure events for responsive resize
        def _on_frame_configure(event):
            canvas.configure(scrollregion=canvas.bbox("all"))
        
        def _on_canvas_configure(event):
            # Make scrollable frame width match canvas width
            canvas.itemconfig(self.canvas_window, width=event.width)
        
        self.scrollable_frame.bind("<Configure>", _on_frame_configure)
        canvas.bind("<Configure>", _on_canvas_configure)
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Mouse wheel scrolling
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        # Use grid for canvas and scrollbar
        canvas.grid(row=0, column=0, sticky='nsew')
        scrollbar.grid(row=0, column=1, sticky='ns')
        
        # Sections
        self._create_import_section(self.scrollable_frame)
        self._create_params_section(self.scrollable_frame)
        self._create_execution_section(self.scrollable_frame)
        self._create_results_section(self.scrollable_frame)
        
        # Footer
        self._create_footer(main_frame)
        
    def _create_title_bar(self, parent):
        """Create title bar with logo."""
        title_frame = ttk.Frame(parent, style='TFrame')
        title_frame.pack(fill='x', pady=(0, 10))
        
        # Try to load icon for title
        try:
            if os.path.exists(PATHS['icon']):
                icon = Image.open(PATHS['icon'])
                icon = icon.resize((40, 40), Image.Resampling.LANCZOS)
                self.title_icon = ImageTk.PhotoImage(icon)
                ttk.Label(title_frame, image=self.title_icon, background=COLORS['bg']).pack(side='left', padx=(0, 10))
        except:
            pass
            
        ttk.Label(title_frame, text=APP_TITLE, style='Title.TLabel').pack(side='left')
        ttk.Label(title_frame, text=f"v{APP_VERSION}", style='Muted.TLabel').pack(side='left', padx=10)
        
        # Developer label on right
        dev_frame = ttk.Frame(title_frame, style='TFrame')
        dev_frame.pack(side='right')
        ttk.Label(dev_frame, text=f"Développé par {DEVELOPER}", style='Muted.TLabel').pack()
        
    def _create_card(self, parent, title, icon=""):
        """Create a card-style frame with title."""
        card = ttk.Frame(parent, style='Card.TFrame', padding=15)
        card.pack(fill='both', expand=True, pady=8, padx=5)
        
        # Card header
        header = ttk.Frame(card, style='Card.TFrame')
        header.pack(fill='x', pady=(0, 10))
        ttk.Label(header, text=f"{icon} {title}", style='Header.TLabel', 
                  background=COLORS['bg_light']).pack(side='left')
        
        return card
    
    def _create_import_section(self, parent):
        """Create file import section."""
        card = self._create_card(parent, "IMPORT DONNÉES", "📁")
        
        # File selection row
        file_frame = ttk.Frame(card, style='Card.TFrame')
        file_frame.pack(fill='x', pady=5)
        
        ttk.Button(file_frame, text="📂 Sélectionner fichier Excel/CSV", 
                   command=self._select_file).pack(side='left', padx=(0, 10))
        
        self.file_label = ttk.Label(file_frame, text="Aucun fichier sélectionné", 
                                     style='Muted.TLabel', background=COLORS['bg_light'])
        self.file_label.pack(side='left', fill='x', expand=True)
        
        # Columns selection
        cols_frame = ttk.Frame(card, style='Card.TFrame')
        cols_frame.pack(fill='x', pady=10)
        
        # ID Column
        ttk.Label(cols_frame, text="Colonne ID:", background=COLORS['bg_light']).pack(side='left')
        self.id_combo = ttk.Combobox(cols_frame, textvariable=self.id_col, width=15)
        self.id_combo.pack(side='left', padx=(5, 20))
        
        # Latitude Column
        ttk.Label(cols_frame, text="Latitude:", background=COLORS['bg_light']).pack(side='left')
        self.lat_combo = ttk.Combobox(cols_frame, textvariable=self.lat_col, width=15)
        self.lat_combo.pack(side='left', padx=(5, 20))
        
        # Longitude Column
        ttk.Label(cols_frame, text="Longitude:", background=COLORS['bg_light']).pack(side='left')
        self.lon_combo = ttk.Combobox(cols_frame, textvariable=self.lon_col, width=15)
        self.lon_combo.pack(side='left', padx=5)
        
        # Info label
        self.data_info = ttk.Label(card, text="", style='Muted.TLabel', 
                                    background=COLORS['bg_light'])
        self.data_info.pack(fill='x', pady=(5, 0))
        
    def _create_params_section(self, parent):
        """Create LKH parameters section."""
        card = self._create_card(parent, "PARAMÈTRES LKH", "⚙️")
        
        # Presets buttons
        preset_frame = ttk.Frame(card, style='Card.TFrame')
        preset_frame.pack(fill='x', pady=(0, 15))
        
        ttk.Label(preset_frame, text="Préréglages:", 
                  background=COLORS['bg_light']).pack(side='left', padx=(0, 10))
        
        for preset_key, preset in PRESETS.items():
            btn = ttk.Button(preset_frame, text=preset['name'],
                            command=lambda p=preset_key: self._apply_preset(p))
            btn.pack(side='left', padx=5)
        
        # Preset description
        self.preset_desc = ttk.Label(card, text="💡 Sélectionnez un préréglage ou personnalisez les paramètres",
                                      style='Muted.TLabel', background=COLORS['bg_light'])
        self.preset_desc.pack(fill='x', pady=(0, 10))
        
        # Parameters grid
        params_container = ttk.Frame(card, style='Card.TFrame')
        params_container.pack(fill='x')
        
        # Create parameter controls in grid
        row = 0
        col = 0
        for param, info in LKH_PARAMS.items():
            if param == 'SCALE':
                continue  # Scale handled separately
                
            frame = ttk.Frame(params_container, style='Card.TFrame')
            frame.grid(row=row, column=col, padx=10, pady=8, sticky='w')
            
            # Label with tooltip indicator
            label_text = f"{param} ⓘ"
            label = ttk.Label(frame, text=label_text, background=COLORS['bg_light'],
                             cursor='question_arrow')
            label.pack(anchor='w')
            
            # Tooltip binding
            self._create_tooltip(label, info)
            
            # Control widget
            if 'options' in info:
                ctrl = ttk.Combobox(frame, textvariable=self.params[param],
                                   values=info['options'], width=12, state='readonly')
            else:
                ctrl = ttk.Spinbox(frame, textvariable=self.params[param],
                                  from_=info['min'], to=info['max'], width=10)
            ctrl.pack(anchor='w', pady=(2, 0))
            
            col += 1
            if col >= 4:
                col = 0
                row += 1
        
        # Scale parameter (separate row)
        scale_frame = ttk.Frame(card, style='Card.TFrame')
        scale_frame.pack(fill='x', pady=(10, 0))
        
        scale_info = LKH_PARAMS['SCALE']
        ttk.Label(scale_frame, text="SCALE (Précision) ⓘ", 
                  background=COLORS['bg_light']).pack(side='left')
        scale_spin = ttk.Spinbox(scale_frame, textvariable=self.params['SCALE'],
                                from_=scale_info['min'], to=scale_info['max'], width=8)
        scale_spin.pack(side='left', padx=10)
        ttk.Label(scale_frame, text="(100 = précision au 1/100 km)", 
                  style='Muted.TLabel', background=COLORS['bg_light']).pack(side='left')
        
    def _create_tooltip(self, widget, info):
        """Create tooltip for parameter explanation."""
        def show_tooltip(event):
            tooltip = tk.Toplevel(widget)
            tooltip.wm_overrideredirect(True)
            tooltip.wm_geometry(f"+{event.x_root+10}+{event.y_root+10}")
            tooltip.configure(bg=COLORS['accent'])
            
            frame = tk.Frame(tooltip, bg=COLORS['accent'], padx=10, pady=8)
            frame.pack()
            
            tk.Label(frame, text=info['description'], bg=COLORS['accent'], 
                    fg=COLORS['text'], font=('Segoe UI', 10, 'bold')).pack(anchor='w')
            tk.Label(frame, text=info['impact'], bg=COLORS['accent'], 
                    fg=COLORS['warning'], font=('Segoe UI', 9)).pack(anchor='w', pady=(5,0))
            tk.Label(frame, text=f"💡 {info['example']}", bg=COLORS['accent'], 
                    fg=COLORS['text_muted'], font=('Segoe UI', 9)).pack(anchor='w', pady=(5,0))
            
            widget.tooltip = tooltip
            
        def hide_tooltip(event):
            if hasattr(widget, 'tooltip'):
                widget.tooltip.destroy()
                
        widget.bind('<Enter>', show_tooltip)
        widget.bind('<Leave>', hide_tooltip)
        
    def _create_execution_section(self, parent):
        """Create execution/progress section."""
        card = self._create_card(parent, "EXÉCUTION", "▶️")
        
        # Buttons row
        btn_frame = ttk.Frame(card, style='Card.TFrame')
        btn_frame.pack(fill='x', pady=(0, 10))
        
        self.start_btn = ttk.Button(btn_frame, text="▶ LANCER OPTIMISATION",
                                    style='Primary.TButton', command=self._start_optimization)
        self.start_btn.pack(side='left', padx=(0, 10))
        
        self.stop_btn = ttk.Button(btn_frame, text="■ Arrêter", 
                                   command=self._stop_optimization, state='disabled')
        self.stop_btn.pack(side='left')
        
        # Progress bar
        progress_frame = ttk.Frame(card, style='Card.TFrame')
        progress_frame.pack(fill='x', pady=10)
        
        self.progress = ttk.Progressbar(progress_frame, mode='determinate')
        self.progress.pack(fill='x', expand=True)
        
        self.progress_label = ttk.Label(progress_frame, text="En attente...", 
                                         style='Muted.TLabel', background=COLORS['bg_light'])
        self.progress_label.pack(pady=(5, 0))
        
        # Time info
        time_frame = ttk.Frame(card, style='Card.TFrame')
        time_frame.pack(fill='x')
        
        self.time_label = ttk.Label(time_frame, text="", style='Muted.TLabel',
                                     background=COLORS['bg_light'])
        self.time_label.pack(side='left')
        
        # Console output
        console_frame = ttk.Frame(card, style='Card.TFrame')
        console_frame.pack(fill='both', expand=True, pady=(10, 0))
        
        console_header = ttk.Frame(console_frame, style='Card.TFrame')
        console_header.pack(fill='x')
        ttk.Label(console_header, text="📟 Console LKH:", 
                  background=COLORS['bg_light']).pack(side='left')
                  
        ttk.Button(console_header, text="🗑️ Effacer", 
                   command=self._clear_console).pack(side='right')
        
        self.console = scrolledtext.ScrolledText(console_frame, height=10,
                                                  bg='#0a0a15', fg='#00ff00',
                                                  font=('Consolas', 9), state='disabled')
        self.console.pack(fill='both', expand=True, pady=(5, 0))
        
    def _create_results_section(self, parent):
        """Create results section."""
        self.results_card = self._create_card(parent, "RÉSULTATS", "📊")
        
        # Status label
        self.result_status = ttk.Label(self.results_card, text="⏳ En attente d'exécution...",
                                        background=COLORS['bg_light'])
        self.result_status.pack(fill='x', pady=(0, 10))
        
        # Distance display
        self.distance_label = ttk.Label(self.results_card, text="", style='Success.TLabel',
                                         background=COLORS['bg_light'])
        self.distance_label.pack(fill='x', pady=5)
        
        # Action buttons
        action_frame = ttk.Frame(self.results_card, style='Card.TFrame')
        action_frame.pack(fill='x', pady=10)
        
        self.tour_btn = ttk.Button(action_frame, text="📄 Inspecter .tour",
                                   command=self._open_tour, state='disabled')
        self.tour_btn.pack(side='left', padx=5)
        
        self.excel_btn = ttk.Button(action_frame, text="📊 Inspecter Excel",
                                    command=self._open_excel, state='disabled')
        self.excel_btn.pack(side='left', padx=5)
        
        self.map_btn = ttk.Button(action_frame, text="🗺️ Inspecter Carte",
                                  command=self._open_map, state='disabled')
        self.map_btn.pack(side='left', padx=5)
        
        # Open folder button
        self.folder_btn = ttk.Button(action_frame, text="📁 Ouvrir dossier résultats",
                                     command=self._open_results_folder, state='disabled')
        self.folder_btn.pack(side='right', padx=5)
        
    def _create_footer(self, parent):
        """Create footer with copyright."""
        footer = ttk.Frame(parent, style='TFrame')
        footer.pack(fill='x', pady=(10, 0))
        
        ttk.Label(footer, text=COPYRIGHT, style='Copyright.TLabel').pack(side='right')
        ttk.Label(footer, text=f"Développé par {DEVELOPER}", style='Copyright.TLabel').pack(side='left')
        
    # =========================================================================
    # ACTIONS
    # =========================================================================
    
    def _select_file(self):
        """Open file dialog to select input file."""
        file_path = filedialog.askopenfilename(
            title="Sélectionner fichier de données",
            initialdir=PATHS['excel_imported'],
            filetypes=[
                ("Excel files", "*.xlsx *.xls"),
                ("CSV files", "*.csv"),
                ("All files", "*.*")
            ]
        )
        
        if file_path:
            # Copy to Imported folder
            filename = os.path.basename(file_path)
            imported_path = os.path.join(PATHS['excel_imported'], filename)
            
            if file_path != imported_path:
                try:
                    shutil.copy2(file_path, imported_path)
                    self._log_console(f"📁 Fichier copié vers: Excel/Imported/{filename}")
                except:
                    imported_path = file_path
                    
            self.file_path.set(imported_path)
            self.file_label.config(text=filename)
            self._load_columns(imported_path)
            
    def _load_columns(self, file_path):
        """Load column names from file."""
        try:
            ext = os.path.splitext(file_path)[1].lower()
            if ext in ['.xlsx', '.xls']:
                df = pd.read_excel(file_path, nrows=5)
            else:
                df = pd.read_csv(file_path, nrows=5)
            
            self.columns = df.columns.tolist()
            
            # Update comboboxes
            self.id_combo['values'] = self.columns
            self.lat_combo['values'] = self.columns
            self.lon_combo['values'] = self.columns
            
            # Auto-detect columns
            for col in self.columns:
                col_lower = col.lower()
                if 'id' in col_lower or 'commune' in col_lower or 'name' in col_lower:
                    self.id_col.set(col)
                elif 'lat' in col_lower or 'y' in col_lower:
                    self.lat_col.set(col)
                elif 'lon' in col_lower or 'x' in col_lower:
                    self.lon_col.set(col)
            
            # Show info
            full_df = pd.read_excel(file_path) if ext in ['.xlsx', '.xls'] else pd.read_csv(file_path)
            self.data_info.config(text=f"✅ {len(full_df)} points chargés | Colonnes détectées automatiquement")
            self._log_console(f"✅ Fichier chargé: {len(full_df)} points, {len(self.columns)} colonnes")
            
        except Exception as e:
            messagebox.showerror("Erreur", f"Impossible de lire le fichier:\n{e}")
            
    def _apply_preset(self, preset_key):
        """Apply a parameter preset."""
        preset = PRESETS[preset_key]
        for param, value in preset.items():
            if param not in ['name', 'description'] and param in self.params:
                self.params[param].set(value)
        
        self.preset_desc.config(text=f"💡 {preset['name']}: {preset['description']}")
        self._log_console(f"⚙️ Préréglage '{preset['name']}' appliqué")
        
    def _log_console(self, message):
        """Log message to console."""
        self.console.config(state='normal')
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.console.insert('end', f"[{timestamp}] {message}\n")
        self.console.see('end')
        self.console.config(state='disabled')
        
    def _clear_console(self):
        """Clear console."""
        self.console.config(state='normal')
        self.console.delete('1.0', 'end')
        self.console.config(state='disabled')
        
    def _start_optimization(self):
        """Start the optimization process."""
        if not self.file_path.get():
            messagebox.showwarning("Attention", "Veuillez sélectionner un fichier de données")
            return
            
        self.is_running = True
        self.start_btn.config(state='disabled')
        self.stop_btn.config(state='normal')
        self.result_status.config(text="⏳ Optimisation en cours...")
        
        # Run in separate thread
        thread = threading.Thread(target=self._run_optimization)
        thread.daemon = True
        thread.start()
        
    def _stop_optimization(self):
        """Stop the optimization process."""
        self.is_running = False
        if self.process:
            self.process.terminate()
        self._log_console("⚠️ Arrêt demandé par l'utilisateur")
        self._reset_ui()
        
    def _reset_ui(self):
        """Reset UI to initial state."""
        self.start_btn.config(state='normal')
        self.stop_btn.config(state='disabled')
        self.progress['value'] = 0
        self.progress_label.config(text="En attente...")
        
    def _run_optimization(self):
        """Run the full optimization pipeline (in thread)."""
        try:
            self.start_time = time.time()
            base_name = os.path.splitext(os.path.basename(self.file_path.get()))[0]
            base_name = base_name.replace(' ', '_')
            
            # Step 1: Convert to TSP
            self._log_console("📁 Étape 1/4: Conversion Excel → TSP...")
            self.root.after(0, lambda: self.progress_label.config(text="Étape 1/4: Conversion vers TSP..."))
            self.root.after(0, lambda: setattr(self.progress, 'value', 10))
            
            converter = ExcelToTSPConverter(
                input_path=self.file_path.get(),
                id_col=self.id_col.get(),
                lat_col=self.lat_col.get(),
                lon_col=self.lon_col.get(),
                scale=self.params['SCALE'].get()
            )
            
            # Save TSP to Data folder, PAR to config folder
            self.tsp_path = os.path.join(PATHS['data'], f"{base_name}.tsp")
            self.par_path = os.path.join(PATHS['config'], f"{base_name}.par")
            self.tour_path = os.path.join(PATHS['result'], f"{base_name}.tour")
            
            converter.compute_distance_matrix()
            converter.generate_tsp_file(self.tsp_path, base_name)
            
            self._log_console(f"✅ TSP créé: LKH_data/Data/{base_name}.tsp")
            
            if not self.is_running:
                return
            
            # Step 2: Create PAR file with user parameters
            self._log_console("⚙️ Étape 2/4: Configuration LKH...")
            self.root.after(0, lambda: setattr(self.progress, 'value', 20))
            self._create_par_file()
            self._log_console(f"✅ Config créée: LKH_data/config/{base_name}.par")
            
            # Step 3: Run LKH
            self._log_console("🚀 Étape 3/4: Optimisation LKH en cours...")
            self.root.after(0, lambda: self.progress_label.config(text="Étape 3/4: Optimisation LKH..."))
            self.root.after(0, lambda: setattr(self.progress, 'value', 30))
            
            self._run_lkh()
            
            if not self.is_running:
                return
            
            # Step 4: Convert results
            self._log_console("📊 Étape 4/4: Export des résultats...")
            self.root.after(0, lambda: self.progress_label.config(text="Étape 4/4: Export résultats..."))
            self.root.after(0, lambda: setattr(self.progress, 'value', 80))
            
            self.excel_path = os.path.join(PATHS['excel_results'], f"{base_name}_result.xlsx")
            
            tour_converter = TourToExcelConverter(
                tour_path=self.tour_path,
                original_data_path=self.file_path.get(),
                id_col=self.id_col.get(),
                lat_col=self.lat_col.get(),
                lon_col=self.lon_col.get()
            )
            tour_converter.generate_output(self.excel_path)
            
            # Calculate actual distance
            self._calculate_distance(tour_converter)
            
            self._log_console(f"✅ Excel créé: Excel/results/{base_name}_result.xlsx")
            
            # Step 5: Generate map
            self._log_console("🗺️ Génération de la carte...")
            self.root.after(0, lambda: setattr(self.progress, 'value', 90))
            
            self.map_path = os.path.join(PATHS['map_view'], f"{base_name}_map.html")
            self._generate_map(tour_converter)
            
            # Done!
            self.root.after(0, lambda: setattr(self.progress, 'value', 100))
            elapsed = time.time() - self.start_time
            self._log_console(f"🎉 Optimisation terminée en {elapsed:.1f} secondes!")
            self._log_console(f"📏 Distance totale: {self.total_distance:,.2f} km")
            
            # Update results
            self.root.after(0, self._show_results)
            
        except Exception as e:
            self._log_console(f"❌ Erreur: {e}")
            self.root.after(0, lambda: messagebox.showerror("Erreur", str(e)))
            
        finally:
            self.root.after(0, self._reset_ui)
            
    def _create_par_file(self):
        """Create PAR file with user parameters."""
        with open(self.par_path, 'w', encoding='utf-8') as f:
            f.write(f"PROBLEM_FILE = {self.tsp_path}\n")
            f.write(f"MOVE_TYPE = {self.params['MOVE_TYPE'].get()}\n")
            f.write(f"PATCHING_C = {self.params['PATCHING_C'].get()}\n")
            f.write(f"PATCHING_A = {self.params['PATCHING_A'].get()}\n")
            f.write(f"RUNS = {self.params['RUNS'].get()}\n")
            f.write(f"MAX_TRIALS = {self.params['MAX_TRIALS'].get()}\n")
            if self.params['POPULATION_SIZE'].get() > 1:
                f.write(f"POPULATION_SIZE = {self.params['POPULATION_SIZE'].get()}\n")
                f.write(f"RECOMBINATION = {self.params['RECOMBINATION'].get()}\n")
            f.write(f"TOUR_FILE = {self.tour_path}\n")
            
    def _run_lkh(self):
        """Run LKH executable."""
        self.process = subprocess.Popen(
            [PATHS['lkh_exe'], self.par_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )
        
        runs = self.params['RUNS'].get()
        current_run = 0
        
        for line in self.process.stdout:
            if not self.is_running:
                break
                
            line = line.strip()
            if line:
                self._log_console(line)
                
                # Parse progress
                if line.startswith('Run '):
                    try:
                        parts = line.split(':')
                        run_part = parts[0].replace('Run ', '').strip()
                        current_run = int(run_part)
                        progress = 30 + (current_run / runs) * 50
                        self.root.after(0, lambda p=progress: setattr(self.progress, 'value', p))
                        self.root.after(0, lambda r=current_run: self.progress_label.config(text=f"Run {r}/{runs}..."))
                        
                        elapsed = time.time() - self.start_time
                        if current_run > 0:
                            estimated = (elapsed / current_run) * runs
                            remaining = max(0, estimated - elapsed)
                            self.root.after(0, lambda e=elapsed, r=remaining: self.time_label.config(
                                text=f"⏱️ Écoulé: {e:.0f}s | Restant estimé: {r:.0f}s"
                            ))
                    except:
                        pass
                        
        self.process.wait()
        
    def _calculate_distance(self, converter):
        """Calculate total tour distance in km."""
        tour_order = converter.tour_order
        df = converter.original_df
        lat_col = converter.lat_col
        lon_col = converter.lon_col
        
        total = 0.0
        for i in range(len(tour_order)):
            idx1 = tour_order[i] - 1
            idx2 = tour_order[(i + 1) % len(tour_order)] - 1
            
            lat1 = df.iloc[idx1][lat_col]
            lon1 = df.iloc[idx1][lon_col]
            lat2 = df.iloc[idx2][lat_col]
            lon2 = df.iloc[idx2][lon_col]
            
            total += haversine_distance(lat1, lon1, lat2, lon2)
            
        self.total_distance = total
        
    def _generate_map(self, converter):
        """Generate the HTML map."""
        try:
            tour_order = converter.tour_order
            df = converter.original_df
            
            viz.create_tour_map(
                df, tour_order,
                converter.id_col, converter.lat_col, converter.lon_col,
                self.map_path, self.params['SCALE'].get()
            )
            self._log_console(f"✅ Carte créée: Map_view/{os.path.basename(self.map_path)}")
        except Exception as e:
            self._log_console(f"⚠️ Carte non générée: {e}")
            self.map_path = None
            
    def _show_results(self):
        """Update UI with results."""
        self.result_status.config(text="✅ Optimisation terminée avec succès!")
        
        if self.total_distance:
            self.distance_label.config(
                text=f"📏 Distance totale optimisée: {self.total_distance:,.2f} km"
            )
        
        self.tour_btn.config(state='normal')
        self.excel_btn.config(state='normal')
        self.folder_btn.config(state='normal')
        if self.map_path and os.path.exists(self.map_path):
            self.map_btn.config(state='normal')
            
    def _open_tour(self):
        """Open tour file in default app."""
        if self.tour_path and os.path.exists(self.tour_path):
            os.startfile(self.tour_path)
            
    def _open_excel(self):
        """Open Excel file."""
        if self.excel_path and os.path.exists(self.excel_path):
            os.startfile(self.excel_path)
            
    def _open_map(self):
        """Open map in browser."""
        if self.map_path and os.path.exists(self.map_path):
            webbrowser.open(f'file://{os.path.abspath(self.map_path)}')
            
    def _open_results_folder(self):
        """Open results folder in explorer."""
        os.startfile(PATHS['excel_results'])


# =============================================================================
# MAIN
# =============================================================================
def main():
    root = tk.Tk()
    app = LKHVisionSolver(root)
    root.mainloop()


if __name__ == '__main__':
    main()
