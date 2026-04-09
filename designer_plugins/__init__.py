"""
Inizializzazione plugin per Qt Designer
"""

import sys
import os

# Aggiungi path progetto
plugin_dir = os.path.dirname(os.path.abspath(__file__))
project_dir = os.path.dirname(plugin_dir)

if project_dir not in sys.path:
    sys.path.insert(0, project_dir)

print(f"[Designer Plugins] Path progetto aggiunto: {project_dir}")
print("[Designer Plugins] __init__.py caricato")
