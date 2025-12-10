# ══════════════════════════════════════════════════════════════════════════════
# CANOPY V2 - Math Utils - Évaluateur d'expressions mathématiques
# Évaluation sécurisée avec sandbox strict
# ══════════════════════════════════════════════════════════════════════════════

import math
import re
from typing import Union, Optional, Tuple

# ══════════════════════════════════════════════════════════════════════════════
# CONFIGURATION DU SANDBOX
# ══════════════════════════════════════════════════════════════════════════════

# Fonctions mathématiques autorisées
ALLOWED_FUNCTIONS = {
    # Trigonométrie
    'sin': math.sin,
    'cos': math.cos,
    'tan': math.tan,
    'asin': math.asin,
    'acos': math.acos,
    'atan': math.atan,
    'atan2': math.atan2,
    
    # Hyperboliques
    'sinh': math.sinh,
    'cosh': math.cosh,
    'tanh': math.tanh,
    
    # Puissances et racines
    'sqrt': math.sqrt,
    'pow': pow,
    'exp': math.exp,
    'log': math.log,
    'log10': math.log10,
    'log2': math.log2,
    
    # Arrondis
    'abs': abs,
    'floor': math.floor,
    'ceil': math.ceil,
    'round': round,
    
    # Divers
    'min': min,
    'max': max,
    'degrees': math.degrees,
    'radians': math.radians,
}

# Constantes autorisées
ALLOWED_CONSTANTS = {
    'pi': math.pi,
    'e': math.e,
    'tau': math.tau,
    'inf': math.inf,
}

# Caractères autorisés dans les expressions
ALLOWED_CHARS_PATTERN = re.compile(r'^[\d\s\+\-\*\/\(\)\.\,\^a-zA-Z\_]+$')

# Mots-clés Python interdits (sécurité)
FORBIDDEN_KEYWORDS = [
    'import', 'exec', 'eval', 'compile', 'open', 'file', 
    '__', 'globals', 'locals', 'getattr', 'setattr', 'delattr',
    'class', 'def', 'lambda', 'yield', 'return', 'raise',
    'try', 'except', 'finally', 'with', 'as', 'assert',
]


# ══════════════════════════════════════════════════════════════════════════════
# CLASSE PRINCIPALE
# ══════════════════════════════════════════════════════════════════════════════

class CanopyMathEvaluator:
    """
    Évaluateur d'expressions mathématiques sécurisé pour CANOPY.
    
    Utilisation:
        result = CanopyMathEvaluator.evaluate("2*pi + sqrt(16)")
        # result = (10.283185307179586, None)  # (valeur, erreur)
        
        result, error = CanopyMathEvaluator.evaluate("invalid")
        # result = None, error = "Erreur de syntaxe..."
    """
    
    # Cache des résultats pour éviter les recalculs
    _cache = {}
    _cache_max_size = 100
    
    @classmethod
    def evaluate(cls, expression: str, default: Optional[float] = None) -> Tuple[Optional[float], Optional[str]]:
        """
        Évalue une expression mathématique de manière sécurisée.
        
        Args:
            expression: L'expression à évaluer (ex: "2*pi + sqrt(16)")
            default: Valeur par défaut si erreur (None par défaut)
            
        Returns:
            Tuple (résultat, erreur):
                - Si succès: (float, None)
                - Si erreur: (default, message_erreur)
        """
        if not expression or not expression.strip():
            return (default, "Expression vide")
        
        # Normaliser l'expression
        expr = cls._normalize_expression(expression)
        
        # Vérifier le cache
        if expr in cls._cache:
            return (cls._cache[expr], None)
        
        # Validation de sécurité
        is_safe, error_msg = cls._validate_expression(expr)
        if not is_safe:
            return (default, error_msg)
        
        # Évaluation dans le sandbox
        try:
            result = cls._safe_eval(expr)
            
            # Vérifier que le résultat est un nombre
            if not isinstance(result, (int, float)):
                return (default, "Le résultat n'est pas un nombre")
            
            # Vérifier les valeurs spéciales
            if math.isnan(result):
                return (default, "Résultat: NaN (Not a Number)")
            
            if math.isinf(result):
                return (default, "Résultat: Infini")
            
            # Mettre en cache
            cls._add_to_cache(expr, result)
            
            return (result, None)
            
        except ZeroDivisionError:
            return (default, "Division par zéro")
        except ValueError as e:
            return (default, f"Erreur de valeur: {str(e)}")
        except TypeError as e:
            return (default, f"Erreur de type: {str(e)}")
        except Exception as e:
            return (default, f"Erreur: {str(e)}")
    
    @classmethod
    def evaluate_simple(cls, expression: str, default: float = 0.0) -> float:
        """
        Version simplifiée qui retourne directement le résultat ou la valeur par défaut.
        
        Args:
            expression: L'expression à évaluer
            default: Valeur par défaut si erreur
            
        Returns:
            Le résultat float ou la valeur par défaut
        """
        result, _ = cls.evaluate(expression, default)
        return result if result is not None else default
    
    @classmethod
    def validate_only(cls, expression: str) -> Tuple[bool, Optional[str]]:
        """
        Valide une expression sans l'évaluer.
        
        Returns:
            Tuple (is_valid, error_message)
        """
        if not expression or not expression.strip():
            return (False, "Expression vide")
        
        expr = cls._normalize_expression(expression)
        return cls._validate_expression(expr)
    
    @classmethod
    def get_help_text(cls) -> str:
        """Retourne le texte d'aide pour l'utilisateur."""
        return """
╔═══════════════════════════════════════════════════════════╗
║  MATH UTILS - AIDE                                        ║
╠═══════════════════════════════════════════════════════════╣
║  OPÉRATEURS:                                              ║
║    +  -  *  /  **  ()                                     ║
║                                                           ║
║  CONSTANTES:                                              ║
║    pi = 3.14159...    e = 2.71828...    tau = 6.28318...  ║
║                                                           ║
║  TRIGONOMÉTRIE (radians):                                 ║
║    sin()  cos()  tan()  asin()  acos()  atan()            ║
║                                                           ║
║  MATHÉMATIQUES:                                           ║
║    sqrt()  abs()  pow()  exp()  log()  log10()            ║
║    floor()  ceil()  round()  min()  max()                 ║
║                                                           ║
║  CONVERSION ANGLES:                                       ║
║    degrees()  radians()                                   ║
║                                                           ║
║  EXEMPLES:                                                ║
║    2*pi           → 6.283                                 ║
║    sqrt(16)       → 4.0                                   ║
║    sin(45*pi/180) → 0.707  (sin de 45°)                   ║
║    2**10          → 1024   (2 puissance 10)               ║
╚═══════════════════════════════════════════════════════════╝
"""
    
    @classmethod
    def get_suggestions(cls, partial_expr: str) -> list:
        """
        Retourne des suggestions basées sur l'expression partielle.
        
        Args:
            partial_expr: Expression en cours de saisie
            
        Returns:
            Liste de suggestions
        """
        suggestions = []
        
        if not partial_expr:
            return list(ALLOWED_FUNCTIONS.keys())[:5]
        
        # Trouver le dernier mot partiel
        words = re.findall(r'[a-zA-Z_]+', partial_expr)
        if not words:
            return suggestions
        
        last_word = words[-1].lower()
        
        # Chercher dans les fonctions
        for func_name in ALLOWED_FUNCTIONS.keys():
            if func_name.startswith(last_word) and func_name != last_word:
                suggestions.append(f"{func_name}()")
        
        # Chercher dans les constantes
        for const_name in ALLOWED_CONSTANTS.keys():
            if const_name.startswith(last_word) and const_name != last_word:
                suggestions.append(const_name)
        
        return suggestions[:5]  # Max 5 suggestions
    
    # ══════════════════════════════════════════════════════════════════════════
    # MÉTHODES PRIVÉES
    # ══════════════════════════════════════════════════════════════════════════
    
    @classmethod
    def _normalize_expression(cls, expression: str) -> str:
        """Normalise l'expression pour l'évaluation."""
        expr = expression.strip()
        
        # Remplacer ^ par ** (notation puissance courante)
        expr = expr.replace('^', '**')
        
        # Remplacer les virgules par des points (notation française)
        # Mais attention aux virgules de séparation d'arguments
        # On ne remplace que si ce n'est pas dans un contexte de fonction
        expr = re.sub(r'(\d),(\d)', r'\1.\2', expr)
        
        return expr
    
    @classmethod
    def _validate_expression(cls, expression: str) -> Tuple[bool, Optional[str]]:
        """
        Valide la sécurité de l'expression.
        
        Returns:
            Tuple (is_safe, error_message)
        """
        # Vérifier les caractères autorisés
        if not ALLOWED_CHARS_PATTERN.match(expression):
            return (False, "Caractères non autorisés détectés")
        
        # Vérifier les mots-clés interdits
        expr_lower = expression.lower()
        for keyword in FORBIDDEN_KEYWORDS:
            if keyword in expr_lower:
                return (False, f"Mot-clé interdit: {keyword}")
        
        # Vérifier les parenthèses équilibrées
        if expression.count('(') != expression.count(')'):
            return (False, "Parenthèses non équilibrées")
        
        # Vérifier que les identifiants sont autorisés
        identifiers = re.findall(r'[a-zA-Z_][a-zA-Z0-9_]*', expression)
        for ident in identifiers:
            if ident not in ALLOWED_FUNCTIONS and ident not in ALLOWED_CONSTANTS:
                return (False, f"Identifiant inconnu: {ident}")
        
        return (True, None)
    
    @classmethod
    def _safe_eval(cls, expression: str) -> float:
        """
        Évalue l'expression dans un environnement sandbox.
        """
        # Construire l'environnement sécurisé
        safe_dict = {
            '__builtins__': {},  # Désactiver tous les builtins
        }
        safe_dict.update(ALLOWED_FUNCTIONS)
        safe_dict.update(ALLOWED_CONSTANTS)
        
        # Évaluer
        return eval(expression, safe_dict, {})
    
    @classmethod
    def _add_to_cache(cls, expression: str, result: float) -> None:
        """Ajoute un résultat au cache avec gestion de la taille."""
        if len(cls._cache) >= cls._cache_max_size:
            # Supprimer le premier élément (FIFO simple)
            first_key = next(iter(cls._cache))
            del cls._cache[first_key]
        
        cls._cache[expression] = result
    
    @classmethod
    def clear_cache(cls) -> None:
        """Vide le cache des résultats."""
        cls._cache.clear()


# ══════════════════════════════════════════════════════════════════════════════
# FONCTIONS UTILITAIRES EXPORTÉES
# ══════════════════════════════════════════════════════════════════════════════

def evaluate_expression(expression: str, default: float = 0.0) -> float:
    """
    Fonction raccourci pour évaluer une expression.
    
    Usage:
        from canopy.math_utils.evaluator import evaluate_expression
        result = evaluate_expression("2*pi + sqrt(16)")
    """
    return CanopyMathEvaluator.evaluate_simple(expression, default)


def validate_expression(expression: str) -> Tuple[bool, Optional[str]]:
    """
    Fonction raccourci pour valider une expression.
    
    Usage:
        from canopy.math_utils.evaluator import validate_expression
        is_valid, error = validate_expression("2*pi")
    """
    return CanopyMathEvaluator.validate_only(expression)


# ══════════════════════════════════════════════════════════════════════════════
# TEST SI EXÉCUTÉ DIRECTEMENT
# ══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    # Tests basiques
    test_expressions = [
        "2 + 3",
        "2 * pi",
        "sqrt(16)",
        "sin(45 * pi / 180)",
        "2 ** 10",
        "log10(1000)",
        "floor(3.7)",
        "max(1, 2, 3)",
        "(5 + 3) / 2",
        "invalid",
        "1 / 0",
        "__import__('os')",
    ]
    
    print("═" * 60)
    print("CANOPY Math Utils - Tests")
    print("═" * 60)
    
    for expr in test_expressions:
        result, error = CanopyMathEvaluator.evaluate(expr)
        if error:
            print(f"  {expr:30} → ERREUR: {error}")
        else:
            print(f"  {expr:30} → {result}")
    
    print("═" * 60)
