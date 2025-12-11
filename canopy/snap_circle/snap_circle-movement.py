# ══════════════════════════════════════════════════════════════════════════════
# CANOPY V2 - Snap Circle - Movement
# Opérateurs de déplacement et d'alignement
# ══════════════════════════════════════════════════════════════════════════════

import bpy
import math
from bpy.types import Operator
from bpy.props import EnumProperty, IntProperty, FloatProperty
from mathutils import Vector

# Imports CANOPY avec fallback
try:
    from canopy.core import canopy_state, redraw_viewport
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
        redraw_viewport = _parent.redraw_viewport
    else:
        raise ImportError("Impossible de trouver le module parent")

# Import dynamique pour les animations
import importlib.util
import sys
from pathlib import Path

_CURRENT_DIR = Path(__file__).parent.resolve()

def _import_sibling(file_name):
    """Importe un fichier frère avec tiret dans le nom"""
    safe_name = file_name.replace('-', '_')
    full_module_name = f"canopy_snap_circle_{safe_name}_movement"
    
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

# Import optionnel des animations
_animations = _import_sibling('snap_circle-animations')


# ══════════════════════════════════════════════════════════════════════════════
# OPÉRATEURS DE DÉPLACEMENT
# ══════════════════════════════════════════════════════════════════════════════

class CANOPY_OT_move_primary_to_secondary(Operator):
    """Déplace l'objet du cercle principal vers le cercle secondaire"""
    bl_idname = "canopy.move_primary_to_secondary"
    bl_label = "Déplacer Principal → Secondaire"
    bl_description = "Déplace l'objet du cercle principal vers la position du cercle secondaire"
    bl_options = {'REGISTER', 'UNDO'}
    
    @classmethod
    def poll(cls, context):
        state = canopy_state.snap_circle
        return (state.primary_location is not None and 
                state.secondary_location is not None and
                state.is_object_valid(state.primary_object))
    
    def execute(self, context):
        state = canopy_state.snap_circle
        offset = state.secondary_location - state.primary_location
        state.primary_object.location += offset
        
        # Mettre à jour la position du cercle
        state.primary_location = state.secondary_location.copy()
        redraw_viewport()
        
        self.report({'INFO'}, f"'{state.primary_object.name}' déplacé vers le cercle secondaire")
        return {'FINISHED'}


class CANOPY_OT_move_secondary_to_primary(Operator):
    """Déplace l'objet du cercle secondaire vers le cercle principal"""
    bl_idname = "canopy.move_secondary_to_primary"
    bl_label = "Déplacer Secondaire → Principal"
    bl_description = "Déplace l'objet du cercle secondaire vers la position du cercle principal"
    bl_options = {'REGISTER', 'UNDO'}
    
    @classmethod
    def poll(cls, context):
        state = canopy_state.snap_circle
        return (state.primary_location is not None and 
                state.secondary_location is not None and
                state.is_object_valid(state.secondary_object))
    
    def execute(self, context):
        state = canopy_state.snap_circle
        offset = state.primary_location - state.secondary_location
        state.secondary_object.location += offset
        
        state.secondary_location = state.primary_location.copy()
        redraw_viewport()
        
        self.report({'INFO'}, f"'{state.secondary_object.name}' déplacé vers le cercle principal")
        return {'FINISHED'}


class CANOPY_OT_snap_selection_to_primary(Operator):
    """Déplace la sélection sur le cercle principal"""
    bl_idname = "canopy.snap_selection_to_primary"
    bl_label = "Sélection → Cercle Principal"
    bl_description = "Déplace le centre de gravité de la sélection sur le cercle principal"
    bl_options = {'REGISTER', 'UNDO'}
    
    @classmethod
    def poll(cls, context):
        state = canopy_state.snap_circle
        return state.primary_location is not None and context.selected_objects
    
    def execute(self, context):
        state = canopy_state.snap_circle
        selected_meshes = [obj for obj in context.selected_objects if obj.type == 'MESH']
        
        if not selected_meshes:
            self.report({'WARNING'}, "Aucun mesh sélectionné")
            return {'CANCELLED'}
        
        # Calculer le centre de gravité
        center = Vector((0, 0, 0))
        for obj in selected_meshes:
            center += obj.location
        center /= len(selected_meshes)
        
        # Calculer et appliquer le déplacement
        offset = state.primary_location - center
        for obj in selected_meshes:
            obj.location += offset
        
        self.report({'INFO'}, f"{len(selected_meshes)} objet(s) déplacé(s)")
        return {'FINISHED'}


class CANOPY_OT_swap_positions(Operator):
    """Inverse les positions des objets par rapport aux cercles"""
    bl_idname = "canopy.swap_positions"
    bl_label = "Inverser Positions"
    bl_description = "Inverse les objets : celui du cercle principal va au cercle secondaire et vice-versa"
    bl_options = {'REGISTER', 'UNDO'}
    
    @classmethod
    def poll(cls, context):
        state = canopy_state.snap_circle
        return (state.primary_location is not None and 
                state.secondary_location is not None and
                state.is_object_valid(state.primary_object) and
                state.is_object_valid(state.secondary_object))
    
    def execute(self, context):
        state = canopy_state.snap_circle
        
        # Animation de swap avec évitement
        if _animations:
            try:
                _animations.create_swap_animations(
                    state.primary_location.copy(),
                    state.secondary_location.copy()
                )
            except:
                pass
        
        # Calculer les offsets
        offset_primary = state.primary_object.location - state.primary_location
        offset_secondary = state.secondary_object.location - state.secondary_location
        
        # Appliquer aux cercles opposés
        new_primary_location = state.secondary_location + offset_primary
        new_secondary_location = state.primary_location + offset_secondary
        
        state.primary_object.location = new_primary_location
        state.secondary_object.location = new_secondary_location
        
        # Échanger les références
        state.primary_object, state.secondary_object = state.secondary_object, state.primary_object
        state.primary_element_type, state.secondary_element_type = state.secondary_element_type, state.primary_element_type
        
        redraw_viewport()
        
        self.report({'INFO'}, "Objets inversés")
        return {'FINISHED'}


class CANOPY_OT_move_by_offset(Operator):
    """Déplace la sélection par l'offset entre les cercles"""
    bl_idname = "canopy.move_by_offset"
    bl_label = "Déplacer par Offset"
    bl_description = "Déplace la sélection de la distance et direction entre les deux cercles"
    bl_options = {'REGISTER', 'UNDO'}
    
    @classmethod
    def poll(cls, context):
        state = canopy_state.snap_circle
        return (state.primary_location is not None and 
                state.secondary_location is not None and
                context.selected_objects)
    
    def execute(self, context):
        state = canopy_state.snap_circle
        offset = state.secondary_location - state.primary_location
        
        moved = 0
        for obj in context.selected_objects:
            if obj.type == 'MESH':
                obj.location += offset
                moved += 1
        
        self.report({'INFO'}, f"{moved} objet(s) déplacé(s) de {offset.length:.3f}")
        return {'FINISHED'}


# ══════════════════════════════════════════════════════════════════════════════
# OPÉRATEURS D'ALIGNEMENT
# ══════════════════════════════════════════════════════════════════════════════

class CANOPY_OT_align_to_axis(Operator):
    """Aligne les objets sur un axe"""
    bl_idname = "canopy.align_to_axis"
    bl_label = "Aligner sur Axe"
    bl_description = "Aligne les objets sélectionnés sur l'axe spécifié passant par le cercle principal"
    bl_options = {'REGISTER', 'UNDO'}
    
    axis: EnumProperty(
        name="Axe",
        items=[
            ('X', "X", "Aligner sur l'axe X"),
            ('Y', "Y", "Aligner sur l'axe Y"),
            ('Z', "Z", "Aligner sur l'axe Z"),
        ],
        default='X'
    )
    
    @classmethod
    def poll(cls, context):
        state = canopy_state.snap_circle
        return state.primary_location is not None and len(context.selected_objects) > 1
    
    def execute(self, context):
        state = canopy_state.snap_circle
        reference_value = getattr(state.primary_location, self.axis.lower())
        
        aligned = 0
        for obj in context.selected_objects:
            if obj.type == 'MESH':
                setattr(obj.location, self.axis.lower(), reference_value)
                aligned += 1
        
        self.report({'INFO'}, f"{aligned} objet(s) aligné(s) sur {self.axis}")
        return {'FINISHED'}


# ══════════════════════════════════════════════════════════════════════════════
# OPÉRATEURS DE DISTRIBUTION
# ══════════════════════════════════════════════════════════════════════════════

class CANOPY_OT_distribute_linear(Operator):
    """Distribue les objets linéairement entre les deux cercles"""
    bl_idname = "canopy.distribute_linear"
    bl_label = "Distribution Linéaire"
    bl_description = "Distribue les objets sélectionnés linéairement entre les deux cercles"
    bl_options = {'REGISTER', 'UNDO'}
    
    @classmethod
    def poll(cls, context):
        state = canopy_state.snap_circle
        return (state.primary_location is not None and 
                state.secondary_location is not None and
                len(context.selected_objects) > 1)
    
    def execute(self, context):
        state = canopy_state.snap_circle
        selected = [obj for obj in context.selected_objects if obj.type == 'MESH']
        
        if len(selected) < 2:
            self.report({'WARNING'}, "Au moins 2 meshes requis")
            return {'CANCELLED'}
        
        # Trier par distance au cercle principal
        selected.sort(key=lambda obj: (obj.location - state.primary_location).length)
        
        # Calculer les positions
        direction = state.secondary_location - state.primary_location
        step = direction / (len(selected) - 1) if len(selected) > 1 else Vector((0, 0, 0))
        
        for i, obj in enumerate(selected):
            obj.location = state.primary_location + step * i
        
        self.report({'INFO'}, f"{len(selected)} objets distribués")
        return {'FINISHED'}


class CANOPY_OT_distribute_circular(Operator):
    """Distribue les objets en cercle autour du cercle principal"""
    bl_idname = "canopy.distribute_circular"
    bl_label = "Distribution Circulaire"
    bl_description = "Distribue les objets en cercle autour du cercle principal"
    bl_options = {'REGISTER', 'UNDO'}
    
    @classmethod
    def poll(cls, context):
        state = canopy_state.snap_circle
        return state.primary_location is not None and len(context.selected_objects) > 1
    
    def execute(self, context):
        state = canopy_state.snap_circle
        selected = [obj for obj in context.selected_objects if obj.type == 'MESH']
        
        if len(selected) < 2:
            self.report({'WARNING'}, "Au moins 2 meshes requis")
            return {'CANCELLED'}
        
        # Calculer le rayon moyen
        radius = 0
        for obj in selected:
            radius += (obj.location - state.primary_location).length
        radius /= len(selected)
        
        if radius < 0.001:
            radius = 1.0
        
        # Distribuer en cercle
        angle_step = 2 * math.pi / len(selected)
        
        for i, obj in enumerate(selected):
            angle = angle_step * i
            obj.location = state.primary_location + Vector((
                math.cos(angle) * radius,
                math.sin(angle) * radius,
                0
            ))
        
        self.report({'INFO'}, f"{len(selected)} objets distribués en cercle")
        return {'FINISHED'}


class CANOPY_OT_distribute_grid(Operator):
    """Distribue les objets en grille"""
    bl_idname = "canopy.distribute_grid"
    bl_label = "Distribution Grille"
    bl_description = "Distribue les objets en grille à partir du cercle principal"
    bl_options = {'REGISTER', 'UNDO'}
    
    columns: IntProperty(
        name="Colonnes",
        default=3,
        min=1,
        max=20
    )
    
    spacing: FloatProperty(
        name="Espacement",
        default=2.0,
        min=0.1,
        max=100.0
    )
    
    @classmethod
    def poll(cls, context):
        state = canopy_state.snap_circle
        return state.primary_location is not None and len(context.selected_objects) > 1
    
    def execute(self, context):
        state = canopy_state.snap_circle
        selected = [obj for obj in context.selected_objects if obj.type == 'MESH']
        
        if not selected:
            self.report({'WARNING'}, "Aucun mesh sélectionné")
            return {'CANCELLED'}
        
        for i, obj in enumerate(selected):
            col = i % self.columns
            row = i // self.columns
            
            obj.location = state.primary_location + Vector((
                col * self.spacing,
                row * self.spacing,
                0
            ))
        
        self.report({'INFO'}, f"{len(selected)} objets distribués en grille")
        return {'FINISHED'}
    
    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)


# ══════════════════════════════════════════════════════════════════════════════
# LISTE DES CLASSES
# ══════════════════════════════════════════════════════════════════════════════

classes = (
    CANOPY_OT_move_primary_to_secondary,
    CANOPY_OT_move_secondary_to_primary,
    CANOPY_OT_snap_selection_to_primary,
    CANOPY_OT_swap_positions,
    CANOPY_OT_move_by_offset,
    CANOPY_OT_align_to_axis,
    CANOPY_OT_distribute_linear,
    CANOPY_OT_distribute_circular,
    CANOPY_OT_distribute_grid,
)
