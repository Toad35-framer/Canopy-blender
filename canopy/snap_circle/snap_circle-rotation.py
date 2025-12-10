# ══════════════════════════════════════════════════════════════════════════════
# CANOPY V2 - Snap Circle - Rotation
# Opérateurs de rotation et d'orientation
# ══════════════════════════════════════════════════════════════════════════════

import bpy
import math
from bpy.types import Operator
from bpy.props import EnumProperty, FloatProperty
from mathutils import Vector, Matrix

# Imports CANOPY
from canopy.core import canopy_state, redraw_viewport

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
get_edge_direction_from_position = _core.get_edge_direction_from_position


# ══════════════════════════════════════════════════════════════════════════════
# FONCTIONS UTILITAIRES
# ══════════════════════════════════════════════════════════════════════════════

def calculate_angle_between_points(pivot, point1, point2):
    """Calcule l'angle entre deux points par rapport à un pivot"""
    vec1 = (point1 - pivot).normalized()
    vec2 = (point2 - pivot).normalized()
    
    dot = max(-1.0, min(1.0, vec1.dot(vec2)))
    angle = math.acos(dot)
    
    # Déterminer le signe (sens horaire/anti-horaire)
    cross = vec1.cross(vec2)
    if cross.z < 0:
        angle = -angle
    
    return angle


def check_rotation_validity(pivot, point1, point2, min_distance=0.01):
    """Vérifie si une rotation est valide"""
    dist_pivot_p1 = (point1 - pivot).length
    dist_pivot_p2 = (point2 - pivot).length
    
    if dist_pivot_p1 < min_distance:
        return False, "Cercle principal trop proche du pivot"
    if dist_pivot_p2 < min_distance:
        return False, "Cercle secondaire trop proche du pivot"
    
    return True, "OK"


def rotate_object_around_point(obj, pivot, axis, angle):
    """Fait tourner un objet autour d'un point"""
    rotation_matrix = Matrix.Rotation(angle, 4, axis)
    to_pivot = Matrix.Translation(-pivot)
    from_pivot = Matrix.Translation(pivot)
    
    transform = from_pivot @ rotation_matrix @ to_pivot
    obj.matrix_world = transform @ obj.matrix_world


# ══════════════════════════════════════════════════════════════════════════════
# OPÉRATEURS DE ROTATION
# ══════════════════════════════════════════════════════════════════════════════

class CANOPY_OT_rotate_primary_to_secondary(Operator):
    """Rotation de l'objet principal vers le secondaire autour du curseur"""
    bl_idname = "canopy.rotate_primary_to_secondary"
    bl_label = "Rotation Principal → Secondaire"
    bl_description = "Fait tourner l'objet du cercle principal vers le secondaire autour du curseur 3D"
    bl_options = {'REGISTER', 'UNDO'}
    
    @classmethod
    def poll(cls, context):
        state = canopy_state.snap_circle
        if not (state.primary_location and state.secondary_location):
            return False
        if not state.is_object_valid(state.primary_object):
            return False
        
        cursor_pos = context.scene.cursor.location
        valid, _ = check_rotation_validity(cursor_pos, state.primary_location, state.secondary_location)
        return valid
    
    def execute(self, context):
        state = canopy_state.snap_circle
        cursor_pos = context.scene.cursor.location
        
        # Calculer l'angle
        angle = calculate_angle_between_points(
            cursor_pos, state.primary_location, state.secondary_location
        )
        
        # Calculer l'axe de rotation (perpendiculaire au plan formé)
        vec1 = (state.primary_location - cursor_pos).normalized()
        vec2 = (state.secondary_location - cursor_pos).normalized()
        axis = vec1.cross(vec2)
        
        if axis.length < 0.001:
            axis = Vector((0, 0, 1))
        else:
            axis.normalize()
        
        # Appliquer la rotation
        rotate_object_around_point(state.primary_object, cursor_pos, axis, angle)
        
        # Mettre à jour la position du cercle
        state.primary_location = state.secondary_location.copy()
        redraw_viewport()
        
        self.report({'INFO'}, f"Rotation de {math.degrees(angle):.1f}°")
        return {'FINISHED'}


class CANOPY_OT_rotate_secondary_to_primary(Operator):
    """Rotation de l'objet secondaire vers le principal autour du curseur"""
    bl_idname = "canopy.rotate_secondary_to_primary"
    bl_label = "Rotation Secondaire → Principal"
    bl_description = "Fait tourner l'objet du cercle secondaire vers le principal autour du curseur 3D"
    bl_options = {'REGISTER', 'UNDO'}
    
    @classmethod
    def poll(cls, context):
        state = canopy_state.snap_circle
        if not (state.primary_location and state.secondary_location):
            return False
        if not state.is_object_valid(state.secondary_object):
            return False
        
        cursor_pos = context.scene.cursor.location
        valid, _ = check_rotation_validity(cursor_pos, state.secondary_location, state.primary_location)
        return valid
    
    def execute(self, context):
        state = canopy_state.snap_circle
        cursor_pos = context.scene.cursor.location
        
        angle = calculate_angle_between_points(
            cursor_pos, state.secondary_location, state.primary_location
        )
        
        vec1 = (state.secondary_location - cursor_pos).normalized()
        vec2 = (state.primary_location - cursor_pos).normalized()
        axis = vec1.cross(vec2)
        
        if axis.length < 0.001:
            axis = Vector((0, 0, 1))
        else:
            axis.normalize()
        
        rotate_object_around_point(state.secondary_object, cursor_pos, axis, angle)
        
        state.secondary_location = state.primary_location.copy()
        redraw_viewport()
        
        self.report({'INFO'}, f"Rotation de {math.degrees(angle):.1f}°")
        return {'FINISHED'}


class CANOPY_OT_rotate_by_angle(Operator):
    """Rotation par angle défini"""
    bl_idname = "canopy.rotate_by_angle"
    bl_label = "Rotation par Angle"
    bl_description = "Fait tourner la sélection d'un angle défini autour du cercle principal"
    bl_options = {'REGISTER', 'UNDO'}
    
    angle: FloatProperty(
        name="Angle (degrés)",
        default=90.0,
        min=-360.0,
        max=360.0
    )
    
    axis: EnumProperty(
        name="Axe",
        items=[
            ('X', "X", "Rotation autour de X"),
            ('Y', "Y", "Rotation autour de Y"),
            ('Z', "Z", "Rotation autour de Z"),
        ],
        default='Z'
    )
    
    @classmethod
    def poll(cls, context):
        state = canopy_state.snap_circle
        return state.primary_location is not None and context.selected_objects
    
    def execute(self, context):
        state = canopy_state.snap_circle
        pivot = state.primary_location
        
        axis_vectors = {
            'X': Vector((1, 0, 0)),
            'Y': Vector((0, 1, 0)),
            'Z': Vector((0, 0, 1)),
        }
        axis = axis_vectors[self.axis]
        angle_rad = math.radians(self.angle)
        
        rotated = 0
        for obj in context.selected_objects:
            if obj.type == 'MESH':
                rotate_object_around_point(obj, pivot, axis, angle_rad)
                rotated += 1
        
        self.report({'INFO'}, f"{rotated} objet(s) tourné(s) de {self.angle}°")
        return {'FINISHED'}
    
    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)


class CANOPY_OT_rotate_around_circle(Operator):
    """Rotation autour d'un cercle"""
    bl_idname = "canopy.rotate_around_circle"
    bl_label = "Rotation autour du Cercle"
    bl_description = "Fait tourner la sélection autour du cercle choisi"
    bl_options = {'REGISTER', 'UNDO'}
    
    circle_type: EnumProperty(
        name="Cercle",
        items=[
            ('PRIMARY', "Principal", "Autour du cercle principal"),
            ('SECONDARY', "Secondaire", "Autour du cercle secondaire"),
        ],
        default='PRIMARY'
    )
    
    angle: FloatProperty(
        name="Angle (degrés)",
        default=90.0,
        min=-360.0,
        max=360.0
    )
    
    @classmethod
    def poll(cls, context):
        state = canopy_state.snap_circle
        return (state.primary_location is not None or 
                state.secondary_location is not None) and context.selected_objects
    
    def execute(self, context):
        state = canopy_state.snap_circle
        
        if self.circle_type == 'PRIMARY':
            pivot = state.primary_location
        else:
            pivot = state.secondary_location
        
        if pivot is None:
            self.report({'WARNING'}, f"Cercle {self.circle_type.lower()} non défini")
            return {'CANCELLED'}
        
        axis = Vector((0, 0, 1))
        angle_rad = math.radians(self.angle)
        
        rotated = 0
        for obj in context.selected_objects:
            if obj.type == 'MESH':
                rotate_object_around_point(obj, pivot, axis, angle_rad)
                rotated += 1
        
        self.report({'INFO'}, f"{rotated} objet(s) tourné(s)")
        return {'FINISHED'}
    
    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)


# ══════════════════════════════════════════════════════════════════════════════
# OPÉRATEURS D'ARÊTES PARALLÈLES
# ══════════════════════════════════════════════════════════════════════════════

class CANOPY_OT_make_edges_parallel_primary(Operator):
    """Rend l'arête de l'objet principal parallèle à celle du secondaire"""
    bl_idname = "canopy.make_edges_parallel_primary"
    bl_label = "Principal → Parallèle"
    bl_description = "Fait tourner l'objet principal pour que son arête soit parallèle à celle du secondaire"
    bl_options = {'REGISTER', 'UNDO'}
    
    @classmethod
    def poll(cls, context):
        state = canopy_state.snap_circle
        return (state.primary_location is not None and 
                state.secondary_location is not None and
                state.is_object_valid(state.primary_object) and
                state.is_object_valid(state.secondary_object) and
                state.primary_element_type == 'EDGE' and
                state.secondary_element_type == 'EDGE')
    
    def execute(self, context):
        state = canopy_state.snap_circle
        
        # Obtenir les directions des arêtes
        edge1_dir = get_edge_direction_from_position(state.primary_location, state.primary_object)
        edge2_dir = get_edge_direction_from_position(state.secondary_location, state.secondary_object)
        
        # Calculer l'axe et l'angle de rotation
        rotation_axis = edge1_dir.cross(edge2_dir)
        
        if rotation_axis.length < 0.001:
            if edge1_dir.dot(edge2_dir) > 0:
                self.report({'INFO'}, "Arêtes déjà parallèles")
                return {'FINISHED'}
            else:
                # Rotation de 180°
                if abs(edge1_dir.x) < 0.9:
                    rotation_axis = Vector((1, 0, 0)).cross(edge1_dir)
                else:
                    rotation_axis = Vector((0, 1, 0)).cross(edge1_dir)
                angle = math.pi
        else:
            rotation_axis.normalize()
            dot = max(-1.0, min(1.0, edge1_dir.dot(edge2_dir)))
            angle = math.acos(dot)
        
        # Appliquer la rotation autour du centre de l'objet
        pivot = state.primary_object.location
        rotate_object_around_point(state.primary_object, pivot, rotation_axis, angle)
        
        self.report({'INFO'}, f"Arête alignée (rotation {math.degrees(angle):.1f}°)")
        return {'FINISHED'}


class CANOPY_OT_make_edges_parallel_secondary(Operator):
    """Rend l'arête de l'objet secondaire parallèle à celle du principal"""
    bl_idname = "canopy.make_edges_parallel_secondary"
    bl_label = "Secondaire → Parallèle"
    bl_description = "Fait tourner l'objet secondaire pour que son arête soit parallèle à celle du principal"
    bl_options = {'REGISTER', 'UNDO'}
    
    @classmethod
    def poll(cls, context):
        state = canopy_state.snap_circle
        return (state.primary_location is not None and 
                state.secondary_location is not None and
                state.is_object_valid(state.primary_object) and
                state.is_object_valid(state.secondary_object) and
                state.primary_element_type == 'EDGE' and
                state.secondary_element_type == 'EDGE')
    
    def execute(self, context):
        state = canopy_state.snap_circle
        
        edge1_dir = get_edge_direction_from_position(state.secondary_location, state.secondary_object)
        edge2_dir = get_edge_direction_from_position(state.primary_location, state.primary_object)
        
        rotation_axis = edge1_dir.cross(edge2_dir)
        
        if rotation_axis.length < 0.001:
            if edge1_dir.dot(edge2_dir) > 0:
                self.report({'INFO'}, "Arêtes déjà parallèles")
                return {'FINISHED'}
            else:
                if abs(edge1_dir.x) < 0.9:
                    rotation_axis = Vector((1, 0, 0)).cross(edge1_dir)
                else:
                    rotation_axis = Vector((0, 1, 0)).cross(edge1_dir)
                angle = math.pi
        else:
            rotation_axis.normalize()
            dot = max(-1.0, min(1.0, edge1_dir.dot(edge2_dir)))
            angle = math.acos(dot)
        
        pivot = state.secondary_object.location
        rotate_object_around_point(state.secondary_object, pivot, rotation_axis, angle)
        
        self.report({'INFO'}, f"Arête alignée (rotation {math.degrees(angle):.1f}°)")
        return {'FINISHED'}


class CANOPY_OT_orient_to_circle(Operator):
    """Oriente la sélection vers le cercle principal"""
    bl_idname = "canopy.orient_to_circle"
    bl_label = "Orienter vers Cercle"
    bl_description = "Oriente les objets sélectionnés pour pointer vers le cercle principal"
    bl_options = {'REGISTER', 'UNDO'}
    
    @classmethod
    def poll(cls, context):
        state = canopy_state.snap_circle
        return state.primary_location is not None and context.selected_objects
    
    def execute(self, context):
        state = canopy_state.snap_circle
        target = state.primary_location
        
        oriented = 0
        for obj in context.selected_objects:
            if obj.type == 'MESH':
                direction = (target - obj.location).normalized()
                
                # Calculer la rotation pour pointer vers la cible
                up = Vector((0, 0, 1))
                if abs(direction.z) > 0.99:
                    up = Vector((0, 1, 0))
                
                right = direction.cross(up).normalized()
                up = right.cross(direction).normalized()
                
                rotation_matrix = Matrix((
                    right,
                    direction,
                    up
                )).transposed().to_4x4()
                
                obj.matrix_world = Matrix.Translation(obj.location) @ rotation_matrix
                oriented += 1
        
        self.report({'INFO'}, f"{oriented} objet(s) orienté(s)")
        return {'FINISHED'}


# ══════════════════════════════════════════════════════════════════════════════
# LISTE DES CLASSES
# ══════════════════════════════════════════════════════════════════════════════

classes = (
    CANOPY_OT_rotate_primary_to_secondary,
    CANOPY_OT_rotate_secondary_to_primary,
    CANOPY_OT_rotate_by_angle,
    CANOPY_OT_rotate_around_circle,
    CANOPY_OT_make_edges_parallel_primary,
    CANOPY_OT_make_edges_parallel_secondary,
    CANOPY_OT_orient_to_circle,
)
