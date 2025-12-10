# ══════════════════════════════════════════════════════════════════════════════
# CANOPY V2 - Snap Circle - Properties
# PropertyGroup pour les paramètres du module
# ══════════════════════════════════════════════════════════════════════════════

import bpy
from bpy.types import PropertyGroup
from bpy.props import (
    FloatProperty, FloatVectorProperty, BoolProperty, EnumProperty
)


# ══════════════════════════════════════════════════════════════════════════════
# PROPRIÉTÉS
# ══════════════════════════════════════════════════════════════════════════════

class SnapCircleProperties(PropertyGroup):
    """Propriétés du module Snap Circle"""
    
    # ══════════════════════════════════════════════════════════════════════════
    # Mode de détection
    # ══════════════════════════════════════════════════════════════════════════
    detection_mode: EnumProperty(
        name="Mode de détection",
        description="Type d'éléments à détecter lors du clic",
        items=[
            ('ALL', "Tous", "Détecter vertices, arêtes et faces"),
            ('VERTEX', "Vertices", "Détecter uniquement les vertices"),
            ('EDGE', "Arêtes", "Détecter uniquement les milieux d'arêtes"),
            ('FACE', "Faces", "Détecter uniquement les centres de faces")
        ],
        default='ALL'
    )
    
    detection_threshold: FloatProperty(
        name="Seuil de détection",
        description="Distance maximale en pixels pour détecter un élément",
        default=15.0,
        min=5.0,
        max=50.0
    )
    
    # ══════════════════════════════════════════════════════════════════════════
    # Cercle principal
    # ══════════════════════════════════════════════════════════════════════════
    circle_size: FloatProperty(
        name="Taille du cercle",
        description="Taille du cercle principal en pixels",
        default=20.0,
        min=5.0,
        max=100.0
    )
    
    circle_color: FloatVectorProperty(
        name="Couleur du cercle",
        description="Couleur du cercle principal",
        default=(1.0, 0.2, 0.2, 1.0),
        size=4,
        subtype='COLOR',
        min=0.0,
        max=1.0
    )
    
    show_circle: BoolProperty(
        name="Afficher le cercle",
        description="Afficher ou masquer le cercle principal",
        default=True
    )
    
    # ══════════════════════════════════════════════════════════════════════════
    # Cercle secondaire
    # ══════════════════════════════════════════════════════════════════════════
    secondary_circle_size: FloatProperty(
        name="Taille du cercle discontinu",
        description="Taille du cercle secondaire en pixels",
        default=20.0,
        min=5.0,
        max=100.0
    )
    
    secondary_circle_color: FloatVectorProperty(
        name="Couleur du cercle discontinu",
        description="Couleur du cercle secondaire",
        default=(0.2, 0.5, 1.0, 1.0),
        size=4,
        subtype='COLOR',
        min=0.0,
        max=1.0
    )
    
    show_secondary_circle: BoolProperty(
        name="Afficher le cercle discontinu",
        description="Afficher ou masquer le cercle secondaire",
        default=True
    )


# ══════════════════════════════════════════════════════════════════════════════
# ENREGISTREMENT
# ══════════════════════════════════════════════════════════════════════════════

def register_properties():
    """Enregistre les propriétés"""
    bpy.utils.register_class(SnapCircleProperties)
    bpy.types.Scene.snap_circle_props = bpy.props.PointerProperty(
        type=SnapCircleProperties
    )


def unregister_properties():
    """Désenregistre les propriétés"""
    try:
        del bpy.types.Scene.snap_circle_props
    except:
        pass
    
    try:
        bpy.utils.unregister_class(SnapCircleProperties)
    except:
        pass
