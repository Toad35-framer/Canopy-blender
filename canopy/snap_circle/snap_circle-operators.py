# ══════════════════════════════════════════════════════════════════════════════
# CANOPY V2 - Snap Circle - Opérateurs de Base
# Opérateurs système (démarrer, arrêter, clic, historique)
# ══════════════════════════════════════════════════════════════════════════════

import bpy
from bpy.types import Operator
from bpy_extras import view3d_utils
from mathutils import Vector

# Imports CANOPY
from canopy.core import canopy_state, canopy_events, EventType, redraw_viewport

# Import dynamique des sous-modules (fichiers avec tirets)
import importlib.util
import sys
from pathlib import Path

def _import_sibling(file_name):
    """Importe un fichier frère avec tiret dans le nom"""
    current_dir = Path(__file__).parent
    file_path = current_dir / f"{file_name}.py"
    module_name = f"canopy.snap_circle.{file_name.replace('-', '_')}"
    
    if module_name in sys.modules:
        return sys.modules[module_name]
    
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module

_core = _import_sibling('snap_circle-core')
_renderer = _import_sibling('snap_circle-renderer')

ElementDetector = _core.ElementDetector
HistoryManager = _core.HistoryManager
register_draw_handler = _renderer.register_draw_handler
unregister_draw_handler = _renderer.unregister_draw_handler


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
                # Sauvegarder l'historique si nécessaire
                if state.primary_location:
                    HistoryManager.save_state()
                
                # Déplacer l'ancien cercle principal vers le secondaire
                if state.primary_location:
                    state.secondary_location = state.primary_location
                    state.secondary_object = state.primary_object
                    state.secondary_element_type = state.primary_element_type
                    
                    canopy_events.emit(EventType.SNAP_CIRCLE_SECONDARY_PLACED, {
                        'location': state.secondary_location,
                        'object': state.secondary_object,
                        'element_type': state.secondary_element_type
                    })
                
                # Définir le nouveau cercle principal
                state.primary_location = closest_element
                state.primary_object = hit_object
                state.primary_element_type = element_type
                
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
)
