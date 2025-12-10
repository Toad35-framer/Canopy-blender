# ══════════════════════════════════════════════════════════════════════════════
# CANOPY V2 - Snap Circle - Keymap
# Gestion des raccourcis clavier
# ══════════════════════════════════════════════════════════════════════════════

import bpy

# Liste globale des keymaps enregistrés
addon_keymaps = []


# ══════════════════════════════════════════════════════════════════════════════
# ENREGISTREMENT
# ══════════════════════════════════════════════════════════════════════════════

def register_keymaps():
    """Enregistre les raccourcis clavier"""
    try:
        wm = bpy.context.window_manager
        
        if wm.keyconfigs.addon is None:
            print("[CANOPY Snap Circle] Keyconfigs non disponibles")
            return
        
        # ══════════════════════════════════════════════════════════════════════
        # Keymap 3D View
        # ══════════════════════════════════════════════════════════════════════
        km = wm.keyconfigs.addon.keymaps.new(name='3D View', space_type='VIEW_3D')
        
        # Ctrl+Shift+S : Menu radial principal
        kmi = km.keymap_items.new('wm.call_menu_pie', 'S', 'PRESS', ctrl=True, shift=True)
        kmi.properties.name = "CANOPY_MT_PIE_snap_circle_main"
        addon_keymaps.append((km, kmi))
        
        # Clic gauche : Gestionnaire de clic
        kmi = km.keymap_items.new('canopy.snap_circle_click', 'LEFTMOUSE', 'PRESS')
        addon_keymaps.append((km, kmi))
        
        print("[CANOPY Snap Circle] Raccourcis enregistrés:")
        print("  • Ctrl+Shift+S : Menu radial")
        print("  • Clic gauche : Placer cercle")
        
    except Exception as e:
        print(f"[CANOPY Snap Circle] Erreur keymaps: {e}")


def unregister_keymaps():
    """Supprime les raccourcis clavier"""
    for km, kmi in addon_keymaps:
        try:
            km.keymap_items.remove(kmi)
        except Exception:
            pass
    
    addon_keymaps.clear()
    print("[CANOPY Snap Circle] Raccourcis supprimés")
