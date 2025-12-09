# 🌳 CANOPY V2

**Suite CAO/DAO complète pour le travail du bois sous Blender avec conformité Eurocode 5**

[![Blender](https://img.shields.io/badge/Blender-4.0+-orange.svg)](https://www.blender.org/)
[![License](https://img.shields.io/badge/License-GPL%20v3-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.10+-green.svg)](https://www.python.org/)

---

## 📋 Description

CANOPY V2 est une suite d'outils intégrés pour Blender, conçue pour la conception et la fabrication de structures en bois. Elle combine :

- **Modélisation 3D** : Outils de CAO spécialisés pour le bois
- **Calcul structurel** : Analyse conforme à l'Eurocode 5
- **Export FAO** : Interface avec machines CNC

## ✨ Fonctionnalités

### Modules disponibles

| Module | Description | État |
|--------|-------------|------|
| **Math Utils** | Calculatrice d'expressions (Ctrl+M) | ✅ Complet |
| **Snap Circle** | Système de référencement par cercles | 🔄 Migration |
| **Plan Manager** | Gestion des plans de projection | 🔄 Migration |
| **REC** | Règle, Équerre, Compas virtuels | 🔄 Migration |
| **Cut/Souder** | Découpe et assemblage de pièces | 🔄 Migration |
| **Création Pièces** | Génération de pièces paramétriques | 📋 Planifié |
| **Eurocode 5** | Vérifications structurelles EC5 | 📋 Planifié |
| **Export Projet** | Export multi-format | 📋 Planifié |

### Raccourcis clavier

| Raccourci | Action |
|-----------|--------|
| `Ctrl+M` | Ouvrir Math Utils |
| `Ctrl+Shift+S` | Menu radial Snap Circle |

## 🚀 Installation

### Méthode 1 : ZIP (Recommandée)

1. Téléchargez la [dernière release](../../releases/latest)
2. Dans Blender : `Edit` → `Preferences` → `Add-ons`
3. Cliquez sur `Install...`
4. Sélectionnez le fichier `canopy_v2.zip`
5. Activez "CANOPY V2" dans la liste

### Méthode 2 : Clone Git

```bash
cd ~/.config/blender/4.0/scripts/addons/
git clone https://github.com/VOTRE_USERNAME/canopy-v2.git canopy
```

Puis activez l'addon dans les préférences Blender.

## 📁 Structure du projet

```
canopy/
├── __init__.py              # Point d'entrée principal
├── core/                    # État partagé et utilitaires
│   ├── __init__.py
│   ├── state.py            # État global de l'application
│   └── events.py           # Système d'événements inter-modules
├── math_utils/             # Calculatrice mathématique
│   ├── __init__.py
│   ├── evaluator.py        # Évaluateur d'expressions sécurisé
│   ├── ui_popup.py         # Interface popup
│   ├── ui_helpers.py       # Helpers pour autres modules
│   └── keymap.py           # Raccourcis clavier
├── snap_circle/            # Système de cercles de référence
├── plan_manager/           # Gestion des projections
├── rec/                    # Règle, Équerre, Compas
├── cut_souder/             # Outils de découpe/soudure
├── creation_pieces/        # Création de pièces
├── gestionnaire_donnees/   # Gestion des données projet
├── eurocode5/              # Calculs Eurocode 5
├── modele_structurel/      # Modèle structurel 1D
├── contacts_structurels/   # Détection des contacts
├── export_projet/          # Export multi-format
└── interface_machines/     # Interface CNC
```

## 🔧 Développement

### Prérequis

- Blender 4.0 ou supérieur
- Python 3.10+

### Installation en mode développement

```bash
# Cloner le repo
git clone https://github.com/VOTRE_USERNAME/canopy-v2.git

# Créer un lien symbolique vers le dossier addons de Blender
ln -s $(pwd)/canopy-v2/canopy ~/.config/blender/4.0/scripts/addons/canopy
```

### Lancer les tests

```bash
# Depuis le dossier racine
blender --background --python tests/run_tests.py
```

## 📖 Documentation

La documentation technique complète est disponible dans le dossier `/docs` :

- [Analyse Globale](docs/10-Analyse_Globale.md)
- [Architecture Générale](docs/20-Architecture_Generale.md)
- [Guide Rédactionnel](docs/GUIDE_REDACTIONNEL_CANOPY.md)

## 🤝 Contribution

Les contributions sont les bienvenues ! Voir [CONTRIBUTING.md](CONTRIBUTING.md) pour les guidelines.

1. Fork le projet
2. Créez une branche (`git checkout -b feature/nouvelle-fonctionnalite`)
3. Committez vos changements (`git commit -m 'Ajout nouvelle fonctionnalité'`)
4. Push sur la branche (`git push origin feature/nouvelle-fonctionnalite`)
5. Ouvrez une Pull Request

## 📜 Licence

Ce projet est sous licence GPL v3 - voir le fichier [LICENSE](LICENSE) pour plus de détails.

## 👤 Auteur

**Jean PINEAU** (Toad35)

## 🙏 Remerciements

- L'équipe Blender pour cet outil extraordinaire
- La communauté Eurocode pour les standards de calcul
- Claude (Anthropic) pour l'assistance au développement

---

<p align="center">
  <i>Fait avec ❤️ pour la communauté du bois</i>
</p>
