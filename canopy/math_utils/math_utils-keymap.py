# ══════════════════════════════════════════════════════════════════════════════
# CANOPY V2 - Math Utils - Keymap (Raccourcis clavier)
# Gestion du raccourci global Ctrl+M
# ══════════════════════════════════════════════════════════════════════════════

import bpy

# Stockage des références aux keymaps pour le nettoyage
addon_keymaps = []


def register_keymap():
    """
    Enregistre le raccourci clavier Ctrl+M pour ouvrir Math Utils.
    
    Ce raccourci est disponible dans tous les contextes de Blender:
    - Vue 3D
    - Node Editor
    - Properties
    - etc.
    """
    # Obtenir le gestionnaire de configuration des touches
    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon
    
    if kc:
        # ══════════════════════════════════════════════════════════════════════
        # Raccourci dans la Vue 3D
        # ══════════════════════════════════════════════════════════════════════
        km = kc.keymaps.new(name='3D View', space_type='VIEW_3D')
        kmi = km.keymap_items.new(
            'canopy.math_utils_popup',  # Opérateur à appeler
            type='M',                    # Touche M
            value='PRESS',               # Sur appui
            ctrl=True,                   # Avec Ctrl
            shift=False,
            alt=False,
        )
        addon_keymaps.append((km, kmi))
        
        # ══════════════════════════════════════════════════════════════════════
        # Raccourci dans le panneau Properties
        # ══════════════════════════════════════════════════════════════════════
        km = kc.keymaps.new(name='Property Editor', space_type='PROPERTIES')
        kmi = km.keymap_items.new(
            'canopy.math_utils_popup',
            type='M',
            value='PRESS',
            ctrl=True,
        )
        addon_keymaps.append((km, kmi))
        
        # ══════════════════════════════════════════════════════════════════════
        # Raccourci dans le Node Editor (Geometry Nodes, Shader, etc.)
        # ══════════════════════════════════════════════════════════════════════
        km = kc.keymaps.new(name='Node Editor', space_type='NODE_EDITOR')
        kmi = km.keymap_items.new(
            'canopy.math_utils_popup',
            type='M',
            value='PRESS',
            ctrl=True,
        )
        addon_keymaps.append((km, kmi))
        
        # ══════════════════════════════════════════════════════════════════════
        # Raccourci dans la Timeline
        # ══════════════════════════════════════════════════════════════════════
        km = kc.keymaps.new(name='Dopesheet', space_type='DOPESHEET_EDITOR')
        kmi = km.keymap_items.new(
            'canopy.math_utils_popup',
            type='M',
            value='PRESS',
            ctrl=True,
        )
        addon_keymaps.append((km, kmi))
        
        # ══════════════════════════════════════════════════════════════════════
        # Raccourci dans le Graph Editor
        # ══════════════════════════════════════════════════════════════════════
        km = kc.keymaps.new(name='Graph Editor', space_type='GRAPH_EDITOR')
        kmi = km.keymap_items.new(
            'canopy.math_utils_popup',
            type='M',
            value='PRESS',
            ctrl=True,
        )
        addon_keymaps.append((km, kmi))
        
        # ══════════════════════════════════════════════════════════════════════
        # Raccourci dans l'éditeur de texte
        # ══════════════════════════════════════════════════════════════════════
        km = kc.keymaps.new(name='Text', space_type='TEXT_EDITOR')
        kmi = km.keymap_items.new(
            'canopy.math_utils_popup',
            type='M',
            value='PRESS',
            ctrl=True,
        )
        addon_keymaps.append((km, kmi))
        
        # ══════════════════════════════════════════════════════════════════════
        # Raccourci global (Window)
        # ══════════════════════════════════════════════════════════════════════
        km = kc.keymaps.new(name='Window', space_type='EMPTY')
        kmi = km.keymap_items.new(
            'canopy.math_utils_popup',
            type='M',
            value='PRESS',
            ctrl=True,
        )
        addon_keymaps.append((km, kmi))
        
        print("[CANOPY Math Utils] Raccourci Ctrl+M enregistré")


def unregister_keymap():
    """
    Supprime les raccourcis clavier enregistrés.
    Appelé lors de la désactivation de l'addon.
    """
    # Supprimer tous les raccourcis enregistrés
    for km, kmi in addon_keymaps:
        try:
            km.keymap_items.remove(kmi)
        except:
            pass
    
    addon_keymaps.clear()
    print("[CANOPY Math Utils] Raccourcis clavier supprimés")


# ══════════════════════════════════════════════════════════════════════════════
# FONCTIONS PUBLIQUES
# ══════════════════════════════════════════════════════════════════════════════

def register():
    """Point d'entrée pour l'enregistrement."""
    register_keymap()


def unregister():
    """Point d'entrée pour le désenregistrement."""
    unregister_keymap()
