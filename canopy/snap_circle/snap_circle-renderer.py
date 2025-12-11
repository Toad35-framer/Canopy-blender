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
try:
    from canopy.core import canopy_state
except ImportError:
    import sys
    from pathlib import Path
    _CURRENT_DIR = Path(__file__).parent.resolve()
    def _get_parent():
        for name, module in sys.modules.items():
            if hasattr(module, '__file__') and module.__file__:
                if Path(module.__file__).resolve() == _CURRENT_DIR / "__init__.py":
                    return module
        return None
    _parent = _get_parent()
    if _parent:
        canopy_state = _parent.canopy_state
    else:
        class _FallbackState:
            class snap_circle:
                is_active = False
                primary_location = None
                secondary_location = None
                draw_handler = None
                _primary_bounce_scale = 1.0
                _secondary_bounce_scale = 1.0
        canopy_state = _FallbackState()

# Variable globale pour le module d'animations
_animations_module = None

def _get_animations():
    """Récupère le module d'animations (lazy loading)"""
    global _animations_module
    if _animations_module is None:
        import importlib.util
        import sys
        from pathlib import Path
        
        current_dir = Path(__file__).parent.resolve()
        file_path = current_dir / "snap_circle-animations.py"
        
        if file_path.exists():
            try:
                module_name = "canopy_snap_circle_animations_renderer"
                spec = importlib.util.spec_from_file_location(module_name, str(file_path))
                if spec and spec.loader:
                    module = importlib.util.module_from_spec(spec)
                    sys.modules[module_name] = module
                    spec.loader.exec_module(module)
                    _animations_module = module
            except Exception as e:
                print(f"[Snap Circle] Erreur chargement animations: {e}")
                _animations_module = False  # Marquer comme échoué
    
    return _animations_module if _animations_module else None


# ══════════════════════════════════════════════════════════════════════════════
# RENDU DES CERCLES
# ══════════════════════════════════════════════════════════════════════════════

class CircleRenderer:
    """Classe pour le rendu des cercles de référence"""
    
    _shader = None
    
    @classmethod
    def get_shader(cls):
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
        
        if context.area is None or context.area.type != 'VIEW_3D':
            return
        
        region = context.region
        rv3d = context.space_data.region_3d
        
        props = context.scene.snap_circle_props if hasattr(context.scene, 'snap_circle_props') else None
        
        # Récupérer les scales et positions de dessin animées
        primary_scale = getattr(state, '_primary_bounce_scale', 1.0)
        secondary_scale = getattr(state, '_secondary_bounce_scale', 1.0)
        
        # Utiliser les positions animées si disponibles, sinon les positions finales
        primary_draw_pos = getattr(state, '_primary_draw_pos', None) or state.primary_location
        secondary_draw_pos = getattr(state, '_secondary_draw_pos', None) or state.secondary_location
        
        # Dessiner le cercle principal
        if primary_draw_pos and (props is None or props.show_circle):
            color = tuple(props.circle_color) if props else (1.0, 0.2, 0.2, 1.0)
            size = (props.circle_size if props else 20.0) * primary_scale
            
            CircleRenderer._draw_circle_at_location(
                primary_draw_pos, region, rv3d, 
                color, size, solid=True
            )
        
        # Dessiner le cercle secondaire
        if secondary_draw_pos and (props is None or props.show_secondary_circle):
            color = tuple(props.secondary_circle_color) if props else (0.2, 0.5, 1.0, 1.0)
            size = (props.secondary_circle_size if props else 20.0) * secondary_scale
            
            CircleRenderer._draw_circle_at_location(
                secondary_draw_pos, region, rv3d,
                color, size, solid=False
            )
        
        # Dessiner la ligne entre les deux cercles (aux positions de dessin)
        if primary_draw_pos and secondary_draw_pos:
            CircleRenderer._draw_connection_line(
                primary_draw_pos, secondary_draw_pos,
                region, rv3d
            )
        
        # Dessiner les animations (lignes, rotations, etc.)
        anim_module = _get_animations()
        if anim_module and hasattr(anim_module, 'AnimationManager'):
            try:
                anim_module.AnimationManager.get().draw(context)
            except Exception as e:
                pass
    
    @staticmethod
    def _draw_circle_at_location(location, region, rv3d, color, size, solid=True):
        """Dessine un cercle à une position 3D"""
        screen_pos = view3d_utils.location_3d_to_region_2d(region, rv3d, location)
        
        if screen_pos is None:
            return
        
        segments = 32 if solid else 16
        points = []
        
        for i in range(segments):
            angle = 2 * math.pi * i / segments
            x = screen_pos.x + math.cos(angle) * size
            y = screen_pos.y + math.sin(angle) * size
            points.append((x, y))
        
        points.append(points[0])
        
        shader = CircleRenderer.get_shader()
        
        if solid:
            batch = batch_for_shader(shader, 'LINE_STRIP', {"pos": points})
        else:
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
