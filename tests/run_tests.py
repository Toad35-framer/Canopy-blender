# ══════════════════════════════════════════════════════════════════════════════
# CANOPY V2 - Tests
# Script pour lancer les tests
# ══════════════════════════════════════════════════════════════════════════════
#
# Usage:
#   blender --background --python tests/run_tests.py
#
# ══════════════════════════════════════════════════════════════════════════════

import sys
import os

# Ajouter le dossier parent au path pour les imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def run_tests():
    """Lance tous les tests CANOPY"""
    print("=" * 60)
    print("CANOPY V2 - Tests")
    print("=" * 60)
    
    # Test import modules
    print("\n[Test] Import des modules...")
    try:
        from canopy import core
        print("  ✅ canopy.core")
    except ImportError as e:
        print(f"  ❌ canopy.core: {e}")
    
    try:
        from canopy import math_utils
        print("  ✅ canopy.math_utils")
    except ImportError as e:
        print(f"  ❌ canopy.math_utils: {e}")
    
    # Test évaluateur mathématique
    print("\n[Test] Évaluateur mathématique...")
    try:
        from canopy.math_utils.evaluator import CanopyMathEvaluator
        
        tests = [
            ("2 + 3", 5.0),
            ("2 * pi", 6.283185307179586),
            ("sqrt(16)", 4.0),
            ("2 ** 10", 1024.0),
        ]
        
        for expr, expected in tests:
            result, error = CanopyMathEvaluator.evaluate(expr)
            if error:
                print(f"  ❌ {expr} -> Erreur: {error}")
            elif abs(result - expected) < 0.0001:
                print(f"  ✅ {expr} = {result}")
            else:
                print(f"  ❌ {expr} = {result} (attendu: {expected})")
    except Exception as e:
        print(f"  ❌ Erreur: {e}")
    
    # Test état global
    print("\n[Test] État global...")
    try:
        from canopy.core.state import canopy_state
        canopy_state.reset_all()
        print("  ✅ canopy_state.reset_all()")
    except Exception as e:
        print(f"  ❌ Erreur: {e}")
    
    # Test événements
    print("\n[Test] Système d'événements...")
    try:
        from canopy.core.events import canopy_events
        
        received = []
        def callback(data):
            received.append(data)
        
        canopy_events.subscribe('TEST_EVENT', callback)
        canopy_events.emit('TEST_EVENT', {'value': 42})
        
        if len(received) == 1 and received[0]['value'] == 42:
            print("  ✅ subscribe/emit fonctionne")
        else:
            print("  ❌ subscribe/emit ne fonctionne pas")
    except Exception as e:
        print(f"  ❌ Erreur: {e}")
    
    print("\n" + "=" * 60)
    print("Tests terminés")
    print("=" * 60)


if __name__ == "__main__":
    run_tests()
