# ══════════════════════════════════════════════════════════════════════════════
# CANOPY V2 - Snap Circle - Renderer
# Rendu GPU des cercles de référence
# ══════════════════════════════════════════════════════════════════════════════

import bpy
import gpu
import math
from gpu_extras.batch import batch_for_shader
from bpy_extras import view3d_utils
from mathutils import Vector

# Import de l'état global CANOPY
from canopy.core import canopy_state


# ══════════════════════════════════════════════════════════════════════════════
# RENDU DES CERCLES
# ══════════════════════════════════════════════════════════════════════════════

class CircleRenderer:
    """Classe pour le rendu des cercles de référence"""
    
    # Shader partagé
    _shader = None
    
    @classmethod
    def get_shader(cls):
        """Retourne le shader (créé une seule fois)"""
        if cls._shader is None:
            cls._shader = gpu.shader.from_builtin('UNIFORM_COLOR')
        return cls._shader
    
    @staticmethod
    def draw_circles():
        """Fonction de dessin appelée par le draw handler"""
        context = bpy.context
        state = canopy_state.snap_circle
        
        if not state.is_active:
            return
        
        # Vérifier qu'on est dans une vue 3D
        if context.area is None or context.area.type != 'VIEW_3D':
            return
        
        region = context.region
        rv3d = context.space_data.region_3d
        
        # Obtenir les propriétés
        props = context.scene.snap_circle_props if hasattr(context.scene, 'snap_circle_props') else None
        
        # Dessiner le cercle principal
        if state.primary_location and (props is None or props.show_circle):
            color = tuple(props.circle_color) if props else (1.0, 0.2, 0.2, 1.0)
            size = props.circle_size if props else 20.0
            
            CircleRenderer._draw_circle_at_location(
                state.primary_location, region, rv3d, 
                color, size, solid=True
            )
        
        # Dessiner le cercle secondaire
        if state.secondary_location and (props is None or props.show_secondary_circle):
            color = tuple(props.secondary_circle_color) if props else (0.2, 0.5, 1.0, 1.0)
            size = props.secondary_circle_size if props else 20.0
            
            CircleRenderer._draw_circle_at_location(
                state.secondary_location, region, rv3d,
                color, size, solid=False  # Discontinu
            )
        
        # Dessiner la ligne entre les deux cercles
        if state.primary_location and state.secondary_location:
            CircleRenderer._draw_connection_line(
                state.primary_location, state.secondary_location,
                region, rv3d
            )
    
    @staticmethod
    def _draw_circle_at_location(location, region, rv3d, color, size, solid=True):
        """Dessine un cercle à une position 3D"""
        # Convertir en coordonnées écran
        screen_pos = view3d_utils.location_3d_to_region_2d(region, rv3d, location)
        
        if screen_pos is None:
            return
        
        # Générer les points du cercle
        segments = 32 if solid else 16
        points = []
        
        for i in range(segments):
            angle = 2 * math.pi * i / segments
            x = screen_pos.x + math.cos(angle) * size
            y = screen_pos.y + math.sin(angle) * size
            points.append((x, y))
        
        # Fermer le cercle
        points.append(points[0])
        
        # Dessiner
        shader = CircleRenderer.get_shader()
        
        if solid:
            # Cercle continu
            batch = batch_for_shader(shader, 'LINE_STRIP', {"pos": points})
        else:
            # Cercle discontinu (pointillé)
            dashed_points = []
            for i in range(0, len(points) - 1, 2):
                dashed_points.append(points[i])
                dashed_points.append(points[i + 1] if i + 1 < len(points) else points[0])
            batch = batch_for_shader(shader, 'LINES', {"pos": dashed_points})
        
        gpu.state.blend_set('ALPHA')
        gpu.state.line_width_set(2.0)
        
        shader.bind()
        shader.uniform_float("color", color)
        batch.draw(shader)
        
        gpu.state.blend_set('NONE')
        gpu.state.line_width_set(1.0)
    
    @staticmethod
    def _draw_connection_line(pos1, pos2, region, rv3d):
        """Dessine une ligne pointillée entre deux positions"""
        screen1 = view3d_utils.location_3d_to_region_2d(region, rv3d, pos1)
        screen2 = view3d_utils.location_3d_to_region_2d(region, rv3d, pos2)
        
        if screen1 is None or screen2 is None:
            return
        
        # Générer une ligne pointillée
        direction = screen2 - screen1
        length = direction.length
        
        if length < 1:
            return
        
        direction.normalize()
        
        dash_length = 8
        gap_length = 4
        
        points = []
        current_pos = 0
        
        while current_pos < length:
            start = screen1 + direction * current_pos
            end_pos = min(current_pos + dash_length, length)
            end = screen1 + direction * end_pos
            
            points.append((start.x, start.y))
            points.append((end.x, end.y))
            
            current_pos += dash_length + gap_length
        
        if len(points) < 2:
            return
        
        # Dessiner
        shader = CircleRenderer.get_shader()
        batch = batch_for_shader(shader, 'LINES', {"pos": points})
        
        gpu.state.blend_set('ALPHA')
        gpu.state.line_width_set(1.0)
        
        shader.bind()
        shader.uniform_float("color", (0.5, 0.5, 0.5, 0.5))
        batch.draw(shader)
        
        gpu.state.blend_set('NONE')


# ══════════════════════════════════════════════════════════════════════════════
# GESTION DU DRAW HANDLER
# ══════════════════════════════════════════════════════════════════════════════

def register_draw_handler():
    """Enregistre le gestionnaire de dessin"""
    state = canopy_state.snap_circle
    
    if state.draw_handler is None:
        state.draw_handler = bpy.types.SpaceView3D.draw_handler_add(
            CircleRenderer.draw_circles, (), 'WINDOW', 'POST_PIXEL'
        )
        state.is_active = True
        return True
    return False


def unregister_draw_handler():
    """Supprime le gestionnaire de dessin"""
    state = canopy_state.snap_circle
    
    if state.draw_handler is not None:
        try:
            bpy.types.SpaceView3D.draw_handler_remove(state.draw_handler, 'WINDOW')
        except:
            pass
        state.draw_handler = None
        state.is_active = False
        return True
    return False
