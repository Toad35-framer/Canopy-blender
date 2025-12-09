# 📚 Documentation CANOPY V2

Ce dossier contient la documentation technique du projet CANOPY V2.

## Structure

```
docs/
├── 10-Analyse_Globale.md          # Vue d'ensemble du projet
├── 20-Architecture_Generale.md    # Architecture technique
├── 30-Module_Math_Utils.md        # Documentation Math Utils
├── 40-Module_Snap_Circle.md       # Documentation Snap Circle
├── ...                            # Autres modules
└── GUIDE_REDACTIONNEL_CANOPY.md   # Guide de style
```

## Conversion depuis .docx

Les documents originaux sont au format .docx. Pour les convertir en Markdown :

```bash
# Avec pandoc
pandoc -f docx -t markdown input.docx -o output.md
```

## Contributions

Voir [CONTRIBUTING.md](../CONTRIBUTING.md) pour les guidelines de documentation.
