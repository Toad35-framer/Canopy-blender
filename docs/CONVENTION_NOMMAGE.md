# ══════════════════════════════════════════════════════════════════════════════
# CANOPY V2 - Convention de Nommage des Fichiers
# Guide pour le développement et la continuité inter-conversations
# ══════════════════════════════════════════════════════════════════════════════

## 📋 Règle de Nommage

**TOUS les fichiers (sauf `__init__.py`) suivent le format:**

```
module-fichier.extension
```

### Exemples:

| Module | Fichier | Nom complet |
|--------|---------|-------------|
| core | state.py | `core-state.py` |
| core | events.py | `core-events.py` |
| math_utils | evaluator.py | `math_utils-evaluator.py` |
| math_utils | fr.lang | `math_utils-fr.lang` |
| snap_circle | core.py | `snap_circle-core.py` |
| snap_circle | renderer.py | `snap_circle-renderer.py` |
| plan_manager | projector.py | `plan_manager-projector.py` |

---

## 🎯 Pourquoi cette convention ?

### 1. Identification immédiate
En voyant `snap_circle-rotation.py`, on sait immédiatement:
- **Module:** snap_circle
- **Fichier:** rotation
- **Fonction:** Gestion des rotations du système Snap Circle

### 2. Continuité inter-conversations
Lors d'une nouvelle conversation avec Claude, vous pouvez uploader les fichiers 
avec leur nom complet. Claude comprendra immédiatement leur contexte.

### 3. Pas de conflits
Deux modules différents peuvent avoir un fichier `core.py`:
- `snap_circle-core.py`
- `plan_manager-core.py`

---

## 📁 Structure type d'un module

```
canopy/
├── mon_module/
│   ├── __init__.py                    # ⚠️ Garde son nom standard
│   ├── mon_module-core.py             # Logique principale
│   ├── mon_module-operators.py        # Opérateurs Blender
│   ├── mon_module-ui_panel.py         # Interface utilisateur
│   ├── mon_module-properties.py       # PropertyGroup
│   ├── mon_module-keymap.py           # Raccourcis clavier
│   └── lang/
│       ├── mon_module-fr.lang         # Traductions FR
│       └── mon_module-en.lang         # Traductions EN
```

---

## 🔧 Système d'import dynamique

Python ne supporte pas nativement les tirets dans les noms de modules.
Chaque `__init__.py` utilise ce système d'import:

```python
import importlib.util
import sys
from pathlib import Path

def import_submodule(module_name: str, file_name: str):
    """
    Importe un sous-module depuis un fichier avec tiret dans le nom.
    
    Args:
        module_name: Nom du module parent (ex: 'canopy.snap_circle')
        file_name: Nom du fichier sans extension (ex: 'snap_circle-core')
    
    Returns:
        Le module importé
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

# Utilisation dans __init__.py:
_MODULE_NAME = __name__
core = import_submodule(_MODULE_NAME, 'mon_module-core')
operators = import_submodule(_MODULE_NAME, 'mon_module-operators')
```

---

## 🔗 Imports entre fichiers du même module

Pour importer depuis un fichier frère (ex: `snap_circle-operators.py` a besoin 
de `snap_circle-core.py`):

```python
# Dans snap_circle-operators.py

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

# Import des dépendances
_core = _import_sibling('snap_circle-core')
_renderer = _import_sibling('snap_circle-renderer')

# Aliases pour usage dans le fichier
ElementDetector = _core.ElementDetector
HistoryManager = _core.HistoryManager
```

---

## 📤 Workflow avec Claude

### 1. Nouvelle conversation
```
Utilisateur: "Claude, voici les fichiers à modifier:"
[Upload: snap_circle-core.py, snap_circle-operators.py]

Claude comprend immédiatement:
- Module: snap_circle
- Fichiers: core et operators
- Peut générer les modifications correctement
```

### 2. Demande de modification
```
Utilisateur: "Ajoute une fonction dans snap_circle-rotation.py"

Claude:
- Sait que c'est le fichier rotation du module snap_circle
- Génère le code avec les bons imports
- Respecte la convention de nommage
```

### 3. Création de nouveau module
```
Utilisateur: "Crée le module plan_manager"

Claude génère:
- plan_manager/__init__.py
- plan_manager/plan_manager-core.py
- plan_manager/plan_manager-operators.py
- etc.
```

---

## ✅ Checklist nouveau fichier

- [ ] Nom: `module-fichier.py`
- [ ] En-tête avec description
- [ ] Fonction `_import_sibling()` si imports internes nécessaires
- [ ] Ajout dans `__init__.py` du module
- [ ] Variable `classes` si contient des classes Blender à enregistrer

---

## 📚 Références

- **Structure complète:** Voir `docs/20-Architecture_Generale.docx`
- **Guide rédactionnel:** Voir `GUIDE_REDACTIONNEL_CANOPY.md`
- **Exemples:** Voir module `snap_circle/` comme référence
