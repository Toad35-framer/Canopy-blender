# ══════════════════════════════════════════════════════════════════════════════
# CANOPY V2 - Math Utils - Popup Modale
# Interface utilisateur pour la saisie d'expressions mathématiques
# ══════════════════════════════════════════════════════════════════════════════

import bpy
from bpy.types import Operator, PropertyGroup
from bpy.props import StringProperty, BoolProperty, FloatProperty, EnumProperty

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
# PROPRIÉTÉS GLOBALES
# ══════════════════════════════════════════════════════════════════════════════

class CANOPY_MathUtilsState(PropertyGroup):
    """État global de Math Utils pour la session."""
    
    # Expression courante
    expression: StringProperty(
        name="Expression",
        description="Expression mathématique à évaluer",
        default="",
    )
    
    # Résultat calculé
    result: StringProperty(
        name="Résultat",
        description="Résultat du calcul",
        default="",
    )
    
    # État de validation
    is_calculated: BoolProperty(
        name="Calculé",
        description="Le résultat a été calculé",
        default=False,
    )
    
    # Historique (stocké comme string séparé par |)
    history: StringProperty(
        name="Historique",
        description="Historique des expressions",
        default="",
    )
    
    # Afficher l'aide
    show_help: BoolProperty(
        name="Afficher l'aide",
        description="Afficher le panneau d'aide",
        default=False,
    )


# ══════════════════════════════════════════════════════════════════════════════
# OPÉRATEUR POPUP PRINCIPAL
# ══════════════════════════════════════════════════════════════════════════════

class CANOPY_OT_math_utils_popup(Operator):
    """Ouvre la calculatrice Math Utils (Ctrl+M)"""
    bl_idname = "canopy.math_utils_popup"
    bl_label = "CANOPY Math Utils"
    bl_options = {'REGISTER', 'UNDO'}
    
    # Propriété pour l'expression
    expression: StringProperty(
        name="",
        description="Tapez votre expression mathématique",
        default="",
    )
    
    # État interne
    _result = None
    _error = None
    _is_calculated = False
    _copied_to_clipboard = False
    
    def invoke(self, context, event):
        """Appelé quand l'opérateur est invoqué."""
        # Réinitialiser l'état
        self._result = None
        self._error = None
        self._is_calculated = False
        self._copied_to_clipboard = False
        self.expression = ""
        
        # Ouvrir la popup
        return context.window_manager.invoke_props_dialog(self, width=400)
    
    def draw(self, context):
        """Dessine le contenu de la popup."""
        layout = self.layout
        
        # ══════════════════════════════════════════════════════════════════════
        # EN-TÊTE
        # ══════════════════════════════════════════════════════════════════════
        box_header = layout.box()
        row = box_header.row()
        row.label(text="", icon='SORTBYEXT')
        row.label(text="CANOPY Math Utils")
        row.operator("canopy.math_utils_help", text="", icon='QUESTION')
        
        layout.separator()
        
        # ══════════════════════════════════════════════════════════════════════
        # ZONE DE SAISIE
        # ══════════════════════════════════════════════════════════════════════
        box_input = layout.box()
        box_input.label(text="Expression:", icon='CONSOLE')
        
        # Champ de saisie principal
        row = box_input.row()
        row.prop(self, "expression", text="")
        row.scale_x = 1.0
        
        # ══════════════════════════════════════════════════════════════════════
        # ZONE DE RÉSULTAT
        # ══════════════════════════════════════════════════════════════════════
        box_result = layout.box()
        
        if self._error:
            # Afficher l'erreur
            row = box_result.row()
            row.alert = True
            row.label(text=f"⚠ {self._error}", icon='ERROR')
            
        elif self._result is not None:
            # Afficher le résultat
            row = box_result.row()
            row.label(text="Résultat:", icon='CHECKMARK')
            
            result_box = box_result.box()
            result_row = result_box.row()
            result_row.scale_y = 1.5
            
            # Formater le résultat
            if self._result == int(self._result):
                result_text = f"= {int(self._result)}"
            else:
                result_text = f"= {self._result:.6f}".rstrip('0').rstrip('.')
            
            result_row.label(text=result_text)
            
            # Indicateur de copie
            if self._copied_to_clipboard:
                box_result.label(text="✓ Copié dans le presse-papier!", icon='COPYDOWN')
        else:
            # État initial
            box_result.label(text="Entrez une expression et appuyez sur Entrée", icon='INFO')
        
        # ══════════════════════════════════════════════════════════════════════
        # AIDE RAPIDE
        # ══════════════════════════════════════════════════════════════════════
        layout.separator()
        
        box_help = layout.box()
        box_help.label(text="Aide rapide:", icon='LIGHT')
        
        col = box_help.column(align=True)
        col.scale_y = 0.8
        col.label(text="• Opérateurs: + - * / ** ()")
        col.label(text="• Constantes: pi, e, tau")
        col.label(text="• Fonctions: sin(), cos(), sqrt(), abs()...")
        
        # ══════════════════════════════════════════════════════════════════════
        # INSTRUCTIONS
        # ══════════════════════════════════════════════════════════════════════
        layout.separator()
        
        box_instructions = layout.box()
        col = box_instructions.column(align=True)
        col.scale_y = 0.9
        
        if not self._is_calculated:
            col.label(text="[Entrée] → Calculer", icon='PLAY')
        else:
            col.label(text="[Entrée] → Valider et copier", icon='COPYDOWN')
            col.label(text="[Échap] → Annuler", icon='X')
    
    def execute(self, context):
        """Exécuté quand on appuie sur Entrée ou OK."""
        
        if not self.expression.strip():
            self._error = "Expression vide"
            return {'CANCELLED'}
        
        # Premier appui sur Entrée → Calculer
        if not self._is_calculated:
            result, error = CanopyMathEvaluator.evaluate(self.expression)
            
            if error:
                self._error = error
                self._result = None
                self._is_calculated = False
                # Garder la popup ouverte
                return {'RUNNING_MODAL'}
            else:
                self._result = result
                self._error = None
                self._is_calculated = True
                # Garder la popup ouverte pour le second Entrée
                return {'RUNNING_MODAL'}
        
        # Second appui sur Entrée → Copier et fermer
        else:
            if self._result is not None:
                # Copier dans le presse-papier
                self._copy_to_clipboard(context, self._result)
                self._copied_to_clipboard = True
                
                # Ajouter à l'historique
                self._add_to_history(context, self.expression, self._result)
                
                # Rapport
                self.report({'INFO'}, f"Résultat copié: {self._result}")
            
            return {'FINISHED'}
    
    def _copy_to_clipboard(self, context, value):
        """Copie la valeur dans le presse-papier système."""
        # Formater la valeur
        if value == int(value):
            text = str(int(value))
        else:
            text = f"{value:.6f}".rstrip('0').rstrip('.')
        
        # Utiliser le presse-papier de Blender
        context.window_manager.clipboard = text
    
    def _add_to_history(self, context, expression, result):
        """Ajoute l'expression à l'historique."""
        # TODO: Implémenter le stockage persistant de l'historique
        pass


# ══════════════════════════════════════════════════════════════════════════════
# OPÉRATEUR D'AIDE
# ══════════════════════════════════════════════════════════════════════════════

class CANOPY_OT_math_utils_help(Operator):
    """Affiche l'aide complète de Math Utils"""
    bl_idname = "canopy.math_utils_help"
    bl_label = "Aide Math Utils"
    bl_options = {'REGISTER'}
    
    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=500)
    
    def draw(self, context):
        layout = self.layout
        
        # Titre
        box = layout.box()
        box.label(text="CANOPY Math Utils - Aide complète", icon='HELP')
        
        layout.separator()
        
        # Opérateurs
        box = layout.box()
        box.label(text="OPÉRATEURS", icon='ADD')
        col = box.column(align=True)
        col.scale_y = 0.9
        col.label(text="+  Addition")
        col.label(text="-  Soustraction")
        col.label(text="*  Multiplication")
        col.label(text="/  Division")
        col.label(text="** ou ^  Puissance")
        col.label(text="()  Parenthèses")
        
        # Constantes
        box = layout.box()
        box.label(text="CONSTANTES", icon='DOT')
        col = box.column(align=True)
        col.scale_y = 0.9
        col.label(text="pi = 3.14159265...")
        col.label(text="e = 2.71828182...")
        col.label(text="tau = 6.28318530... (2π)")
        
        # Fonctions trigonométriques
        box = layout.box()
        box.label(text="TRIGONOMÉTRIE (radians)", icon='DRIVER_ROTATIONAL_DIFFERENCE')
        col = box.column(align=True)
        col.scale_y = 0.9
        col.label(text="sin(x)  cos(x)  tan(x)")
        col.label(text="asin(x)  acos(x)  atan(x)")
        col.label(text="degrees(rad)  radians(deg)")
        
        # Fonctions mathématiques
        box = layout.box()
        box.label(text="MATHÉMATIQUES", icon='PLUS')
        col = box.column(align=True)
        col.scale_y = 0.9
        col.label(text="sqrt(x) - Racine carrée")
        col.label(text="abs(x) - Valeur absolue")
        col.label(text="pow(x, y) - Puissance")
        col.label(text="exp(x) - Exponentielle")
        col.label(text="log(x) - Logarithme naturel")
        col.label(text="log10(x) - Logarithme base 10")
        col.label(text="floor(x) - Arrondi inférieur")
        col.label(text="ceil(x) - Arrondi supérieur")
        col.label(text="round(x) - Arrondi standard")
        col.label(text="min(a, b, ...) - Minimum")
        col.label(text="max(a, b, ...) - Maximum")
        
        # Exemples
        box = layout.box()
        box.label(text="EXEMPLES", icon='FILE_TEXT')
        col = box.column(align=True)
        col.scale_y = 0.9
        col.label(text="2*pi → 6.283")
        col.label(text="sqrt(16) → 4")
        col.label(text="sin(radians(45)) → 0.707")
        col.label(text="2**10 → 1024")
        col.label(text="(2500 + 500) / 2 → 1500")
    
    def execute(self, context):
        return {'FINISHED'}


# ══════════════════════════════════════════════════════════════════════════════
# OPÉRATEUR POUR CHAMP CANOPY
# ══════════════════════════════════════════════════════════════════════════════

class CANOPY_OT_math_field_popup(Operator):
    """Ouvre Math Utils pour ce champ"""
    bl_idname = "canopy.math_field_popup"
    bl_label = "Math Utils"
    bl_options = {'REGISTER', 'UNDO'}
    
    # Propriétés pour savoir quel champ mettre à jour
    target_data_path: StringProperty(
        name="Data Path",
        description="Chemin vers la propriété cible",
        default="",
    )
    
    target_property: StringProperty(
        name="Property",
        description="Nom de la propriété cible",
        default="",
    )
    
    # Expression
    expression: StringProperty(
        name="",
        description="Expression mathématique",
        default="",
    )
    
    # État interne
    _result = None
    _error = None
    _is_calculated = False
    
    def invoke(self, context, event):
        self._result = None
        self._error = None
        self._is_calculated = False
        self.expression = ""
        
        return context.window_manager.invoke_props_dialog(self, width=350)
    
    def draw(self, context):
        layout = self.layout
        
        # En-tête compact
        row = layout.row()
        row.label(text="Math Utils", icon='SORTBYEXT')
        
        # Champ de saisie
        layout.prop(self, "expression", text="")
        
        # Résultat
        if self._error:
            row = layout.row()
            row.alert = True
            row.label(text=f"⚠ {self._error}")
        elif self._result is not None:
            box = layout.box()
            if self._result == int(self._result):
                box.label(text=f"= {int(self._result)}")
            else:
                box.label(text=f"= {self._result:.4f}")
        
        # Instructions
        if not self._is_calculated:
            layout.label(text="[Entrée] Calculer", icon='PLAY')
        else:
            layout.label(text="[Entrée] Appliquer au champ", icon='CHECKMARK')
    
    def execute(self, context):
        if not self.expression.strip():
            return {'CANCELLED'}
        
        # Premier Entrée → Calculer
        if not self._is_calculated:
            result, error = CanopyMathEvaluator.evaluate(self.expression)
            
            if error:
                self._error = error
                return {'RUNNING_MODAL'}
            else:
                self._result = result
                self._is_calculated = True
                return {'RUNNING_MODAL'}
        
        # Second Entrée → Appliquer
        else:
            if self._result is not None and self.target_data_path and self.target_property:
                try:
                    # Résoudre le chemin de données
                    target = eval(self.target_data_path)
                    setattr(target, self.target_property, self._result)
                    self.report({'INFO'}, f"Valeur appliquée: {self._result}")
                except Exception as e:
                    self.report({'ERROR'}, f"Erreur: {e}")
            
            return {'FINISHED'}


# ══════════════════════════════════════════════════════════════════════════════
# ENREGISTREMENT
# ══════════════════════════════════════════════════════════════════════════════

classes = [
    CANOPY_MathUtilsState,
    CANOPY_OT_math_utils_popup,
    CANOPY_OT_math_utils_help,
    CANOPY_OT_math_field_popup,
]


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    
    # Enregistrer les propriétés globales
    bpy.types.WindowManager.canopy_math_utils = bpy.props.PointerProperty(
        type=CANOPY_MathUtilsState
    )


def unregister():
    # Supprimer les propriétés globales
    if hasattr(bpy.types.WindowManager, 'canopy_math_utils'):
        del bpy.types.WindowManager.canopy_math_utils
    
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
