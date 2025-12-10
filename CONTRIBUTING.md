# 🤝 Contributing to CANOPY V2

Merci de votre intérêt pour contribuer à CANOPY V2 !

## 📋 Comment contribuer

### Signaler un bug

1. Vérifiez que le bug n'a pas déjà été signalé dans les [Issues](../../issues)
2. Créez une nouvelle issue avec le template "Bug Report"
3. Incluez:
   - Version de Blender
   - Version de CANOPY
   - Étapes pour reproduire
   - Comportement attendu vs observé
   - Screenshots si pertinent

### Proposer une fonctionnalité

1. Ouvrez une issue avec le template "Feature Request"
2. Décrivez clairement le besoin
3. Proposez une implémentation si possible

### Soumettre du code

1. **Fork** le repository
2. Créez une **branche** pour votre fonctionnalité
   ```bash
   git checkout -b feature/ma-fonctionnalite
   ```
3. Écrivez du code **propre et documenté**
4. Testez vos modifications
5. **Committez** avec des messages clairs
   ```bash
   git commit -m "feat(module): description courte"
   ```
6. **Push** et ouvrez une **Pull Request**

## 📐 Standards de code

### Structure des fichiers

```python
# ══════════════════════════════════════════════════════════════════════════════
# CANOPY V2 - [Nom du Module] - [Description]
# [Description détaillée]
# ══════════════════════════════════════════════════════════════════════════════

import bpy
# ... autres imports

# ══════════════════════════════════════════════════════════════════════════════
# SECTION
# ══════════════════════════════════════════════════════════════════════════════

class MaClasse:
    """Documentation de la classe"""
    pass
```

### Conventions de nommage

#### 📁 Nommage des fichiers (IMPORTANT)

**Tous les fichiers (sauf `__init__.py`) suivent le format:**
```
module-fichier.extension
```

**Exemples:**
- `core-state.py` (pas `state.py`)
- `snap_circle-operators.py` (pas `operators.py`)
- `math_utils-fr.lang` (pas `fr.lang`)

**Voir `docs/CONVENTION_NOMMAGE.md` pour les détails complets.**

#### Code Python

- **Classes Blender**: `CANOPY_OT_nom_operateur`, `CANOPY_PT_nom_panel`
- **Fonctions**: `snake_case`
- **Constantes**: `UPPER_SNAKE_CASE`
- **Variables privées**: `_prefixe_underscore`

### Documentation

- Docstrings pour toutes les fonctions/classes publiques
- Commentaires pour la logique complexe
- Type hints quand pertinent

## 🧪 Tests

Avant de soumettre:

```bash
# Lancer les tests
blender --background --python tests/run_tests.py
```

## 📜 Licence

En contribuant, vous acceptez que votre code soit sous licence GPL v3.
