# ══════════════════════════════════════════════════════════════════════════════
# CANOPY V2 - Snap Circle - UI Panel
# Panneau principal dans le sidebar
# ══════════════════════════════════════════════════════════════════════════════

import bpy
from bpy.types import Panel

# Imports CANOPY
from canopy.core import canopy_state

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
get_element_info = _core.get_element_info
HistoryManager = _core.HistoryManager


# ══════════════════════════════════════════════════════════════════════════════
# PANNEAU PRINCIPAL
# ══════════════════════════════════════════════════════════════════════════════

class CANOPY_PT_snap_circle_main(Panel):
    """Panneau principal de Snap Circle"""
    bl_label = "Snap Circle"
    bl_idname = "CANOPY_PT_snap_circle_main"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "CANOPY"
    
    def draw(self, context):
        layout = self.layout
        state = canopy_state.snap_circle
        
        # Vérifier les propriétés
        if not hasattr(context.scene, 'snap_circle_props'):
            layout.label(text="❌ Redémarrez Blender!", icon='ERROR')
            return
        
        props = context.scene.snap_circle_props
        
        # ══════════════════════════════════════════════════════════════════════
        # État du système
        # ══════════════════════════════════════════════════════════════════════
        box = layout.box()
        
        if not state.is_active:
            box.operator("canopy.snap_circle_start", text="🔴 DÉMARRER", icon='PLAY')
            box.label(text="Système inactif", icon='RADIOBUT_OFF')
        else:
            box.operator("canopy.snap_circle_stop", text="🟢 ARRÊTER", icon='PAUSE')
            box.label(text="Système actif", icon='CHECKMARK')
            box.operator("canopy.snap_circle_reset", text="Reset", icon='FILE_REFRESH')
        
        if not state.is_active:
            layout.label(text="Démarrez le système pour utiliser Snap Circle")
            return
        
        # ══════════════════════════════════════════════════════════════════════
        # Instructions
        # ══════════════════════════════════════════════════════════════════════
        box = layout.box()
        box.label(text="UTILISATION:", icon='INFO')
        box.label(text="• Clic gauche: placer cercle")
        box.label(text="• Ctrl+Shift+S: menu radial")
        
        # ══════════════════════════════════════════════════════════════════════
        # Mode de détection
        # ══════════════════════════════════════════════════════════════════════
        box = layout.box()
        box.label(text="DÉTECTION:", icon='ZOOM_SELECTED')
        box.prop(props, "detection_mode", text="")
        box.prop(props, "detection_threshold")
        
        # ══════════════════════════════════════════════════════════════════════
        # Informations sur les cercles
        # ══════════════════════════════════════════════════════════════════════
        self._draw_circle_info(layout, "PRINCIPAL", True)
        self._draw_circle_info(layout, "SECONDAIRE", False)
        
        # ══════════════════════════════════════════════════════════════════════
        # Distance entre cercles
        # ══════════════════════════════════════════════════════════════════════
        if state.primary_location and state.secondary_location:
            self._draw_distance_info(layout)
        
        # ══════════════════════════════════════════════════════════════════════
        # Historique
        # ══════════════════════════════════════════════════════════════════════
        self._draw_history_controls(layout)
        
        # ══════════════════════════════════════════════════════════════════════
        # Paramètres visuels
        # ══════════════════════════════════════════════════════════════════════
        box = layout.box()
        box.label(text="APPARENCE:", icon='RESTRICT_VIEW_OFF')
        
        # Cercle principal
        row = box.row()
        row.prop(props, "show_circle", text="Principal")
        if props.show_circle:
            row = box.row(align=True)
            row.prop(props, "circle_size", text="Taille")
            row.prop(props, "circle_color", text="")
        
        # Cercle secondaire
        row = box.row()
        row.prop(props, "show_secondary_circle", text="Secondaire")
        if props.show_secondary_circle:
            row = box.row(align=True)
            row.prop(props, "secondary_circle_size", text="Taille")
            row.prop(props, "secondary_circle_color", text="")
    
    def _draw_circle_info(self, layout, name, is_primary):
        """Affiche les informations d'un cercle"""
        state = canopy_state.snap_circle
        box = layout.box()
        
        if is_primary:
            location = state.primary_location
            obj = state.primary_object
            element_type = state.primary_element_type
            icon_type = 'RADIOBUT_ON'
        else:
            location = state.secondary_location
            obj = state.secondary_object
            element_type = state.secondary_element_type
            icon_type = 'MESH_CIRCLE'
        
        if location:
            icon, element_name = get_element_info(element_type)
            box.label(text=f"CERCLE {name}:", icon=icon)
            
            if state.is_object_valid(obj):
                box.label(text=f"  📦 Objet: {obj.name}")
            else:
                box.label(text="  ⚠️ Objet: [Supprimé]")
            
            box.label(text=f"  📍 Position:")
            col = box.column(align=True)
            col.label(text=f"    X: {location.x:.3f}")
            col.label(text=f"    Y: {location.y:.3f}")
            col.label(text=f"    Z: {location.z:.3f}")
        else:
            box.label(text=f"Aucun cercle {name.lower()}", icon=icon_type)
    
    def _draw_distance_info(self, layout):
        """Affiche la distance entre les cercles"""
        state = canopy_state.snap_circle
        box = layout.box()
        
        distance = (state.primary_location - state.secondary_location).length
        diff = state.primary_location - state.secondary_location
        
        box.label(text="DISTANCE:", icon='DRIVER_DISTANCE')
        box.label(text=f"  📏 Total: {distance:.3f}")
        
        col = box.column(align=True)
        col.label(text=f"  ΔX: {abs(diff.x):.3f}")
        col.label(text=f"  ΔY: {abs(diff.y):.3f}")
        col.label(text=f"  ΔZ: {abs(diff.z):.3f}")
    
    def _draw_history_controls(self, layout):
        """Affiche les contrôles d'historique"""
        state = canopy_state.snap_circle
        box = layout.box()
        box.label(text="HISTORIQUE:", icon='RECOVER_LAST')
        
        row = box.row(align=True)
        
        sub = row.row(align=True)
        sub.enabled = HistoryManager.can_go_back()
        sub.operator("canopy.snap_circle_history_back", text="", icon='BACK')
        
        sub = row.row(align=True)
        sub.enabled = HistoryManager.can_go_forward()
        sub.operator("canopy.snap_circle_history_forward", text="", icon='FORWARD')
        
        if state.history_stack:
            row.label(text=f"{len(state.history_stack)} états")


# ══════════════════════════════════════════════════════════════════════════════
# SOUS-PANNEAU DÉPLACEMENT
# ══════════════════════════════════════════════════════════════════════════════

class CANOPY_PT_snap_circle_movement(Panel):
    """Panneau des outils de déplacement"""
    bl_label = "Déplacement"
    bl_idname = "CANOPY_PT_snap_circle_movement"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "CANOPY"
    bl_parent_id = "CANOPY_PT_snap_circle_main"
    bl_options = {'DEFAULT_CLOSED'}
    
    @classmethod
    def poll(cls, context):
        return canopy_state.snap_circle.is_active
    
    def draw(self, context):
        layout = self.layout
        state = canopy_state.snap_circle
        
        # Déplacement direct
        if state.primary_location and state.secondary_location:
            box = layout.box()
            box.label(text="DÉPLACEMENT DIRECT:", icon='TRANSFORM_MOVE')
            col = box.column(align=True)
            col.operator("canopy.move_primary_to_secondary")
            col.operator("canopy.move_secondary_to_primary")
            col.operator("canopy.swap_positions")
        
        # Sélection
        if state.primary_location:
            box = layout.box()
            box.label(text="SÉLECTION:", icon='RESTRICT_SELECT_OFF')
            box.operator("canopy.snap_selection_to_primary")
            
            if state.secondary_location:
                box.operator("canopy.move_by_offset")
        
        # Alignement
        if state.primary_location and len(context.selected_objects) > 1:
            box = layout.box()
            box.label(text="ALIGNEMENT:", icon='ALIGN_JUSTIFY')
            
            row = box.row(align=True)
            op = row.operator("canopy.align_to_axis", text="X")
            op.axis = 'X'
            op = row.operator("canopy.align_to_axis", text="Y")
            op.axis = 'Y'
            op = row.operator("canopy.align_to_axis", text="Z")
            op.axis = 'Z'
        
        # Distribution
        if state.primary_location and len(context.selected_objects) > 1:
            box = layout.box()
            box.label(text="DISTRIBUTION:", icon='SNAP_GRID')
            col = box.column(align=True)
            
            if state.secondary_location:
                col.operator("canopy.distribute_linear")
            
            col.operator("canopy.distribute_circular")
            col.operator("canopy.distribute_grid")


# ══════════════════════════════════════════════════════════════════════════════
# SOUS-PANNEAU ROTATION
# ══════════════════════════════════════════════════════════════════════════════

class CANOPY_PT_snap_circle_rotation(Panel):
    """Panneau des outils de rotation"""
    bl_label = "Rotation"
    bl_idname = "CANOPY_PT_snap_circle_rotation"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "CANOPY"
    bl_parent_id = "CANOPY_PT_snap_circle_main"
    bl_options = {'DEFAULT_CLOSED'}
    
    @classmethod
    def poll(cls, context):
        return canopy_state.snap_circle.is_active
    
    def draw(self, context):
        layout = self.layout
        state = canopy_state.snap_circle
        
        # Rotations principales
        if state.primary_location and state.secondary_location:
            box = layout.box()
            box.label(text="SECTEUR ANGULAIRE:", icon='DRIVER_ROTATIONAL_DIFFERENCE')
            
            col = box.column(align=True)
            if state.is_object_valid(state.primary_object):
                col.operator("canopy.rotate_primary_to_secondary")
            if state.is_object_valid(state.secondary_object):
                col.operator("canopy.rotate_secondary_to_primary")
        
        # Arêtes parallèles
        if (state.primary_location and state.secondary_location and
            state.is_object_valid(state.primary_object) and
            state.is_object_valid(state.secondary_object) and
            state.primary_element_type == 'EDGE' and
            state.secondary_element_type == 'EDGE'):
            
            box = layout.box()
            box.label(text="ARÊTES PARALLÈLES:", icon='ARROW_LEFTRIGHT')
            col = box.column(align=True)
            col.operator("canopy.make_edges_parallel_primary")
            col.operator("canopy.make_edges_parallel_secondary")
        
        # Rotation libre
        box = layout.box()
        box.label(text="ROTATION LIBRE:", icon='CON_ROTLIKE')
        box.operator("canopy.rotate_by_angle")
        
        if state.primary_location or state.secondary_location:
            box.operator("canopy.rotate_around_circle")
        
        # Orientation
        if context.selected_objects:
            box = layout.box()
            box.label(text="ORIENTATION:", icon='ORIENTATION_NORMAL')
            box.operator("canopy.orient_to_circle")


# ══════════════════════════════════════════════════════════════════════════════
# SOUS-PANNEAU UTILITAIRES
# ══════════════════════════════════════════════════════════════════════════════

class CANOPY_PT_snap_circle_utilities(Panel):
    """Panneau des utilitaires"""
    bl_label = "Utilitaires"
    bl_idname = "CANOPY_PT_snap_circle_utilities"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "CANOPY"
    bl_parent_id = "CANOPY_PT_snap_circle_main"
    bl_options = {'DEFAULT_CLOSED'}
    
    @classmethod
    def poll(cls, context):
        return canopy_state.snap_circle.is_active
    
    def draw(self, context):
        layout = self.layout
        state = canopy_state.snap_circle
        
        box = layout.box()
        box.label(text="CURSEUR:", icon='PIVOT_CURSOR')
        
        col = box.column(align=True)
        col.enabled = state.primary_location is not None
        col.operator("canopy.snap_cursor_to_primary")
        
        col = box.column(align=True)
        col.enabled = state.secondary_location is not None
        col.operator("canopy.snap_cursor_to_secondary")
        
        box = layout.box()
        box.label(text="ORIGINE:", icon='OBJECT_ORIGIN')
        col = box.column(align=True)
        col.enabled = state.primary_location is not None and bool(context.selected_objects)
        col.operator("canopy.set_origin_to_primary")


# ══════════════════════════════════════════════════════════════════════════════
# LISTE DES CLASSES
# ══════════════════════════════════════════════════════════════════════════════

classes = (
    CANOPY_PT_snap_circle_main,
    CANOPY_PT_snap_circle_movement,
    CANOPY_PT_snap_circle_rotation,
    CANOPY_PT_snap_circle_utilities,
)
