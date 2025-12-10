# ══════════════════════════════════════════════════════════════════════════════
# CANOPY V2 - Module Core
# Fondations partagées par tous les modules
# ══════════════════════════════════════════════════════════════════════════════
#
# Ce module fournit les éléments de base utilisés par tous les autres modules:
# - État global partagé (canopy_state)
# - Système d'événements (canopy_events)
# - Fonctions utilitaires communes
#
# UTILISATION:
#   from canopy.core import canopy_state, canopy_events
#   from canopy.core import redraw_viewport, get_3d_view_context
#
# CONVENTION DE NOMMAGE:
#   Tous les fichiers (sauf __init__.py) suivent le format: module-fichier.py
#   Exemple: core-state.py, core-events.py
#
# ══════════════════════════════════════════════════════════════════════════════

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
        module_name: Nom du module parent (ex: 'canopy.core')
        file_name: Nom du fichier sans extension (ex: 'core-state')
    
    Returns:
        Le module importé
    """
    full_module_name = f"{module_name}.{file_name.replace('-', '_')}"
    
    if full_module_name in sys.modules:
        return sys.modules[full_module_name]
    
    current_dir = Path(__file__).parent
    file_path = current_dir / f"{file_name}.py"
    
    if not file_path.exists():
        raise ImportError(f"Fichier non trouvé: {file_path}")
    
    spec = importlib.util.spec_from_file_location(full_module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[full_module_name] = module
    spec.loader.exec_module(module)
    
    return module


# ══════════════════════════════════════════════════════════════════════════════
# IMPORT DES SOUS-MODULES
# ══════════════════════════════════════════════════════════════════════════════

_MODULE_NAME = __name__

# Charger les modules
_state_module = import_submodule(_MODULE_NAME, 'core-state')
_events_module = import_submodule(_MODULE_NAME, 'core-events')


# ══════════════════════════════════════════════════════════════════════════════
# EXPORTS DEPUIS STATE
# ══════════════════════════════════════════════════════════════════════════════

canopy_state = _state_module.canopy_state
get_state = _state_module.get_state
redraw_viewport = _state_module.redraw_viewport
get_3d_view_context = _state_module.get_3d_view_context

# Classes d'état (pour typage)
CanopyState = _state_module.CanopyState
SnapCircleState = _state_module.SnapCircleState
PlanManagerState = _state_module.PlanManagerState
RECState = _state_module.RECState
CutSouderState = _state_module.CutSouderState
VisibilityState = _state_module.VisibilityState


# ══════════════════════════════════════════════════════════════════════════════
# EXPORTS DEPUIS EVENTS
# ══════════════════════════════════════════════════════════════════════════════

canopy_events = _events_module.canopy_events
EventType = _events_module.EventType
Event = _events_module.Event
EventManager = _events_module.EventManager
on_event = _events_module.on_event


# ══════════════════════════════════════════════════════════════════════════════
# EXPORTS PUBLICS
# ══════════════════════════════════════════════════════════════════════════════

__all__ = [
    # État global
    'canopy_state',
    'get_state',
    
    # Événements
    'canopy_events',
    'EventType',
    'on_event',
    
    # Utilitaires
    'redraw_viewport',
    'get_3d_view_context',
    
    # Classes (pour typage)
    'CanopyState',
    'SnapCircleState',
    'PlanManagerState',
    'RECState',
    'CutSouderState',
    'VisibilityState',
    'Event',
    'EventManager',
]


# ══════════════════════════════════════════════════════════════════════════════
# ENREGISTREMENT BLENDER
# ══════════════════════════════════════════════════════════════════════════════

def register():
    """Initialise le module Core"""
    print("[CANOPY Core] Module Core initialisé")
    canopy_events.emit(EventType.CANOPY_INITIALIZED)


def unregister():
    """Nettoie le module Core"""
    canopy_events.emit(EventType.CANOPY_SHUTDOWN)
    canopy_state.reset_all()
    canopy_events.clear_subscribers()
    print("[CANOPY Core] Module Core nettoyé")
