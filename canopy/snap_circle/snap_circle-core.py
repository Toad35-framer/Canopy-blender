# ══════════════════════════════════════════════════════════════════════════════
# CANOPY V2 - Snap Circle - Core
# Détection d'éléments et fonctions utilitaires de base
# ══════════════════════════════════════════════════════════════════════════════

import bpy
import bmesh
from mathutils import Vector
from bpy_extras import view3d_utils
from typing import Optional, Tuple, List

# Import de l'état global CANOPY
from canopy.core import canopy_state, canopy_events, EventType, redraw_viewport


# ══════════════════════════════════════════════════════════════════════════════
# FONCTIONS UTILITAIRES
# ══════════════════════════════════════════════════════════════════════════════

def get_element_info(element_type: str) -> Tuple[str, str]:
    """Retourne l'icône et le nom pour un type d'élément"""
    mapping = {
        'VERTEX': ('VERTEXSEL', 'Vertex'),
        'EDGE': ('EDGESEL', 'Arête'),
        'FACE': ('FACESEL', 'Face'),
    }
    return mapping.get(element_type, ('DOT', 'Inconnu'))


# ══════════════════════════════════════════════════════════════════════════════
# GESTIONNAIRE D'HISTORIQUE
# ══════════════════════════════════════════════════════════════════════════════

class HistoryManager:
    """Gestionnaire d'historique pour Snap Circle"""
    
    @staticmethod
    def save_state():
        """Sauvegarde l'état actuel dans l'historique"""
        state = canopy_state.snap_circle
        
        if state.primary_location is None:
            return
        
        current = {
            'primary_location': state.primary_location.copy() if state.primary_location else None,
            'primary_object': state.primary_object,
            'primary_element_type': state.primary_element_type,
            'secondary_location': state.secondary_location.copy() if state.secondary_location else None,
            'secondary_object': state.secondary_object,
            'secondary_element_type': state.secondary_element_type
        }
        
        # Supprimer les états futurs si on n'est pas à la fin
        if state.history_index < -1:
            state.history_stack = state.history_stack[:state.history_index + 1]
            state.history_index = -1
        
        state.history_stack.append(current)
        
        # Limiter la taille
        if len(state.history_stack) > state.max_history_size:
            state.history_stack.pop(0)
    
    @staticmethod
    def restore_state(history_state: dict):
        """Restaure un état depuis l'historique"""
        state = canopy_state.snap_circle
        
        state.primary_location = history_state['primary_location'].copy() if history_state['primary_location'] else None
        state.primary_object = history_state['primary_object']
        state.primary_element_type = history_state['primary_element_type']
        state.secondary_location = history_state['secondary_location'].copy() if history_state['secondary_location'] else None
        state.secondary_object = history_state['secondary_object']
        state.secondary_element_type = history_state['secondary_element_type']
        
        redraw_viewport()
    
    @staticmethod
    def can_go_back() -> bool:
        """Vérifie s'il est possible de revenir en arrière"""
        state = canopy_state.snap_circle
        return len(state.history_stack) > 0 and state.history_index > -(len(state.history_stack))
    
    @staticmethod
    def can_go_forward() -> bool:
        """Vérifie s'il est possible d'avancer"""
        state = canopy_state.snap_circle
        return state.history_index < -1
    
    @staticmethod
    def go_back():
        """Revient à l'état précédent"""
        state = canopy_state.snap_circle
        
        if not HistoryManager.can_go_back():
            return False
        
        state.history_index -= 1
        stack_index = len(state.history_stack) + state.history_index
        
        if 0 <= stack_index < len(state.history_stack):
            HistoryManager.restore_state(state.history_stack[stack_index])
            return True
        return False
    
    @staticmethod
    def go_forward():
        """Avance à l'état suivant"""
        state = canopy_state.snap_circle
        
        if not HistoryManager.can_go_forward():
            return False
        
        state.history_index += 1
        
        if state.history_index < -1:
            stack_index = len(state.history_stack) + state.history_index
            if 0 <= stack_index < len(state.history_stack):
                HistoryManager.restore_state(state.history_stack[stack_index])
                return True
        return False


# ══════════════════════════════════════════════════════════════════════════════
# DÉTECTEUR D'ÉLÉMENTS
# ══════════════════════════════════════════════════════════════════════════════

class ElementDetector:
    """Classe pour détecter les éléments de mesh sous la souris"""
    
    @staticmethod
    def find_closest_element(context, event, obj) -> Tuple[Optional[Vector], Optional[str]]:
        """
        Trouve l'élément le plus proche (vertex, edge center, face center).
        
        Returns:
            Tuple (position_world, element_type) ou (None, None)
        """
        if obj is None or obj.type != 'MESH':
            return None, None
        
        # Obtenir les propriétés de détection
        props = context.scene.snap_circle_props if hasattr(context.scene, 'snap_circle_props') else None
        detection_mode = props.detection_mode if props else 'ALL'
        threshold = props.detection_threshold if props else 15.0
        
        mouse_coord = Vector((event.mouse_region_x, event.mouse_region_y))
        
        # Créer un bmesh temporaire
        bm = bmesh.new()
        bm.from_mesh(obj.data)
        bm.transform(obj.matrix_world)
        
        results = []
        
        # Tester les vertices
        if detection_mode in ('ALL', 'VERTEX'):
            result = ElementDetector._test_vertices(bm, context, mouse_coord, threshold)
            if result:
                results.append((*result, 'VERTEX'))
        
        # Tester les edges (milieux)
        if detection_mode in ('ALL', 'EDGE'):
            result = ElementDetector._test_edges(bm, context, mouse_coord, threshold)
            if result:
                results.append((*result, 'EDGE'))
        
        # Tester les faces (centres)
        if detection_mode in ('ALL', 'FACE'):
            result = ElementDetector._test_faces(bm, context, mouse_coord, threshold)
            if result:
                results.append((*result, 'FACE'))
        
        bm.free()
        
        # Retourner l'élément le plus proche
        if results:
            results.sort(key=lambda x: x[1])  # Trier par distance
            return results[0][0], results[0][2]
        
        return None, None
    
    @staticmethod
    def _test_vertices(bm, context, mouse_coord, threshold):
        """Teste les vertices"""
        closest = None
        min_dist = float('inf')
        
        for vert in bm.verts:
            screen_pos = view3d_utils.location_3d_to_region_2d(
                context.region, context.space_data.region_3d, vert.co
            )
            
            if screen_pos:
                dist = (mouse_coord - screen_pos).length
                if dist < threshold and dist < min_dist:
                    min_dist = dist
                    closest = vert.co.copy()
        
        return (closest, min_dist) if closest else None
    
    @staticmethod
    def _test_edges(bm, context, mouse_coord, threshold):
        """Teste les milieux d'arêtes"""
        closest = None
        min_dist = float('inf')
        
        for edge in bm.edges:
            edge_center = (edge.verts[0].co + edge.verts[1].co) / 2
            screen_pos = view3d_utils.location_3d_to_region_2d(
                context.region, context.space_data.region_3d, edge_center
            )
            
            if screen_pos:
                dist = (mouse_coord - screen_pos).length
                if dist < threshold and dist < min_dist:
                    min_dist = dist
                    closest = edge_center.copy()
        
        return (closest, min_dist) if closest else None
    
    @staticmethod
    def _test_faces(bm, context, mouse_coord, threshold):
        """Teste les centres de faces"""
        closest = None
        min_dist = float('inf')
        
        for face in bm.faces:
            face_center = face.calc_center_median()
            screen_pos = view3d_utils.location_3d_to_region_2d(
                context.region, context.space_data.region_3d, face_center
            )
            
            if screen_pos:
                dist = (mouse_coord - screen_pos).length
                if dist < threshold and dist < min_dist:
                    min_dist = dist
                    closest = face_center.copy()
        
        return (closest, min_dist) if closest else None


# ══════════════════════════════════════════════════════════════════════════════
# FONCTIONS DE CALCUL
# ══════════════════════════════════════════════════════════════════════════════

def get_edge_direction_from_position(pos: Vector, obj: bpy.types.Object) -> Vector:
    """
    Calcule la direction d'une arête à partir d'une position (milieu d'arête).
    
    Args:
        pos: Position du cercle (milieu d'arête)
        obj: Objet contenant l'arête
    
    Returns:
        Vector direction de l'arête (normalisé)
    """
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    bm.normal_update()
    
    obj_matrix = obj.matrix_world
    closest_edge = None
    min_distance = float('inf')
    
    # Trouver l'arête la plus proche
    for edge in bm.edges:
        edge_center = (edge.verts[0].co + edge.verts[1].co) / 2
        world_pos = obj_matrix @ edge_center
        
        distance = (world_pos - pos).length
        if distance < min_distance:
            min_distance = distance
            closest_edge = edge
    
    if closest_edge:
        vert1_world = obj_matrix @ closest_edge.verts[0].co
        vert2_world = obj_matrix @ closest_edge.verts[1].co
        edge_direction = (vert2_world - vert1_world).normalized()
    else:
        edge_direction = Vector((1, 0, 0))
    
    bm.free()
    return edge_direction
