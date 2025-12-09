# ══════════════════════════════════════════════════════════════════════════════
# CANOPY V2 - Module Math Utils
# Calculateur d'expressions mathématiques pour l'écosystème CANOPY
# ══════════════════════════════════════════════════════════════════════════════
#
# Ce module fournit un système d'évaluation d'expressions mathématiques
# sécurisé utilisable par tous les modules CANOPY.
#
# FONCTIONNALITÉS:
#   - Popup globale accessible via Ctrl+M
#   - Bouton 📐 intégrable dans tous les champs numériques
#   - Double validation: Entrée = calculer, Entrée×2 = copier dans presse-papier
#   - Sandbox sécurisé (pas d'exécution de code malicieux)
#   - Fonctions: sin, cos, tan, sqrt, abs, log, exp, etc.
#   - Constantes: pi, e, tau
#
# UTILISATION DANS LES AUTRES MODULES:
#
#   from canopy.math_utils import draw_math_field, get_math_value
#
#   # Dans la méthode draw() d'un panel:
#   draw_math_field(layout, data, "ma_propriete", text="Longueur (mm)")
#
#   # Pour récupérer la valeur:
#   valeur = get_math_value(data, "ma_propriete", default=0.0)
#
# ══════════════════════════════════════════════════════════════════════════════

# Imports des sous-modules
from . import evaluator
from . import ui_popup
from . import ui_helpers
from . import keymap

# Exports publics pour les autres modules
from .evaluator import (
    CanopyMathEvaluator,
    evaluate_expression,
    validate_expression,
)

from .ui_helpers import (
    draw_math_field,
    draw_math_field_row,
    draw_expression_field,
    get_math_value,
    is_valid_expression,
    format_result,
)


# ══════════════════════════════════════════════════════════════════════════════
# INFORMATIONS DU MODULE
# ══════════════════════════════════════════════════════════════════════════════

__all__ = [
    # Évaluateur
    'CanopyMathEvaluator',
    'evaluate_expression',
    'validate_expression',
    
    # Helpers UI
    'draw_math_field',
    'draw_math_field_row',
    'draw_expression_field',
    'get_math_value',
    'is_valid_expression',
    'format_result',
]

__version__ = "2.0.0"
__author__ = "Jean PINEAU"


# ══════════════════════════════════════════════════════════════════════════════
# ENREGISTREMENT BLENDER
# ══════════════════════════════════════════════════════════════════════════════

def register():
    """Enregistre le module Math Utils dans Blender."""
    print("[CANOPY] Enregistrement du module Math Utils...")
    
    # Enregistrer les opérateurs et propriétés
    ui_popup.register()
    
    # Enregistrer les raccourcis clavier
    keymap.register()
    
    print("[CANOPY] Module Math Utils enregistré ✓")
    print("[CANOPY] → Raccourci: Ctrl+M pour ouvrir la calculatrice")


def unregister():
    """Désenregistre le module Math Utils de Blender."""
    print("[CANOPY] Désenregistrement du module Math Utils...")
    
    # Désenregistrer les raccourcis clavier
    keymap.unregister()
    
    # Désenregistrer les opérateurs et propriétés
    ui_popup.unregister()
    
    print("[CANOPY] Module Math Utils désenregistré")


# ══════════════════════════════════════════════════════════════════════════════
# TEST SI EXÉCUTÉ DIRECTEMENT
# ══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    # Test basique de l'évaluateur
    print("=" * 60)
    print("CANOPY Math Utils - Test")
    print("=" * 60)
    
    tests = [
        "2 + 3",
        "2 * pi",
        "sqrt(16)",
        "sin(45 * pi / 180)",
        "2 ** 10",
    ]
    
    for expr in tests:
        result = evaluate_expression(expr)
        print(f"  {expr:25} = {result}")
    
    print("=" * 60)
