# ══════════════════════════════════════════════════════════════════════════════
# CANOPY V2 - Suite CAO/DAO Bois pour Blender
# Point d'entrée principal de l'addon
# ══════════════════════════════════════════════════════════════════════════════
#
# CANOPY est une suite d'outils intégrés pour la conception et la fabrication
# de structures en bois, avec conformité Eurocode 5.
#
# INSTALLATION:
#   1. Télécharger canopy_v2.zip depuis GitHub
#   2. Dans Blender: Edit > Preferences > Add-ons > Install
#   3. Sélectionner canopy_v2.zip
#   4. Cocher "CANOPY V2" pour activer
#
# UTILISATION:
#   - Ctrl+M : Ouvre la calculatrice Math Utils (disponible partout)
#   - Panneau latéral N > onglet CANOPY
#
# REPOSITORY:
#   https://github.com/VOTRE_USERNAME/canopy-v2
#
# ══════════════════════════════════════════════════════════════════════════════

bl_info = {
    "name": "CANOPY V2",
    "author": "Jean PINEAU (Toad35)",
    "version": (2, 0, 0),
    "blender": (4, 0, 0),
    "location": "View3D > Sidebar > CANOPY",
    "description": "Suite CAO/DAO complète pour le travail du bois avec Eurocode 5",
    "warning": "",
    "doc_url": "https://github.com/VOTRE_USERNAME/canopy-v2",
    "tracker_url": "https://github.com/VOTRE_USERNAME/canopy-v2/issues",
    "category": "3D View",
}


# ══════════════════════════════════════════════════════════════════════════════
# IMPORTS DES MODULES
# ══════════════════════════════════════════════════════════════════════════════

# Module Core (toujours en premier - fondation)
from . import core

# Modules implémentés
from . import math_utils
from . import snap_circle

# Modules à venir (décommenter au fur et à mesure)
# from . import plan_manager
# from . import rec
# from . import cut_souder
# from . import creation_pieces
# from . import gestionnaire_donnees
# from . import eurocode5
# from . import modele_structurel
# from . import contacts_structurels
# from . import export_projet
# from . import interface_machines
# from . import visibility


# ══════════════════════════════════════════════════════════════════════════════
# LISTE DES MODULES ACTIFS
# ══════════════════════════════════════════════════════════════════════════════

# Ordre important: core doit être enregistré en premier
modules = [
    core,
    math_utils,
    snap_circle,           # ✅ Migré
    # plan_manager,        # 🔄 Migration en cours
    # rec,                 # 🔄 Migration en cours
    # cut_souder,          # 🔄 Migration en cours
    # creation_pieces,     # 📋 Planifié
    # gestionnaire_donnees,# 📋 Planifié
    # eurocode5,           # 📋 Planifié
    # modele_structurel,   # 📋 Planifié
    # contacts_structurels,# 📋 Planifié
    # export_projet,       # 📋 Planifié
    # interface_machines,  # 📋 Planifié
    # visibility,          # 🔄 Migration en cours
]


# ══════════════════════════════════════════════════════════════════════════════
# ENREGISTREMENT
# ══════════════════════════════════════════════════════════════════════════════

def register():
    """Enregistrement de tous les modules CANOPY"""
    print("")
    print("═" * 60)
    print("  CANOPY V2 - Suite CAO/DAO Bois pour Blender")
    print("═" * 60)
    
    success_count = 0
    error_count = 0
    
    for module in modules:
        module_name = module.__name__.split('.')[-1]
        if hasattr(module, 'register'):
            try:
                module.register()
                success_count += 1
            except Exception as e:
                print(f"  ❌ Erreur module {module_name}: {e}")
                error_count += 1
    
    print("─" * 60)
    print(f"  ✅ {success_count} module(s) chargé(s)")
    if error_count > 0:
        print(f"  ❌ {error_count} erreur(s)")
    print("")
    print("  📌 Raccourcis:")
    print("     • Ctrl+M       : Math Utils (calculatrice)")
    print("     • Ctrl+Shift+S : Menu radial Snap Circle")
    print("     • N            : Panneau latéral CANOPY")
    print("")
    print("═" * 60)
    print("")


def unregister():
    """Désenregistrement de tous les modules CANOPY"""
    print("")
    print("[CANOPY] Désactivation...")
    
    # Désenregistrer dans l'ordre inverse
    for module in reversed(modules):
        module_name = module.__name__.split('.')[-1]
        if hasattr(module, 'unregister'):
            try:
                module.unregister()
            except Exception as e:
                print(f"  ⚠️ Erreur désenregistrement {module_name}: {e}")
    
    print("[CANOPY] Désactivé")
    print("")


# ══════════════════════════════════════════════════════════════════════════════
# POINT D'ENTRÉE DIRECT (pour tests)
# ══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    register()
