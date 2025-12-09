# ══════════════════════════════════════════════════════════════════════════════
# CANOPY V2 - Snap Circle - Menus Radiaux (Pie Menus)
# Menus accessibles via raccourcis clavier
# ══════════════════════════════════════════════════════════════════════════════

import bpy
from bpy.types import Menu

# Imports CANOPY
from canopy.core import canopy_state


# ══════════════════════════════════════════════════════════════════════════════
# MENU RADIAL PRINCIPAL
# ══════════════════════════════════════════════════════════════════════════════

class CANOPY_MT_PIE_snap_circle_main(Menu):
    """Menu radial principal de Snap Circle"""
    bl_idname = "CANOPY_MT_PIE_snap_circle_main"
    bl_label = "Snap Circle"
    
    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie()
        state = canopy_state.snap_circle
        
        # 4 - GAUCHE : Système
        pie.operator("wm.call_menu_pie", text="Système", icon='SETTINGS').name = "CANOPY_MT_PIE_snap_circle_system"
        
        # 6 - DROITE : Déplacement
        if state.primary_location:
            pie.operator("wm.call_menu_pie", text="Déplacement", icon='TRANSFORM_MOVE').name = "CANOPY_MT_PIE_snap_circle_move"
        else:
            pie.separator()
        
        # 2 - BAS : Rotation
        if state.primary_location:
            pie.operator("wm.call_menu_pie", text="Rotation", icon='DRIVER_ROTATIONAL_DIFFERENCE').name = "CANOPY_MT_PIE_snap_circle_rotation"
        else:
            pie.separator()
        
        # 8 - HAUT : Utilitaires
        if state.primary_location:
            pie.operator("wm.call_menu_pie", text="Utilitaires", icon='TOOL_SETTINGS').name = "CANOPY_MT_PIE_snap_circle_utilities"
        else:
            pie.separator()
        
        # 7 - HAUT-GAUCHE : Info cercle principal
        if state.primary_location and state.is_object_valid(state.primary_object):
            pie.label(text=f"● {state.primary_object.name}", icon='RADIOBUT_ON')
        else:
            pie.label(text="● Non défini", icon='RADIOBUT_OFF')
        
        # 9 - HAUT-DROITE : Info cercle secondaire
        if state.secondary_location and state.is_object_valid(state.secondary_object):
            pie.label(text=f"○ {state.secondary_object.name}", icon='MESH_CIRCLE')
        else:
            pie.label(text="○ Non défini", icon='MESH_CIRCLE')
        
        # 1 - BAS-GAUCHE : Distance
        if state.primary_location and state.secondary_location:
            distance = (state.primary_location - state.secondary_location).length
            pie.label(text=f"📏 {distance:.3f}", icon='DRIVER_DISTANCE')
        else:
            pie.separator()
        
        # 3 - BAS-DROITE : Reset
        if state.primary_location:
            pie.operator("canopy.snap_circle_reset", text="Reset", icon='FILE_REFRESH')
        else:
            pie.separator()


# ══════════════════════════════════════════════════════════════════════════════
# SOUS-MENU SYSTÈME
# ══════════════════════════════════════════════════════════════════════════════

class CANOPY_MT_PIE_snap_circle_system(Menu):
    """Sous-menu système"""
    bl_idname = "CANOPY_MT_PIE_snap_circle_system"
    bl_label = "Système"
    
    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie()
        state = canopy_state.snap_circle
        
        # 4 - GAUCHE : Démarrer/Arrêter
        if state.is_active:
            pie.operator("canopy.snap_circle_stop", text="Arrêter", icon='PAUSE')
        else:
            pie.operator("canopy.snap_circle_start", text="Démarrer", icon='PLAY')
        
        # 6 - DROITE : Reset
        pie.operator("canopy.snap_circle_reset", text="Reset", icon='FILE_REFRESH')
        
        # 2 - BAS : Historique arrière
        pie.operator("canopy.snap_circle_history_back", text="← Historique", icon='BACK')
        
        # 8 - HAUT : Historique avant
        pie.operator("canopy.snap_circle_history_forward", text="Historique →", icon='FORWARD')


# ══════════════════════════════════════════════════════════════════════════════
# SOUS-MENU DÉPLACEMENT
# ══════════════════════════════════════════════════════════════════════════════

class CANOPY_MT_PIE_snap_circle_move(Menu):
    """Sous-menu déplacement"""
    bl_idname = "CANOPY_MT_PIE_snap_circle_move"
    bl_label = "Déplacement"
    
    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie()
        state = canopy_state.snap_circle
        
        # 4 - GAUCHE : Principal → Secondaire
        if state.primary_location and state.secondary_location:
            pie.operator("canopy.move_primary_to_secondary", text="Principal → Secondaire", icon='FORWARD')
        else:
            pie.separator()
        
        # 6 - DROITE : Secondaire → Principal
        if state.primary_location and state.secondary_location:
            pie.operator("canopy.move_secondary_to_primary", text="Secondaire → Principal", icon='BACK')
        else:
            pie.separator()
        
        # 2 - BAS : Sélection → Principal
        if state.primary_location:
            pie.operator("canopy.snap_selection_to_primary", text="Sélection → Principal", icon='SNAP_ON')
        else:
            pie.separator()
        
        # 8 - HAUT : Inverser positions
        if state.primary_location and state.secondary_location:
            pie.operator("canopy.swap_positions", text="Inverser", icon='FILE_REFRESH')
        else:
            pie.separator()
        
        # 7 - HAUT-GAUCHE : Alignement
        if state.primary_location and len(context.selected_objects) > 1:
            pie.operator("wm.call_menu_pie", text="Alignement", icon='ALIGN_JUSTIFY').name = "CANOPY_MT_PIE_snap_circle_align"
        else:
            pie.separator()
        
        # 9 - HAUT-DROITE : Distribution
        if state.primary_location and len(context.selected_objects) > 1:
            pie.operator("wm.call_menu_pie", text="Distribution", icon='SNAP_GRID').name = "CANOPY_MT_PIE_snap_circle_distribute"
        else:
            pie.separator()
        
        # 1 - BAS-GAUCHE : Déplacer par offset
        if state.primary_location and state.secondary_location:
            pie.operator("canopy.move_by_offset", text="Par Offset", icon='TRANSFORM_MOVE')
        else:
            pie.separator()
        
        # 3 - BAS-DROITE : Vide
        pie.separator()


# ══════════════════════════════════════════════════════════════════════════════
# SOUS-MENU ALIGNEMENT
# ══════════════════════════════════════════════════════════════════════════════

class CANOPY_MT_PIE_snap_circle_align(Menu):
    """Sous-menu alignement"""
    bl_idname = "CANOPY_MT_PIE_snap_circle_align"
    bl_label = "Alignement"
    
    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie()
        
        # 4 - GAUCHE : X
        op = pie.operator("canopy.align_to_axis", text="Aligner X", icon='EVENT_X')
        op.axis = 'X'
        
        # 6 - DROITE : Y
        op = pie.operator("canopy.align_to_axis", text="Aligner Y", icon='EVENT_Y')
        op.axis = 'Y'
        
        # 2 - BAS : Z
        op = pie.operator("canopy.align_to_axis", text="Aligner Z", icon='EVENT_Z')
        op.axis = 'Z'
        
        # 8 - HAUT : Vide
        pie.separator()


# ══════════════════════════════════════════════════════════════════════════════
# SOUS-MENU DISTRIBUTION
# ══════════════════════════════════════════════════════════════════════════════

class CANOPY_MT_PIE_snap_circle_distribute(Menu):
    """Sous-menu distribution"""
    bl_idname = "CANOPY_MT_PIE_snap_circle_distribute"
    bl_label = "Distribution"
    
    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie()
        state = canopy_state.snap_circle
        
        # 4 - GAUCHE : Linéaire
        if state.secondary_location:
            pie.operator("canopy.distribute_linear", text="Linéaire", icon='ALIGN_JUSTIFY')
        else:
            pie.separator()
        
        # 6 - DROITE : Circulaire
        pie.operator("canopy.distribute_circular", text="Circulaire", icon='MESH_CIRCLE')
        
        # 2 - BAS : Grille
        pie.operator("canopy.distribute_grid", text="Grille", icon='MESH_GRID')
        
        # 8 - HAUT : Vide
        pie.separator()


# ══════════════════════════════════════════════════════════════════════════════
# SOUS-MENU ROTATION
# ══════════════════════════════════════════════════════════════════════════════

class CANOPY_MT_PIE_snap_circle_rotation(Menu):
    """Sous-menu rotation"""
    bl_idname = "CANOPY_MT_PIE_snap_circle_rotation"
    bl_label = "Rotation"
    
    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie()
        state = canopy_state.snap_circle
        
        # 4 - GAUCHE : Principal → Secondaire
        if (state.primary_location and state.secondary_location and 
            state.is_object_valid(state.primary_object)):
            pie.operator("canopy.rotate_primary_to_secondary", text="Principal → Secondaire", icon='FORWARD')
        else:
            pie.separator()
        
        # 6 - DROITE : Secondaire → Principal
        if (state.primary_location and state.secondary_location and
            state.is_object_valid(state.secondary_object)):
            pie.operator("canopy.rotate_secondary_to_primary", text="Secondaire → Principal", icon='BACK')
        else:
            pie.separator()
        
        # 2 - BAS : Rotation par angle
        pie.operator("canopy.rotate_by_angle", text="Par Angle", icon='DRIVER_ROTATIONAL_DIFFERENCE')
        
        # 8 - HAUT : Rotation autour cercle
        if state.primary_location or state.secondary_location:
            pie.operator("canopy.rotate_around_circle", text="Autour Cercle", icon='CON_ROTLIKE')
        else:
            pie.separator()
        
        # 7 - HAUT-GAUCHE : Arêtes parallèles
        if (state.primary_element_type == 'EDGE' and state.secondary_element_type == 'EDGE'):
            pie.operator("wm.call_menu_pie", text="Arêtes Parallèles", icon='ARROW_LEFTRIGHT').name = "CANOPY_MT_PIE_snap_circle_parallel"
        else:
            pie.separator()
        
        # 9 - HAUT-DROITE : Orienter
        if context.selected_objects:
            pie.operator("canopy.orient_to_circle", text="Orienter", icon='ORIENTATION_NORMAL')
        else:
            pie.separator()
        
        # 1 - BAS-GAUCHE : Vide
        pie.separator()
        
        # 3 - BAS-DROITE : Vide
        pie.separator()


# ══════════════════════════════════════════════════════════════════════════════
# SOUS-MENU ARÊTES PARALLÈLES
# ══════════════════════════════════════════════════════════════════════════════

class CANOPY_MT_PIE_snap_circle_parallel(Menu):
    """Sous-menu arêtes parallèles"""
    bl_idname = "CANOPY_MT_PIE_snap_circle_parallel"
    bl_label = "Arêtes Parallèles"
    
    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie()
        
        # 4 - GAUCHE : Principal → Parallèle
        pie.operator("canopy.make_edges_parallel_primary", text="Principal → Parallèle", icon='ARROW_LEFTRIGHT')
        
        # 6 - DROITE : Secondaire → Parallèle
        pie.operator("canopy.make_edges_parallel_secondary", text="Secondaire → Parallèle", icon='ARROW_LEFTRIGHT')
        
        # 2 - BAS : Info
        pie.label(text="Cercles sur milieux d'arêtes", icon='EDGESEL')
        
        # 8 - HAUT : Info
        pie.label(text="Rotation sur place", icon='INFO')


# ══════════════════════════════════════════════════════════════════════════════
# SOUS-MENU UTILITAIRES
# ══════════════════════════════════════════════════════════════════════════════

class CANOPY_MT_PIE_snap_circle_utilities(Menu):
    """Sous-menu utilitaires"""
    bl_idname = "CANOPY_MT_PIE_snap_circle_utilities"
    bl_label = "Utilitaires"
    
    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie()
        state = canopy_state.snap_circle
        
        # 4 - GAUCHE : Curseur → Principal
        if state.primary_location:
            pie.operator("canopy.snap_cursor_to_primary", text="Curseur → Principal", icon='PIVOT_CURSOR')
        else:
            pie.separator()
        
        # 6 - DROITE : Origine → Principal
        if state.primary_location:
            pie.operator("canopy.set_origin_to_primary", text="Origine → Principal", icon='OBJECT_ORIGIN')
        else:
            pie.separator()
        
        # 2 - BAS : Curseur → Secondaire
        if state.secondary_location:
            pie.operator("canopy.snap_cursor_to_secondary", text="Curseur → Secondaire", icon='PIVOT_CURSOR')
        else:
            pie.separator()
        
        # 8 - HAUT : Vide
        pie.separator()


# ══════════════════════════════════════════════════════════════════════════════
# LISTE DES CLASSES
# ══════════════════════════════════════════════════════════════════════════════

classes = (
    CANOPY_MT_PIE_snap_circle_main,
    CANOPY_MT_PIE_snap_circle_system,
    CANOPY_MT_PIE_snap_circle_move,
    CANOPY_MT_PIE_snap_circle_align,
    CANOPY_MT_PIE_snap_circle_distribute,
    CANOPY_MT_PIE_snap_circle_rotation,
    CANOPY_MT_PIE_snap_circle_parallel,
    CANOPY_MT_PIE_snap_circle_utilities,
)
