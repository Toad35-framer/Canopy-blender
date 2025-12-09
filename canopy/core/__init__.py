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
# ══════════════════════════════════════════════════════════════════════════════

from .state import (
    canopy_state,
    get_state,
    redraw_viewport,
    get_3d_view_context,
    # Classes d'état individuelles (pour typage)
    CanopyState,
    SnapCircleState,
    PlanManagerState,
    RECState,
    CutSouderState,
    VisibilityState,
)

from .events import (
    canopy_events,
    EventType,
    Event,
    EventManager,
    on_event,
)


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

__version__ = "2.0.0"


# ══════════════════════════════════════════════════════════════════════════════
# ENREGISTREMENT BLENDER (pas nécessaire pour core, mais garde la cohérence)
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
