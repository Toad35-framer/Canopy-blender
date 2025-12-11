# ══════════════════════════════════════════════════════════════════════════════
# CANOPY V2 - Snap Circle Module
# Système de cercles de référence pour le positionnement précis
# ══════════════════════════════════════════════════════════════════════════════

bl_info = {
    "name": "CANOPY - Snap Circle",
    "author": "Jean PINEAU",
    "version": (2, 0, 0),
    "blender": (4, 0, 0),
    "location": "View3D > Sidebar > CANOPY, View3D > Shift+S",
    "description": "Système de cercles de référence pour le positionnement précis",
    "warning": "",
    "doc_url": "",
    "category": "3D View",
}

import bpy
import importlib.util
import sys
from pathlib import Path

# ══════════════════════════════════════════════════════════════════════════════
# MODULE CORE INTÉGRÉ (mode standalone)
# ══════════════════════════════════════════════════════════════════════════════

class SnapCircleState:
    """État du module Snap Circle"""
    
    def __init__(self):
        self.is_active = False
        self.draw_handler = None
        
        # Cercle principal
        self.primary_location = None
        self.primary_object = None
        self.primary_element_type = None
        
        # Cercle secondaire
        self.secondary_location = None
        self.secondary_object = None
        self.secondary_element_type = None
        
        # Pour les animations
        self._primary_bounce_scale = 1.0
        self._secondary_bounce_scale = 1.0
    
    def reset(self):
        """Remet l'état à zéro"""
        self.primary_location = None
        self.primary_object = None
        self.primary_element_type = None
        self.secondary_location = None
        self.secondary_object = None
        self.secondary_element_type = None
    
    def is_object_valid(self, obj):
        """Vérifie si un objet est valide"""
        try:
            return obj is not None and obj.name in bpy.data.objects
        except:
            return False


class CanopyState:
    """État global CANOPY (mode standalone)"""
    def __init__(self):
        self.snap_circle = SnapCircleState()
    
    def reset_all(self):
        self.snap_circle.reset()


class EventType:
    """Types d'événements"""
    SNAP_CIRCLE_STARTED = "snap_circle.started"
    SNAP_CIRCLE_STOPPED = "snap_circle.stopped"
    SNAP_CIRCLE_RESET = "snap_circle.reset"
    SNAP_CIRCLE_PRIMARY_PLACED = "snap_circle.primary_placed"
    SNAP_CIRCLE_SECONDARY_PLACED = "snap_circle.secondary_placed"
    CANOPY_INITIALIZED = "canopy.initialized"
    CANOPY_SHUTDOWN = "canopy.shutdown"


class EventManager:
    """Gestionnaire d'événements minimal"""
    def __init__(self):
        self._subscribers = {}
    
    def emit(self, event_type, data=None):
        """Émet un événement"""
        if event_type in self._subscribers:
            for callback in self._subscribers[event_type]:
                try:
                    callback(data)
                except:
                    pass
    
    def subscribe(self, event_type, callback):
        """S'abonne à un événement"""
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        self._subscribers[event_type].append(callback)
    
    def clear_subscribers(self):
        self._subscribers = {}


# Instances globales
canopy_state = CanopyState()
canopy_events = EventManager()


def redraw_viewport():
    """Force le rafraîchissement des viewports"""
    try:
        for area in bpy.context.screen.areas:
            if area.type == 'VIEW_3D':
                area.tag_redraw()
    except:
        pass


# ══════════════════════════════════════════════════════════════════════════════
# SYSTÈME D'IMPORT DYNAMIQUE
# ══════════════════════════════════════════════════════════════════════════════

_CURRENT_DIR = Path(__file__).parent.resolve()
_loaded_modules = {}

def _import_sibling(file_name):
    """Importe un fichier frère avec tiret dans le nom"""
    global _loaded_modules
    
    safe_name = file_name.replace('-', '_')
    full_module_name = f"snap_circle_{safe_name}"
    
    file_path = _CURRENT_DIR / f"{file_name}.py"
    
    if not file_path.exists():
        print(f"[Snap Circle] Fichier non trouvé: {file_path}")
        return None
    
    # Toujours recharger
    if full_module_name in sys.modules:
        del sys.modules[full_module_name]
    
    spec = importlib.util.spec_from_file_location(full_module_name, str(file_path))
    if spec is None or spec.loader is None:
        return None
    
    module = importlib.util.module_from_spec(spec)
    sys.modules[full_module_name] = module
    
    try:
        spec.loader.exec_module(module)
        _loaded_modules[file_name] = module
        return module
    except Exception as e:
        print(f"[Snap Circle] Erreur chargement {file_name}: {e}")
        import traceback
        traceback.print_exc()
        return None


# ══════════════════════════════════════════════════════════════════════════════
# CHARGEMENT DES MODULES
# ══════════════════════════════════════════════════════════════════════════════

_MODULE_NAMES = [
    'snap_circle-lang',
    'snap_circle-properties',
    'snap_circle-core',
    'snap_circle-renderer',
    'snap_circle-animations',
    'snap_circle-operators',
    'snap_circle-movement',
    'snap_circle-rotation',
    'snap_circle-keymap',
    'snap_circle-ui_panel',
    'snap_circle-ui_pie_menus',
]

_classes_to_register = []


def _collect_classes():
    """Collecte toutes les classes à enregistrer"""
    global _classes_to_register
    _classes_to_register = []
    
    for module_name in _MODULE_NAMES:
        module = _loaded_modules.get(module_name)
        if module is None:
            continue
        
        for attr_name in dir(module):
            if attr_name.startswith('_'):
                continue
            attr = getattr(module, attr_name)
            if isinstance(attr, type):
                if hasattr(attr, 'bl_idname') or hasattr(attr, 'bl_label'):
                    if attr not in _classes_to_register:
                        _classes_to_register.append(attr)
    
    return _classes_to_register


# ══════════════════════════════════════════════════════════════════════════════
# ENREGISTREMENT / DÉSENREGISTREMENT
# ══════════════════════════════════════════════════════════════════════════════

def register():
    """Enregistre le module Snap Circle"""
    print("\n[CANOPY Snap Circle] ═══════════════════════════════════════")
    print("[CANOPY Snap Circle] Début de l'enregistrement...")
    
    # Charger tous les modules
    for module_name in _MODULE_NAMES:
        module = _import_sibling(module_name)
        if module:
            print(f"  ✓ {module_name}")
        else:
            print(f"  ✗ {module_name}")
    
    # Enregistrer les propriétés
    props_module = _loaded_modules.get('snap_circle-properties')
    if props_module and hasattr(props_module, 'register_properties'):
        try:
            props_module.register_properties()
            print("  ✓ Propriétés enregistrées")
        except Exception as e:
            print(f"  ✗ Erreur propriétés: {e}")
    
    # Collecter et enregistrer les classes
    classes = _collect_classes()
    registered_count = 0
    
    for cls in classes:
        try:
            # Skip PropertyGroup (déjà fait)
            if hasattr(cls, '__mro__'):
                if bpy.types.PropertyGroup in cls.__mro__:
                    continue
            bpy.utils.register_class(cls)
            registered_count += 1
        except ValueError as e:
            if "already registered" not in str(e):
                print(f"  ! {cls.__name__}: {e}")
        except Exception as e:
            print(f"  ! {cls.__name__}: {e}")
    
    print(f"  ✓ {registered_count} classes enregistrées")
    
    # Keymaps
    keymap_module = _loaded_modules.get('snap_circle-keymap')
    if keymap_module and hasattr(keymap_module, 'register_keymaps'):
        try:
            keymap_module.register_keymaps()
            print("  ✓ Raccourcis clavier")
        except Exception as e:
            print(f"  ✗ Keymaps: {e}")
    
    # Animations
    anim_module = _loaded_modules.get('snap_circle-animations')
    if anim_module and hasattr(anim_module, 'initialize'):
        try:
            anim_module.initialize()
            print("  ✓ Animations")
        except Exception as e:
            print(f"  ✗ Animations: {e}")
    
    print("[CANOPY Snap Circle] Enregistrement terminé !")
    print("[CANOPY Snap Circle] ═══════════════════════════════════════\n")


def unregister():
    """Désenregistre le module Snap Circle"""
    print("\n[CANOPY Snap Circle] Désenregistrement...")
    
    # Animations
    anim_module = _loaded_modules.get('snap_circle-animations')
    if anim_module and hasattr(anim_module, 'cleanup'):
        try:
            anim_module.cleanup()
        except:
            pass
    
    # Keymaps
    keymap_module = _loaded_modules.get('snap_circle-keymap')
    if keymap_module and hasattr(keymap_module, 'unregister_keymaps'):
        try:
            keymap_module.unregister_keymaps()
        except:
            pass
    
    # Renderer
    renderer_module = _loaded_modules.get('snap_circle-renderer')
    if renderer_module and hasattr(renderer_module, 'unregister_draw_handler'):
        try:
            renderer_module.unregister_draw_handler()
        except:
            pass
    
    # Classes
    for cls in reversed(_classes_to_register):
        try:
            if hasattr(cls, '__mro__') and bpy.types.PropertyGroup in cls.__mro__:
                continue
            bpy.utils.unregister_class(cls)
        except:
            pass
    
    # Propriétés
    props_module = _loaded_modules.get('snap_circle-properties')
    if props_module and hasattr(props_module, 'unregister_properties'):
        try:
            props_module.unregister_properties()
        except:
            pass
    
    _loaded_modules.clear()
    print("[CANOPY Snap Circle] Désenregistrement terminé !\n")


if __name__ == "__main__":
    register()
