# ══════════════════════════════════════════════════════════════════════════════
# CANOPY V2 - Core - État Global Partagé
# Gestion centralisée de l'état de l'application
# ══════════════════════════════════════════════════════════════════════════════
#
# Ce module fournit un état global accessible par tous les modules CANOPY.
# Il remplace les variables globales dispersées dans les anciens fichiers.
#
# UTILISATION:
#   from canopy.core.state import canopy_state
#   
#   # Accéder à l'état Snap Circle
#   canopy_state.snap_circle.primary_location
#   
#   # Accéder à l'état du Plan Manager
#   canopy_state.plan_manager.is_active
#
# ══════════════════════════════════════════════════════════════════════════════

import bpy
from mathutils import Vector
from typing import Optional, List, Dict, Any, Tuple
from dataclasses import dataclass, field


# ══════════════════════════════════════════════════════════════════════════════
# CLASSES D'ÉTAT PAR MODULE
# ══════════════════════════════════════════════════════════════════════════════

@dataclass
class SnapCircleState:
    """État du module Snap Circle"""
    
    # Cercle principal
    primary_location: Optional[Vector] = None
    primary_object: Optional[bpy.types.Object] = None
    primary_element_type: Optional[str] = None
    
    # Cercle secondaire
    secondary_location: Optional[Vector] = None
    secondary_object: Optional[bpy.types.Object] = None
    secondary_element_type: Optional[str] = None
    
    # Système
    draw_handler: Any = None
    is_active: bool = False
    
    # Historique
    history_stack: List[Dict[str, Any]] = field(default_factory=list)
    history_index: int = -1
    max_history_size: int = 10
    
    def reset(self):
        """Réinitialise l'état Snap Circle"""
        self.primary_location = None
        self.primary_object = None
        self.primary_element_type = None
        self.secondary_location = None
        self.secondary_object = None
        self.secondary_element_type = None
        self.history_stack.clear()
        self.history_index = -1
    
    def is_object_valid(self, obj: Optional[bpy.types.Object]) -> bool:
        """Vérifie si un objet Blender est toujours valide"""
        if obj is None:
            return False
        try:
            _ = obj.name
            return True
        except ReferenceError:
            return False
    
    def get_primary_circle(self) -> Tuple[Optional[Vector], Optional[bpy.types.Object], Optional[str]]:
        """Retourne les données du cercle principal"""
        if self.is_object_valid(self.primary_object):
            return (self.primary_location, self.primary_object, self.primary_element_type)
        else:
            self.primary_object = None
            return (self.primary_location, None, self.primary_element_type)
    
    def get_secondary_circle(self) -> Tuple[Optional[Vector], Optional[bpy.types.Object], Optional[str]]:
        """Retourne les données du cercle secondaire"""
        if self.is_object_valid(self.secondary_object):
            return (self.secondary_location, self.secondary_object, self.secondary_element_type)
        else:
            self.secondary_object = None
            return (self.secondary_location, None, self.secondary_element_type)


@dataclass
class PlanManagerState:
    """État du module Plan Manager (ex-Projector)"""
    
    # Mode de projection
    is_active: bool = False
    current_projection_data: Optional[Dict[str, Any]] = None
    
    # Sauvegardes
    saved_projections: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    
    # Vue
    locked_view_data: Dict[str, Any] = field(default_factory=dict)
    gizmo_follow_mouse: bool = False
    selected_element_data: Optional[Dict[str, Any]] = None
    
    # Overlays originaux
    original_overlay_settings: Dict[str, Any] = field(default_factory=dict)
    
    # Draw handlers
    draw_handlers: List[Tuple[str, Any]] = field(default_factory=list)
    
    # Position souris
    current_mouse_pos: List[int] = field(default_factory=lambda: [0, 0])
    
    def reset(self):
        """Réinitialise l'état Plan Manager"""
        self.is_active = False
        self.current_projection_data = None
        self.locked_view_data.clear()
        self.gizmo_follow_mouse = False
        self.selected_element_data = None
    
    def get_projection_normal(self) -> Optional[Vector]:
        """Retourne la normale du plan de projection actif"""
        if self.current_projection_data:
            return self.current_projection_data.get('normal')
        return None
    
    def get_projection_center(self) -> Optional[Vector]:
        """Retourne le centre du plan de projection actif"""
        if self.current_projection_data:
            return self.current_projection_data.get('center')
        return None


@dataclass
class RECState:
    """État du module REC (Règle, Équerre, Compas)"""
    
    # Éléments de construction
    construction_lines: List[Any] = field(default_factory=list)
    virtual_vertices: List[Any] = field(default_factory=list)
    construction_circles: List[Any] = field(default_factory=list)
    
    # Système
    draw_handler: Any = None
    unique_element_id: int = 0
    
    # Historique des couleurs
    color_history: Dict[str, List[Tuple[float, float, float, float]]] = field(
        default_factory=lambda: {
            'line': [(1.0, 0.0, 0.0, 1.0), (0.0, 1.0, 0.0, 1.0), (0.0, 0.0, 1.0, 1.0), (1.0, 1.0, 0.0, 1.0)],
            'vertex': [(0.0, 1.0, 0.0, 1.0), (1.0, 0.0, 1.0, 1.0), (0.0, 1.0, 1.0, 1.0), (1.0, 0.5, 0.0, 1.0)],
            'circle': [(0.0, 0.0, 1.0, 1.0), (1.0, 0.0, 0.0, 1.0), (0.0, 1.0, 0.0, 1.0), (1.0, 1.0, 0.0, 1.0)]
        }
    )
    
    def reset(self):
        """Réinitialise l'état REC"""
        self.construction_lines.clear()
        self.virtual_vertices.clear()
        self.construction_circles.clear()
        self.unique_element_id = 0
    
    def get_next_id(self) -> int:
        """Retourne un nouvel ID unique pour un élément"""
        current_id = self.unique_element_id
        self.unique_element_id += 1
        return current_id
    
    def add_color_to_history(self, color_type: str, color: Tuple[float, float, float, float]):
        """Ajoute une couleur à l'historique"""
        if color_type in self.color_history:
            history = self.color_history[color_type]
            # Éviter les doublons consécutifs
            if history and history[0] == color:
                return
            # Insérer en début et limiter à 4
            history.insert(0, color)
            self.color_history[color_type] = history[:4]


@dataclass 
class CutSouderState:
    """État du module Cut/Souder"""
    
    # Objets à traiter
    objects_to_cut: List[bpy.types.Object] = field(default_factory=list)
    objects_to_weld: List[bpy.types.Object] = field(default_factory=list)
    
    # État de l'opération
    is_cutting: bool = False
    is_welding: bool = False
    
    def reset(self):
        """Réinitialise l'état Cut/Souder"""
        self.objects_to_cut.clear()
        self.objects_to_weld.clear()
        self.is_cutting = False
        self.is_welding = False


@dataclass
class VisibilityState:
    """État du module Visibility Manager"""
    
    # Presets de visibilité (stockés aussi dans la scène)
    presets_cache: Dict[str, Dict[str, bool]] = field(default_factory=dict)
    
    def reset(self):
        """Réinitialise l'état Visibility"""
        self.presets_cache.clear()


# ══════════════════════════════════════════════════════════════════════════════
# CLASSE D'ÉTAT GLOBAL
# ══════════════════════════════════════════════════════════════════════════════

class CanopyState:
    """
    État global de CANOPY.
    
    Singleton accessible depuis tous les modules via:
        from canopy.core.state import canopy_state
    """
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        # Initialiser les états de chaque module
        self.snap_circle = SnapCircleState()
        self.plan_manager = PlanManagerState()
        self.rec = RECState()
        self.cut_souder = CutSouderState()
        self.visibility = VisibilityState()
        
        # Métadonnées
        self._initialized = True
        self._version = "2.0.0"
    
    def reset_all(self):
        """Réinitialise tous les états"""
        self.snap_circle.reset()
        self.plan_manager.reset()
        self.rec.reset()
        self.cut_souder.reset()
        self.visibility.reset()
    
    def is_plan_mode_active(self) -> bool:
        """Vérifie si le mode plan est actif (pour REC et autres)"""
        return self.plan_manager.is_active
    
    def get_projection_plane_data(self) -> Optional[Dict[str, Any]]:
        """Récupère les données du plan de projection actif"""
        if self.plan_manager.is_active and self.plan_manager.current_projection_data:
            return {
                'normal': self.plan_manager.get_projection_normal(),
                'center': self.plan_manager.get_projection_center(),
                'type': self.plan_manager.current_projection_data.get('type')
            }
        return None


# ══════════════════════════════════════════════════════════════════════════════
# INSTANCE SINGLETON
# ══════════════════════════════════════════════════════════════════════════════

# Instance globale unique - à importer dans les autres modules
canopy_state = CanopyState()


# ══════════════════════════════════════════════════════════════════════════════
# FONCTIONS UTILITAIRES
# ══════════════════════════════════════════════════════════════════════════════

def get_state() -> CanopyState:
    """
    Retourne l'état global de CANOPY.
    
    Alternative à l'import direct pour compatibilité avec l'ancien code.
    """
    return canopy_state


def redraw_viewport():
    """Force le rafraîchissement de toutes les viewports 3D"""
    for area in bpy.context.screen.areas:
        if area.type == 'VIEW_3D':
            area.tag_redraw()


def get_3d_view_context():
    """Obtient le contexte 3D View actif"""
    for window in bpy.context.window_manager.windows:
        for area in window.screen.areas:
            if area.type == 'VIEW_3D':
                for region in area.regions:
                    if region.type == 'WINDOW':
                        return area, region
    return None, None
