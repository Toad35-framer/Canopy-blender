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
# ══════════════════════════════════════════════════════════════════════════════

import bpy

# Imports des sous-modules
from . import core
from . import renderer
from . import operators
from . import movement
from . import rotation
from . import ui_panel
from . import ui_pie_menus
from . import properties
from . import keymap


# ══════════════════════════════════════════════════════════════════════════════
# EXPORTS PUBLICS
# ══════════════════════════════════════════════════════════════════════════════

# Core
from .core import (
    ElementDetector,
    HistoryManager,
    get_element_info,
    get_edge_direction_from_position,
)

# Renderer
from .renderer import (
    CircleRenderer,
    register_draw_handler,
    unregister_draw_handler,
)

__all__ = [
    'ElementDetector',
    'HistoryManager',
    'CircleRenderer',
    'get_element_info',
    'register_draw_handler',
    'unregister_draw_handler',
]

__version__ = "2.0.0"


# ══════════════════════════════════════════════════════════════════════════════
# ENREGISTREMENT
# ══════════════════════════════════════════════════════════════════════════════

def register():
    """Enregistre le module Snap Circle"""
    print("[CANOPY] Snap Circle: Enregistrement...")
    
    # Propriétés
    properties.register_properties()
    
    # Opérateurs
    for cls in operators.classes:
        bpy.utils.register_class(cls)
    
    for cls in movement.classes:
        bpy.utils.register_class(cls)
    
    for cls in rotation.classes:
        bpy.utils.register_class(cls)
    
    # UI
    for cls in ui_panel.classes:
        bpy.utils.register_class(cls)
    
    for cls in ui_pie_menus.classes:
        bpy.utils.register_class(cls)
    
    # Keymaps
    keymap.register_keymaps()
    
    print("[CANOPY] ✅ Snap Circle v2.0 activé")
    print("[CANOPY]    • Panneau: Sidebar N > CANOPY > Snap Circle")
    print("[CANOPY]    • Menu: Ctrl+Shift+S")


def unregister():
    """Désenregistre le module Snap Circle"""
    print("[CANOPY] Snap Circle: Désenregistrement...")
    
    # Nettoyer le draw handler
    renderer.unregister_draw_handler()
    
    # Keymaps
    keymap.unregister_keymaps()
    
    # UI
    for cls in reversed(ui_pie_menus.classes):
        try:
            bpy.utils.unregister_class(cls)
        except:
            pass
    
    for cls in reversed(ui_panel.classes):
        try:
            bpy.utils.unregister_class(cls)
        except:
            pass
    
    # Opérateurs
    for cls in reversed(rotation.classes):
        try:
            bpy.utils.unregister_class(cls)
        except:
            pass
    
    for cls in reversed(movement.classes):
        try:
            bpy.utils.unregister_class(cls)
        except:
            pass
    
    for cls in reversed(operators.classes):
        try:
            bpy.utils.unregister_class(cls)
        except:
            pass
    
    # Propriétés
    properties.unregister_properties()
    
    print("[CANOPY] Snap Circle désactivé")
