# ══════════════════════════════════════════════════════════════════════════════
# CANOPY V2 - Math Utils - UI Helpers
# Fonctions d'aide pour intégrer Math Utils dans les autres modules
# ══════════════════════════════════════════════════════════════════════════════

import bpy
from bpy.types import UILayout
# Import dynamique pour fichiers avec tirets
import importlib.util
import sys
from pathlib import Path

def _import_sibling(file_name):
    """Importe un fichier frère avec tiret dans le nom"""
    current_dir = Path(__file__).parent
    file_path = current_dir / f"{file_name}.py"
    module_name = f"canopy.math_utils.{file_name.replace('-', '_')}"
    
    if module_name in sys.modules:
        return sys.modules[module_name]
    
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module

_evaluator = _import_sibling('math_utils-evaluator')
CanopyMathEvaluator = _evaluator.CanopyMathEvaluator


# ══════════════════════════════════════════════════════════════════════════════
# FONCTION PRINCIPALE : Dessiner un champ avec bouton Math Utils
# ══════════════════════════════════════════════════════════════════════════════

def draw_math_field(
    layout: UILayout,
    data,
    property_name: str,
    text: str = "",
    icon: str = 'NONE',
    slider: bool = False,
    factor: float = 0.85,
):
    """
    Dessine un champ de propriété avec un bouton Math Utils à côté.
    
    Cette fonction est destinée à être utilisée par TOUS les modules CANOPY
    pour offrir une interface cohérente avec accès à Math Utils.
    
    Args:
        layout: Le layout Blender où dessiner
        data: L'objet contenant la propriété (ex: context.scene, self, etc.)
        property_name: Le nom de la propriété (ex: "longueur", "angle")
        text: Le label du champ (optionnel)
        icon: L'icône à afficher (optionnel)
        slider: Afficher comme slider (optionnel)
        factor: Proportion du champ vs bouton (0.85 = 85% champ, 15% bouton)
    
    Usage dans un autre module:
        from canopy.math_utils.ui_helpers import draw_math_field
        
        def draw(self, context):
            layout = self.layout
            draw_math_field(layout, context.scene, "ma_propriete", text="Longueur")
    """
    # Créer une ligne avec split
    row = layout.row(align=True)
    
    # Partie gauche : le champ de propriété
    split = row.split(factor=factor, align=True)
    
    if icon != 'NONE':
        split.prop(data, property_name, text=text, icon=icon, slider=slider)
    else:
        split.prop(data, property_name, text=text, slider=slider)
    
    # Partie droite : le bouton Math Utils
    # Construire le data_path pour identifier la cible
    data_path = repr(data)
    
    op = split.operator(
        "canopy.math_field_popup",
        text="",
        icon='SORTBYEXT',  # Icône calculatrice
    )
    op.target_data_path = data_path
    op.target_property = property_name
    
    return row


def draw_math_field_row(
    layout: UILayout,
    data,
    property_name: str,
    text: str = "",
    icon: str = 'NONE',
):
    """
    Version simplifiée qui crée automatiquement une row.
    
    Usage:
        draw_math_field_row(layout, self, "distance", text="Distance (mm)")
    """
    return draw_math_field(layout, data, property_name, text, icon)


# ══════════════════════════════════════════════════════════════════════════════
# FONCTION : Champ d'expression avec aperçu en temps réel
# ══════════════════════════════════════════════════════════════════════════════

def draw_expression_field(
    layout: UILayout,
    data,
    expression_prop: str,
    result_prop: str = None,
    text: str = "Expression",
    show_result: bool = True,
):
    """
    Dessine un champ pour saisir une expression avec aperçu du résultat.
    
    Ce type de champ stocke l'expression ET le résultat séparément,
    permettant de conserver la formule originale.
    
    Args:
        layout: Le layout Blender
        data: L'objet contenant les propriétés
        expression_prop: Nom de la propriété StringProperty pour l'expression
        result_prop: Nom de la propriété FloatProperty pour le résultat (optionnel)
        text: Label du champ
        show_result: Afficher l'aperçu du résultat
    
    Usage:
        # Dans votre module, définir les propriétés:
        longueur_expr: StringProperty(name="Expression", default="")
        longueur_value: FloatProperty(name="Valeur", default=0.0)
        
        # Dans draw():
        draw_expression_field(layout, self, "longueur_expr", "longueur_value", "Longueur")
    """
    box = layout.box()
    
    # Ligne d'en-tête
    row = box.row(align=True)
    row.label(text=text, icon='DRIVER_TRANSFORM')
    
    # Bouton aide Math Utils
    row.operator("canopy.math_utils_help", text="", icon='QUESTION')
    
    # Champ d'expression
    row = box.row(align=True)
    row.prop(data, expression_prop, text="")
    
    # Bouton calculer
    op = row.operator("canopy.math_field_popup", text="", icon='SORTBYEXT')
    
    # Aperçu du résultat
    if show_result:
        expression = getattr(data, expression_prop, "")
        
        if expression:
            result, error = CanopyMathEvaluator.evaluate(expression)
            
            result_row = box.row()
            
            if error:
                result_row.alert = True
                result_row.label(text=f"⚠ {error}", icon='ERROR')
            else:
                # Formater le résultat
                if result == int(result):
                    result_text = f"= {int(result)}"
                else:
                    result_text = f"= {result:.4f}"
                
                result_row.label(text=result_text, icon='CHECKMARK')
                
                # Mettre à jour la propriété résultat si fournie
                if result_prop and hasattr(data, result_prop):
                    setattr(data, result_prop, result)


# ══════════════════════════════════════════════════════════════════════════════
# FONCTION : Récupérer la valeur d'un champ Math Utils
# ══════════════════════════════════════════════════════════════════════════════

def get_math_value(data, expression_prop: str, default: float = 0.0) -> float:
    """
    Évalue l'expression stockée dans une propriété et retourne le résultat.
    
    Args:
        data: L'objet contenant la propriété
        expression_prop: Nom de la propriété contenant l'expression
        default: Valeur par défaut si erreur
    
    Returns:
        float: Le résultat de l'expression ou la valeur par défaut
    
    Usage:
        longueur = get_math_value(self, "longueur_expr", default=1000.0)
    """
    expression = getattr(data, expression_prop, "")
    
    if not expression:
        return default
    
    # Si c'est déjà un nombre simple, le retourner directement
    try:
        return float(expression)
    except ValueError:
        pass
    
    # Sinon, évaluer l'expression
    return CanopyMathEvaluator.evaluate_simple(expression, default)


# ══════════════════════════════════════════════════════════════════════════════
# FONCTION : Valider une expression
# ══════════════════════════════════════════════════════════════════════════════

def is_valid_expression(expression: str) -> bool:
    """
    Vérifie si une expression est valide.
    
    Args:
        expression: L'expression à valider
    
    Returns:
        bool: True si l'expression est valide
    """
    is_valid, _ = CanopyMathEvaluator.validate_only(expression)
    return is_valid


# ══════════════════════════════════════════════════════════════════════════════
# FONCTION : Formater un résultat pour affichage
# ══════════════════════════════════════════════════════════════════════════════

def format_result(value: float, decimals: int = 4, unit: str = "") -> str:
    """
    Formate un résultat numérique pour l'affichage.
    
    Args:
        value: La valeur à formater
        decimals: Nombre de décimales maximum
        unit: Unité à ajouter (ex: "mm", "°")
    
    Returns:
        str: La valeur formatée
    """
    if value == int(value):
        result = str(int(value))
    else:
        result = f"{value:.{decimals}f}".rstrip('0').rstrip('.')
    
    if unit:
        result += f" {unit}"
    
    return result


# ══════════════════════════════════════════════════════════════════════════════
# EXEMPLE D'UTILISATION DANS UN AUTRE MODULE
# ══════════════════════════════════════════════════════════════════════════════

"""
# ══════════════════════════════════════════════════════════════════════════════
# Exemple d'intégration dans le module Création de Pièces
# ══════════════════════════════════════════════════════════════════════════════

from canopy.math_utils.ui_helpers import draw_math_field, get_math_value

class CANOPY_PT_creation_pieces(Panel):
    bl_label = "Création de Pièces"
    bl_idname = "CANOPY_PT_creation_pieces"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "CANOPY"
    
    def draw(self, context):
        layout = self.layout
        scene = context.scene
        
        # Utiliser draw_math_field pour chaque champ numérique
        box = layout.box()
        box.label(text="Dimensions", icon='ARROW_LEFTRIGHT')
        
        # Chaque champ a automatiquement le bouton Math Utils
        draw_math_field(layout, scene.canopy_piece, "longueur", text="Longueur (mm)")
        draw_math_field(layout, scene.canopy_piece, "hauteur_h", text="Hauteur h (mm)")
        draw_math_field(layout, scene.canopy_piece, "largeur_b", text="Largeur b (mm)")


class CANOPY_OT_create_piece(Operator):
    bl_idname = "canopy.create_piece"
    bl_label = "Créer la pièce"
    
    def execute(self, context):
        scene = context.scene
        
        # Récupérer les valeurs (qui peuvent être des expressions)
        longueur = get_math_value(scene.canopy_piece, "longueur", default=1000)
        hauteur = get_math_value(scene.canopy_piece, "hauteur_h", default=100)
        largeur = get_math_value(scene.canopy_piece, "largeur_b", default=50)
        
        # Créer la pièce avec ces dimensions...
        
        return {'FINISHED'}
"""
