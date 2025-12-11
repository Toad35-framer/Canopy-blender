# ══════════════════════════════════════════════════════════════════════════════
# CANOPY V2 - Snap Circle - Opérateurs de Base
# Opérateurs système (démarrer, arrêter, clic, historique)
# ══════════════════════════════════════════════════════════════════════════════

import bpy
from bpy.types import Operator
from bpy_extras import view3d_utils
from mathutils import Vector

# Imports CANOPY avec fallback
try:
    from canopy.core import canopy_state, canopy_events, EventType, redraw_viewport
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
        canopy_events = _parent.canopy_events
        EventType = _parent.EventType
        redraw_viewport = _parent.redraw_viewport
    else:
        raise ImportError("Impossible de trouver le module parent")

# Import dynamique des sous-modules (fichiers avec tirets)
import importlib.util
import sys
from pathlib import Path

_CURRENT_DIR = Path(__file__).parent.resolve()

def _import_sibling(file_name):
    """Importe un fichier frère avec tiret dans le nom"""
    safe_name = file_name.replace('-', '_')
    full_module_name = f"canopy_snap_circle_{safe_name}_operators"
    
    file_path = _CURRENT_DIR / f"{file_name}.py"
    
    if not file_path.exists():
        return None
    
    try:
        spec = importlib.util.spec_from_file_location(full_module_name, str(file_path))
        if spec is None or spec.loader is None:
            return None
        
        module = importlib.util.module_from_spec(spec)
        sys.modules[full_module_name] = module
        spec.loader.exec_module(module)
        return module
    except Exception as e:
        print(f"[Snap Circle] Erreur import {file_name}: {e}")
        return None

_core = _import_sibling('snap_circle-core')
_renderer = _import_sibling('snap_circle-renderer')
_animations = _import_sibling('snap_circle-animations')

if _core:
    ElementDetector = _core.ElementDetector
    HistoryManager = _core.HistoryManager
else:
    ElementDetector = None
    HistoryManager = None

if _renderer:
    register_draw_handler = _renderer.register_draw_handler
    unregister_draw_handler = _renderer.unregister_draw_handler
else:
    register_draw_handler = lambda: False
    unregister_draw_handler = lambda: False


# ══════════════════════════════════════════════════════════════════════════════
# OPÉRATEURS SYSTÈME
# ══════════════════════════════════════════════════════════════════════════════

class CANOPY_OT_snap_circle_start(Operator):
    """Démarre le système de cercle de référence"""
    bl_idname = "canopy.snap_circle_start"
    bl_label = "Démarrer Snap Circle"
    bl_description = "Active le système de cercle de référence"
    
    def execute(self, context):
        if register_draw_handler():
            canopy_events.emit(EventType.SNAP_CIRCLE_STARTED)
            
            # Démarrer le moniteur de survol pour les animations
            if _animations and hasattr(_animations, 'start_hover_monitor'):
                _animations.start_hover_monitor()
            
            self.report({'INFO'}, "Snap Circle activé - Cliquez sur les éléments pour placer les cercles")
        else:
            self.report({'WARNING'}, "Système déjà actif")
        
        redraw_viewport()
        return {'FINISHED'}


class CANOPY_OT_snap_circle_stop(Operator):
    """Arrête le système de cercle de référence"""
    bl_idname = "canopy.snap_circle_stop"
    bl_label = "Arrêter Snap Circle"
    bl_description = "Désactive le système de cercle de référence"
    
    def execute(self, context):
        # Arrêter les animations et le moniteur de survol
        if _animations:
            if hasattr(_animations, 'stop_hover_monitor'):
                _animations.stop_hover_monitor()
            if hasattr(_animations, 'AnimationManager'):
                _animations.AnimationManager.get().clear()
        
        unregister_draw_handler()
        canopy_state.snap_circle.reset()
        canopy_events.emit(EventType.SNAP_CIRCLE_STOPPED)
        redraw_viewport()
        
        self.report({'INFO'}, "Snap Circle arrêté")
        return {'FINISHED'}


class CANOPY_OT_snap_circle_reset(Operator):
    """Reset le système"""
    bl_idname = "canopy.snap_circle_reset"
    bl_label = "Reset Snap Circle"
    bl_description = "Remet à zéro tous les cercles"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        canopy_state.snap_circle.reset()
        canopy_events.emit(EventType.SNAP_CIRCLE_RESET)
        redraw_viewport()
        
        self.report({'INFO'}, "Cercles remis à zéro")
        return {'FINISHED'}


class CANOPY_OT_snap_circle_click(Operator):
    """Gestionnaire de clic pour placer les cercles"""
    bl_idname = "canopy.snap_circle_click"
    bl_label = "Snap Circle Click"
    bl_description = "Gère les clics pour placer les cercles de référence"
    
    def execute(self, context):
        return {'FINISHED'}
    
    def invoke(self, context, event):
        state = canopy_state.snap_circle
        
        if not state.is_active:
            return {'PASS_THROUGH'}
        
        # Vérifier que le clic est dans la viewport
        if not (0 <= event.mouse_region_x <= context.region.width and
                0 <= event.mouse_region_y <= context.region.height):
            return {'PASS_THROUGH'}
        
        # Raycast pour trouver l'objet cliqué
        hit_object = self._perform_raycast(context, event)
        
        if hit_object and hit_object.type == 'MESH':
            # Trouver l'élément le plus proche
            closest_element, element_type = ElementDetector.find_closest_element(
                context, event, hit_object
            )
            
            if closest_element and element_type:
                # Sauvegarder les anciennes positions AVANT modification
                old_primary_location = state.primary_location.copy() if state.primary_location else None
                old_secondary_location = state.secondary_location.copy() if state.secondary_location else None
                
                # Sauvegarder l'historique si nécessaire
                if state.primary_location:
                    HistoryManager.save_state()
                
                # ══════════════════════════════════════════════════════════════
                # CAS 1: Premier clic - Aucun cercle n'existe
                # → Rebond sur le nouveau cercle principal
                # ══════════════════════════════════════════════════════════════
                if old_primary_location is None:
                    # Définir le cercle principal
                    state.primary_location = closest_element
                    state.primary_object = hit_object
                    state.primary_element_type = element_type
                    
                    # Animation rebond pour la première apparition
                    if _animations and hasattr(_animations, 'create_bounce'):
                        try:
                            _animations.create_bounce(is_primary=True)
                        except:
                            pass
                    
                    canopy_events.emit(EventType.SNAP_CIRCLE_PRIMARY_PLACED, {
                        'location': state.primary_location,
                        'object': state.primary_object,
                        'element_type': state.primary_element_type
                    })
                
                # ══════════════════════════════════════════════════════════════
                # CAS 2: Deuxième clic - Principal existe, pas de secondaire
                # → Déplacement du principal + Rebond du secondaire (apparition)
                # ══════════════════════════════════════════════════════════════
                elif old_secondary_location is None:
                    # Le secondaire prend l'ancienne position du principal
                    state.secondary_location = old_primary_location
                    state.secondary_object = state.primary_object
                    state.secondary_element_type = state.primary_element_type
                    
                    # Le principal va à la nouvelle position
                    state.primary_location = closest_element
                    state.primary_object = hit_object
                    state.primary_element_type = element_type
                    
                    # Animations
                    if _animations:
                        try:
                            # Déplacement du principal vers sa nouvelle position
                            if hasattr(_animations, 'create_move_animation'):
                                _animations.create_move_animation(
                                    start=old_primary_location,
                                    end=closest_element,
                                    is_primary=True
                                )
                            
                            # Rebond du secondaire (première apparition)
                            if hasattr(_animations, 'create_bounce'):
                                _animations.create_bounce(is_primary=False)
                        except:
                            pass
                    
                    canopy_events.emit(EventType.SNAP_CIRCLE_SECONDARY_PLACED, {
                        'location': state.secondary_location,
                        'object': state.secondary_object,
                        'element_type': state.secondary_element_type
                    })
                    canopy_events.emit(EventType.SNAP_CIRCLE_PRIMARY_PLACED, {
                        'location': state.primary_location,
                        'object': state.primary_object,
                        'element_type': state.primary_element_type
                    })
                
                # ══════════════════════════════════════════════════════════════
                # CAS 3: Troisième clic+ - Les deux cercles existent
                # → Déplacement des deux avec évitement si croisement
                # ══════════════════════════════════════════════════════════════
                else:
                    # Le secondaire prend l'ancienne position du principal
                    state.secondary_location = old_primary_location
                    state.secondary_object = state.primary_object
                    state.secondary_element_type = state.primary_element_type
                    
                    # Le principal va à la nouvelle position
                    state.primary_location = closest_element
                    state.primary_object = hit_object
                    state.primary_element_type = element_type
                    
                    # Animations de déplacement avec évitement
                    if _animations:
                        try:
                            if hasattr(_animations, 'create_move_animation'):
                                # Déplacement du principal
                                _animations.create_move_animation(
                                    start=old_primary_location,
                                    end=closest_element,
                                    is_primary=True,
                                    other_start=old_secondary_location,
                                    other_end=old_primary_location
                                )
                                
                                # Déplacement du secondaire (avec léger délai)
                                _animations.create_move_animation(
                                    start=old_secondary_location,
                                    end=old_primary_location,
                                    is_primary=False,
                                    other_start=old_primary_location,
                                    other_end=closest_element,
                                    delay=0.03  # Petit décalage
                                )
                        except:
                            pass
                    
                    canopy_events.emit(EventType.SNAP_CIRCLE_SECONDARY_PLACED, {
                        'location': state.secondary_location,
                        'object': state.secondary_object,
                        'element_type': state.secondary_element_type
                    })
                    canopy_events.emit(EventType.SNAP_CIRCLE_PRIMARY_PLACED, {
                        'location': state.primary_location,
                        'object': state.primary_object,
                        'element_type': state.primary_element_type
                    })
                
                redraw_viewport()
                return {'FINISHED'}
        
        return {'PASS_THROUGH'}
    
    def _perform_raycast(self, context, event):
        """Effectue un raycast pour détecter l'objet sous la souris"""
        try:
            mouse_coord = (event.mouse_region_x, event.mouse_region_y)
            
            ray_origin = view3d_utils.region_2d_to_origin_3d(
                context.region, context.space_data.region_3d, mouse_coord
            )
            ray_direction = view3d_utils.region_2d_to_vector_3d(
                context.region, context.space_data.region_3d, mouse_coord
            )
            
            depsgraph = context.evaluated_depsgraph_get()
            hit, _, _, _, hit_object, _ = context.scene.ray_cast(
                depsgraph, ray_origin, ray_direction
            )
            
            return hit_object if hit else None
            
        except Exception:
            return None


# ══════════════════════════════════════════════════════════════════════════════
# OPÉRATEURS HISTORIQUE
# ══════════════════════════════════════════════════════════════════════════════

class CANOPY_OT_snap_circle_history_back(Operator):
    """Revient en arrière dans l'historique"""
    bl_idname = "canopy.snap_circle_history_back"
    bl_label = "Historique Arrière"
    bl_description = "Revient à la position précédente des cercles"
    bl_options = {'REGISTER', 'UNDO'}
    
    @classmethod
    def poll(cls, context):
        return HistoryManager.can_go_back()
    
    def execute(self, context):
        if HistoryManager.go_back():
            state = canopy_state.snap_circle
            self.report({'INFO'}, f"Retour historique ({-state.history_index}/{len(state.history_stack)})")
            return {'FINISHED'}
        
        self.report({'WARNING'}, "Aucun état précédent")
        return {'CANCELLED'}


class CANOPY_OT_snap_circle_history_forward(Operator):
    """Avance dans l'historique"""
    bl_idname = "canopy.snap_circle_history_forward"
    bl_label = "Historique Avant"
    bl_description = "Avance à la position suivante des cercles"
    bl_options = {'REGISTER', 'UNDO'}
    
    @classmethod
    def poll(cls, context):
        return HistoryManager.can_go_forward()
    
    def execute(self, context):
        if HistoryManager.go_forward():
            state = canopy_state.snap_circle
            self.report({'INFO'}, f"Avance historique ({-state.history_index}/{len(state.history_stack)})")
            return {'FINISHED'}
        
        self.report({'WARNING'}, "Aucun état suivant")
        return {'CANCELLED'}


# ══════════════════════════════════════════════════════════════════════════════
# OPÉRATEURS UTILITAIRES
# ══════════════════════════════════════════════════════════════════════════════

class CANOPY_OT_snap_cursor_to_primary(Operator):
    """Place le curseur 3D sur le cercle principal"""
    bl_idname = "canopy.snap_cursor_to_primary"
    bl_label = "Curseur → Cercle Principal"
    bl_description = "Place le curseur 3D sur le cercle de référence principal"
    bl_options = {'REGISTER', 'UNDO'}
    
    @classmethod
    def poll(cls, context):
        return canopy_state.snap_circle.primary_location is not None
    
    def execute(self, context):
        context.scene.cursor.location = canopy_state.snap_circle.primary_location
        self.report({'INFO'}, "Curseur placé sur le cercle principal")
        return {'FINISHED'}


class CANOPY_OT_snap_cursor_to_secondary(Operator):
    """Place le curseur 3D sur le cercle secondaire"""
    bl_idname = "canopy.snap_cursor_to_secondary"
    bl_label = "Curseur → Cercle Secondaire"
    bl_description = "Place le curseur 3D sur le cercle de référence secondaire"
    bl_options = {'REGISTER', 'UNDO'}
    
    @classmethod
    def poll(cls, context):
        return canopy_state.snap_circle.secondary_location is not None
    
    def execute(self, context):
        context.scene.cursor.location = canopy_state.snap_circle.secondary_location
        self.report({'INFO'}, "Curseur placé sur le cercle secondaire")
        return {'FINISHED'}


class CANOPY_OT_set_origin_to_primary(Operator):
    """Définit l'origine sur le cercle principal"""
    bl_idname = "canopy.set_origin_to_primary"
    bl_label = "Origine → Cercle Principal"
    bl_description = "Définit l'origine des objets sélectionnés sur le cercle principal"
    bl_options = {'REGISTER', 'UNDO'}
    
    @classmethod
    def poll(cls, context):
        return (canopy_state.snap_circle.primary_location is not None and 
                context.selected_objects)
    
    def execute(self, context):
        state = canopy_state.snap_circle
        selected_meshes = [obj for obj in context.selected_objects if obj.type == 'MESH']
        
        if not selected_meshes:
            self.report({'WARNING'}, "Aucun mesh sélectionné")
            return {'CANCELLED'}
        
        # Sauvegarder le mode et le curseur
        original_mode = context.mode
        original_cursor = context.scene.cursor.location.copy()
        
        if context.mode != 'OBJECT':
            bpy.ops.object.mode_set(mode='OBJECT')
        
        # Placer le curseur et définir l'origine
        context.scene.cursor.location = state.primary_location
        
        for obj in selected_meshes:
            bpy.ops.object.select_all(action='DESELECT')
            obj.select_set(True)
            context.view_layer.objects.active = obj
            bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
        
        # Restaurer
        context.scene.cursor.location = original_cursor
        for obj in selected_meshes:
            obj.select_set(True)
        
        if original_mode == 'EDIT_MESH':
            bpy.ops.object.mode_set(mode='EDIT')
        
        self.report({'INFO'}, f"Origine définie pour {len(selected_meshes)} objet(s)")
        return {'FINISHED'}


# ══════════════════════════════════════════════════════════════════════════════
# OPÉRATEURS DE PRÉVISUALISATION (boutons "?")
# ══════════════════════════════════════════════════════════════════════════════

class CANOPY_OT_preview_move_p_to_s(Operator):
    """Prévisualise le déplacement Principal → Secondaire"""
    bl_idname = "canopy.preview_move_p_to_s"
    bl_label = ""
    bl_description = "Voir l'animation: déplace l'objet du cercle principal vers le secondaire"
    bl_options = {'INTERNAL'}
    
    @classmethod
    def poll(cls, context):
        state = canopy_state.snap_circle
        return (state.is_active and 
                state.primary_location is not None and 
                state.secondary_location is not None)
    
    def execute(self, context):
        if _animations:
            state = canopy_state.snap_circle
            if hasattr(_animations, 'preview_line'):
                _animations.preview_line(
                    state.primary_location, 
                    state.secondary_location, 
                    erase_from_start=True
                )
        return {'FINISHED'}


class CANOPY_OT_preview_move_s_to_p(Operator):
    """Prévisualise le déplacement Secondaire → Principal"""
    bl_idname = "canopy.preview_move_s_to_p"
    bl_label = ""
    bl_description = "Voir l'animation: déplace l'objet du cercle secondaire vers le principal"
    bl_options = {'INTERNAL'}
    
    @classmethod
    def poll(cls, context):
        state = canopy_state.snap_circle
        return (state.is_active and 
                state.primary_location is not None and 
                state.secondary_location is not None)
    
    def execute(self, context):
        if _animations:
            state = canopy_state.snap_circle
            if hasattr(_animations, 'preview_line'):
                _animations.preview_line(
                    state.secondary_location, 
                    state.primary_location, 
                    erase_from_start=True
                )
        return {'FINISHED'}


class CANOPY_OT_preview_rotate_p_to_s(Operator):
    """Prévisualise la rotation Principal → Secondaire"""
    bl_idname = "canopy.preview_rotate_p_to_s"
    bl_label = ""
    bl_description = "Voir l'animation: rotation autour du cercle principal vers le secondaire"
    bl_options = {'INTERNAL'}
    
    @classmethod
    def poll(cls, context):
        state = canopy_state.snap_circle
        return (state.is_active and 
                state.primary_location is not None and 
                state.secondary_location is not None)
    
    def execute(self, context):
        if _animations:
            state = canopy_state.snap_circle
            if hasattr(_animations, 'preview_rotation'):
                import math
                from mathutils import Vector
                
                pivot = state.primary_location
                start = state.secondary_location
                
                # Rotation simulée de 60°
                direction = start - pivot
                angle = math.radians(60)
                cos_a, sin_a = math.cos(angle), math.sin(angle)
                rotated = Vector((
                    direction.x * cos_a - direction.y * sin_a,
                    direction.x * sin_a + direction.y * cos_a,
                    direction.z
                ))
                target = pivot + rotated
                
                _animations.preview_rotation(pivot, start, target)
        return {'FINISHED'}


class CANOPY_OT_preview_rotate_s_to_p(Operator):
    """Prévisualise la rotation Secondaire → Principal"""
    bl_idname = "canopy.preview_rotate_s_to_p"
    bl_label = ""
    bl_description = "Voir l'animation: rotation autour du cercle secondaire vers le principal"
    bl_options = {'INTERNAL'}
    
    @classmethod
    def poll(cls, context):
        state = canopy_state.snap_circle
        return (state.is_active and 
                state.primary_location is not None and 
                state.secondary_location is not None)
    
    def execute(self, context):
        if _animations:
            state = canopy_state.snap_circle
            if hasattr(_animations, 'preview_rotation'):
                import math
                from mathutils import Vector
                
                pivot = state.secondary_location
                start = state.primary_location
                
                direction = start - pivot
                angle = math.radians(60)
                cos_a, sin_a = math.cos(angle), math.sin(angle)
                rotated = Vector((
                    direction.x * cos_a - direction.y * sin_a,
                    direction.x * sin_a + direction.y * cos_a,
                    direction.z
                ))
                target = pivot + rotated
                
                _animations.preview_rotation(pivot, start, target)
        return {'FINISHED'}


class CANOPY_OT_preview_parallel_p(Operator):
    """Prévisualise l'alignement parallèle vers Principal"""
    bl_idname = "canopy.preview_parallel_p"
    bl_label = ""
    bl_description = "Voir l'animation: aligne l'arête secondaire parallèlement à la principale"
    bl_options = {'INTERNAL'}
    
    @classmethod
    def poll(cls, context):
        state = canopy_state.snap_circle
        return (state.is_active and 
                state.primary_location is not None and 
                state.secondary_location is not None and
                state.primary_element_type == 'EDGE' and
                state.secondary_element_type == 'EDGE')
    
    def execute(self, context):
        if _animations:
            state = canopy_state.snap_circle
            if hasattr(_animations, 'preview_edge_rotation'):
                from mathutils import Vector
                
                target_dir = (state.primary_location - state.secondary_location).normalized()
                start_dir = Vector((-target_dir.y, target_dir.x, 0))
                if start_dir.length < 0.001:
                    start_dir = Vector((1, 0, 0))
                start_dir.normalize()
                
                _animations.preview_edge_rotation(
                    state.secondary_location, 
                    start_dir, 
                    target_dir, 
                    1.5
                )
        return {'FINISHED'}


class CANOPY_OT_preview_parallel_s(Operator):
    """Prévisualise l'alignement parallèle vers Secondaire"""
    bl_idname = "canopy.preview_parallel_s"
    bl_label = ""
    bl_description = "Voir l'animation: aligne l'arête principale parallèlement à la secondaire"
    bl_options = {'INTERNAL'}
    
    @classmethod
    def poll(cls, context):
        state = canopy_state.snap_circle
        return (state.is_active and 
                state.primary_location is not None and 
                state.secondary_location is not None and
                state.primary_element_type == 'EDGE' and
                state.secondary_element_type == 'EDGE')
    
    def execute(self, context):
        if _animations:
            state = canopy_state.snap_circle
            if hasattr(_animations, 'preview_edge_rotation'):
                from mathutils import Vector
                
                target_dir = (state.secondary_location - state.primary_location).normalized()
                start_dir = Vector((-target_dir.y, target_dir.x, 0))
                if start_dir.length < 0.001:
                    start_dir = Vector((1, 0, 0))
                start_dir.normalize()
                
                _animations.preview_edge_rotation(
                    state.primary_location, 
                    start_dir, 
                    target_dir, 
                    1.5
                )
        return {'FINISHED'}


# ══════════════════════════════════════════════════════════════════════════════
# LISTE DES CLASSES
# ══════════════════════════════════════════════════════════════════════════════

classes = (
    CANOPY_OT_snap_circle_start,
    CANOPY_OT_snap_circle_stop,
    CANOPY_OT_snap_circle_reset,
    CANOPY_OT_snap_circle_click,
    CANOPY_OT_snap_circle_history_back,
    CANOPY_OT_snap_circle_history_forward,
    CANOPY_OT_snap_cursor_to_primary,
    CANOPY_OT_snap_cursor_to_secondary,
    CANOPY_OT_set_origin_to_primary,
    # Opérateurs de prévisualisation
    CANOPY_OT_preview_move_p_to_s,
    CANOPY_OT_preview_move_s_to_p,
    CANOPY_OT_preview_rotate_p_to_s,
    CANOPY_OT_preview_rotate_s_to_p,
    CANOPY_OT_preview_parallel_p,
    CANOPY_OT_preview_parallel_s,
)
