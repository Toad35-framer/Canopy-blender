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
# CONVENTION DE NOMMAGE:
#   Tous les fichiers (sauf __init__.py) suivent le format: module-fichier.py
#   Exemple: math_utils-evaluator.py, math_utils-ui_popup.py
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

import importlib.util
import sys
from pathlib import Path

__version__ = "2.0.0"
__author__ = "Jean PINEAU"


# ══════════════════════════════════════════════════════════════════════════════
# SYSTÈME D'IMPORT POUR FICHIERS AVEC TIRETS
# ══════════════════════════════════════════════════════════════════════════════

def import_submodule(module_name: str, file_name: str):
    """
    Importe un sous-module depuis un fichier avec tiret dans le nom.
    """
    full_module_name = f"{module_name}.{file_name.replace('-', '_')}"
    
    if full_module_name in sys.modules:
        return sys.modules[full_module_name]
    
    current_dir = Path(__file__).parent
    file_path = current_dir / f"{file_name}.py"
    
    if not file_path.exists():
        raise ImportError(f"Fichier non trouvé: {file_path}")
    
    spec = importlib.util.spec_from_file_location(full_module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[full_module_name] = module
    spec.loader.exec_module(module)
    
    return module


# ══════════════════════════════════════════════════════════════════════════════
# IMPORT DES SOUS-MODULES
# ══════════════════════════════════════════════════════════════════════════════

_MODULE_NAME = __name__

# Charger les modules
evaluator = import_submodule(_MODULE_NAME, 'math_utils-evaluator')
ui_popup = import_submodule(_MODULE_NAME, 'math_utils-ui_popup')
ui_helpers = import_submodule(_MODULE_NAME, 'math_utils-ui_helpers')
keymap = import_submodule(_MODULE_NAME, 'math_utils-keymap')


# ══════════════════════════════════════════════════════════════════════════════
# EXPORTS PUBLICS
# ══════════════════════════════════════════════════════════════════════════════

# Depuis evaluator
CanopyMathEvaluator = evaluator.CanopyMathEvaluator
evaluate_expression = evaluator.evaluate_expression
validate_expression = evaluator.validate_expression

# Depuis ui_helpers
draw_math_field = ui_helpers.draw_math_field
draw_math_field_row = ui_helpers.draw_math_field_row
draw_expression_field = ui_helpers.draw_expression_field
get_math_value = ui_helpers.get_math_value
is_valid_expression = ui_helpers.is_valid_expression
format_result = ui_helpers.format_result


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
