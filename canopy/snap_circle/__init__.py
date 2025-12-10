# ══════════════════════════════════════════════════════════════════════════════
# CANOPY V2 - Module Snap Circle
# Système de cercles de référence pour le positionnement précis
# ══════════════════════════════════════════════════════════════════════════════
#
# Ce module fournit un système de cercles de référence permettant de:
# - Placer des cercles sur des éléments de mesh (vertices, edges, faces)
# - Déplacer des objets entre les cercles
# - Effectuer des rotations précises
# - Aligner et distribuer des objets
#
# UTILISATION:
#   - Activer avec le bouton "Démarrer" dans le panneau CANOPY
#   - Cliquer sur des éléments pour placer les cercles
#   - Ctrl+Shift+S pour le menu radial
#
# CONVENTION DE NOMMAGE:
#   Tous les fichiers (sauf __init__.py) suivent le format: module-fichier.py
#   Exemple: snap_circle-core.py, snap_circle-renderer.py
#
# ══════════════════════════════════════════════════════════════════════════════

import bpy
import importlib
import importlib.util
import sys
from pathlib import Path

__version__ = "2.0.0"

# ══════════════════════════════════════════════════════════════════════════════
# SYSTÈME D'IMPORT POUR FICHIERS AVEC TIRETS
# ══════════════════════════════════════════════════════════════════════════════

def import_submodule(module_name: str, file_name: str):
    """
    Importe un sous-module depuis un fichier avec tiret dans le nom.
    
    Args:
        module_name: Nom du module parent (ex: 'canopy.snap_circle')
        file_name: Nom du fichier sans extension (ex: 'snap_circle-core')
    
    Returns:
        Le module importé
    """
    # Construire le chemin complet du module
    full_module_name = f"{module_name}.{file_name.replace('-', '_')}"
    
    # Si déjà importé, recharger
    if full_module_name in sys.modules:
        return importlib.reload(sys.modules[full_module_name])
    
    # Trouver le chemin du fichier
    current_dir = Path(__file__).parent
    file_path = current_dir / f"{file_name}.py"
    
    if not file_path.exists():
        raise ImportError(f"Fichier non trouvé: {file_path}")
    
    # Charger le module depuis le fichier
    spec = importlib.util.spec_from_file_location(full_module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[full_module_name] = module
    spec.loader.exec_module(module)
    
    return module


# ══════════════════════════════════════════════════════════════════════════════
# IMPORT DES SOUS-MODULES
# ══════════════════════════════════════════════════════════════════════════════

# Nom du module courant
_MODULE_NAME = __name__

# Liste des sous-modules à importer (ordre important)
_SUBMODULES = [
    'snap_circle-core',
    'snap_circle-renderer',
    'snap_circle-properties',
    'snap_circle-operators',
    'snap_circle-movement',
    'snap_circle-rotation',
    'snap_circle-ui_panel',
    'snap_circle-ui_pie_menus',
    'snap_circle-keymap',
]

# Dictionnaire pour stocker les modules importés
_loaded_modules = {}

def _load_all_submodules():
    """Charge tous les sous-modules"""
    global _loaded_modules
    for submodule_name in _SUBMODULES:
        try:
            _loaded_modules[submodule_name] = import_submodule(_MODULE_NAME, submodule_name)
        except Exception as e:
            print(f"[CANOPY Snap Circle] Erreur import {submodule_name}: {e}")

# Charger les modules au premier import
_load_all_submodules()

# Aliases pour accès facile
core = _loaded_modules.get('snap_circle-core')
renderer = _loaded_modules.get('snap_circle-renderer')
properties = _loaded_modules.get('snap_circle-properties')
operators = _loaded_modules.get('snap_circle-operators')
movement = _loaded_modules.get('snap_circle-movement')
rotation = _loaded_modules.get('snap_circle-rotation')
ui_panel = _loaded_modules.get('snap_circle-ui_panel')
ui_pie_menus = _loaded_modules.get('snap_circle-ui_pie_menus')
keymap = _loaded_modules.get('snap_circle-keymap')


# ══════════════════════════════════════════════════════════════════════════════
# EXPORTS PUBLICS
# ══════════════════════════════════════════════════════════════════════════════

# Core
if core:
    ElementDetector = core.ElementDetector
    HistoryManager = core.HistoryManager
    get_element_info = core.get_element_info
    get_edge_direction_from_position = core.get_edge_direction_from_position

# Renderer
if renderer:
    CircleRenderer = renderer.CircleRenderer
    register_draw_handler = renderer.register_draw_handler
    unregister_draw_handler = renderer.unregister_draw_handler

__all__ = [
    'ElementDetector',
    'HistoryManager',
    'CircleRenderer',
    'get_element_info',
    'register_draw_handler',
    'unregister_draw_handler',
]


# ══════════════════════════════════════════════════════════════════════════════
# ENREGISTREMENT
# ══════════════════════════════════════════════════════════════════════════════

def register():
    """Enregistre le module Snap Circle"""
    print("[CANOPY] Snap Circle: Enregistrement...")
    
    # Propriétés
    if properties:
        properties.register_properties()
    
    # Opérateurs
    if operators:
        for cls in operators.classes:
            bpy.utils.register_class(cls)
    
    if movement:
        for cls in movement.classes:
            bpy.utils.register_class(cls)
    
    if rotation:
        for cls in rotation.classes:
            bpy.utils.register_class(cls)
    
    # UI
    if ui_panel:
        for cls in ui_panel.classes:
            bpy.utils.register_class(cls)
    
    if ui_pie_menus:
        for cls in ui_pie_menus.classes:
            bpy.utils.register_class(cls)
    
    # Keymaps
    if keymap:
        keymap.register_keymaps()
    
    print("[CANOPY] ✅ Snap Circle v2.0 activé")
    print("[CANOPY]    • Panneau: Sidebar N > CANOPY > Snap Circle")
    print("[CANOPY]    • Menu: Ctrl+Shift+S")


def unregister():
    """Désenregistre le module Snap Circle"""
    print("[CANOPY] Snap Circle: Désenregistrement...")
    
    # Nettoyer le draw handler
    if renderer:
        renderer.unregister_draw_handler()
    
    # Keymaps
    if keymap:
        keymap.unregister_keymaps()
    
    # UI
    if ui_pie_menus:
        for cls in reversed(ui_pie_menus.classes):
            try:
                bpy.utils.unregister_class(cls)
            except:
                pass
    
    if ui_panel:
        for cls in reversed(ui_panel.classes):
            try:
                bpy.utils.unregister_class(cls)
            except:
                pass
    
    # Opérateurs
    if rotation:
        for cls in reversed(rotation.classes):
            try:
                bpy.utils.unregister_class(cls)
            except:
                pass
    
    if movement:
        for cls in reversed(movement.classes):
            try:
                bpy.utils.unregister_class(cls)
            except:
                pass
    
    if operators:
        for cls in reversed(operators.classes):
            try:
                bpy.utils.unregister_class(cls)
            except:
                pass
    
    # Propriétés
    if properties:
        properties.unregister_properties()
    
    print("[CANOPY] Snap Circle désactivé")
