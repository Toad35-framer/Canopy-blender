# ══════════════════════════════════════════════════════════════════════════════
# CANOPY V2 - Snap Circle - Système de Localisation
# Gestion des traductions multi-langues
# ══════════════════════════════════════════════════════════════════════════════

import bpy
from pathlib import Path
from typing import Dict, Optional

# ══════════════════════════════════════════════════════════════════════════════
# GESTIONNAIRE DE TRADUCTIONS
# ══════════════════════════════════════════════════════════════════════════════

class TranslationManager:
    """Gestionnaire centralisé des traductions"""
    
    _instance: Optional['TranslationManager'] = None
    _translations: Dict[str, str] = {}
    _current_lang: str = "fr"
    _fallback_lang: str = "en"
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        self._translations = {}
        self._load_language(self._current_lang)
    
    def _get_lang_dir(self) -> Path:
        """Retourne le chemin du dossier lang"""
        return Path(__file__).parent / "lang"
    
    def _parse_lang_file(self, filepath: Path) -> Dict[str, str]:
        """Parse un fichier .lang et retourne un dictionnaire"""
        translations = {}
        
        if not filepath.exists():
            print(f"[CANOPY] Fichier de langue non trouvé: {filepath}")
            return translations
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    
                    # Ignorer commentaires et lignes vides
                    if not line or line.startswith('#'):
                        continue
                    
                    # Parser KEY = "value" ou KEY = 'value'
                    if '=' in line:
                        key, _, value = line.partition('=')
                        key = key.strip()
                        value = value.strip()
                        
                        # Retirer les guillemets
                        if (value.startswith('"') and value.endswith('"')) or \
                           (value.startswith("'") and value.endswith("'")):
                            value = value[1:-1]
                        
                        # Traiter les séquences d'échappement
                        value = value.replace('\\n', '\n')
                        value = value.replace('\\t', '\t')
                        
                        translations[key] = value
        
        except Exception as e:
            print(f"[CANOPY] Erreur lecture {filepath}: {e}")
        
        return translations
    
    def _load_language(self, lang_code: str) -> bool:
        """Charge un fichier de langue"""
        lang_dir = self._get_lang_dir()
        # Convention de nommage : snap_circle-{lang}.lang
        lang_file = lang_dir / f"snap_circle-{lang_code}.lang"
        
        new_translations = self._parse_lang_file(lang_file)
        
        if new_translations:
            self._translations = new_translations
            self._current_lang = lang_code
            print(f"[CANOPY] Snap Circle: Langue '{lang_code}' chargée ({len(new_translations)} clés)")
            return True
        
        return False
    
    def set_language(self, lang_code: str) -> bool:
        """Change la langue active"""
        if self._load_language(lang_code):
            return True
        
        # Fallback
        if lang_code != self._fallback_lang:
            print(f"[CANOPY] Fallback vers '{self._fallback_lang}'")
            return self._load_language(self._fallback_lang)
        
        return False
    
    def get(self, key: str, **kwargs) -> str:
        """
        Récupère une traduction par sa clé.
        
        Args:
            key: Clé de traduction
            **kwargs: Variables pour le formatage (ex: name="Jean" -> {name})
        
        Returns:
            Texte traduit ou la clé si non trouvée
        """
        text = self._translations.get(key, key)
        
        # Formatage avec les arguments fournis
        if kwargs:
            try:
                text = text.format(**kwargs)
            except KeyError:
                pass  # Garder le texte tel quel si formatage échoue
        
        return text
    
    def get_current_language(self) -> str:
        """Retourne le code de la langue actuelle"""
        return self._current_lang
    
    def get_available_languages(self) -> list:
        """Liste les langues disponibles"""
        lang_dir = self._get_lang_dir()
        if not lang_dir.exists():
            return []
        return [f.stem for f in lang_dir.glob("*.lang")]
    
    def reload(self):
        """Recharge la langue actuelle"""
        self._load_language(self._current_lang)


# ══════════════════════════════════════════════════════════════════════════════
# INSTANCE GLOBALE ET FONCTION RACCOURCI
# ══════════════════════════════════════════════════════════════════════════════

# Instance singleton
_manager = TranslationManager()

def T(key: str, **kwargs) -> str:
    """
    Fonction raccourci pour les traductions.
    
    Usage:
        from . import snap_circle_lang as L
        label = L.T("UI_START")  # "🔴 DÉMARRER"
        msg = L.T("MSG_OBJECT_MOVED", name="Cube")  # "Cube déplacé..."
    """
    return _manager.get(key, **kwargs)


def set_language(lang_code: str) -> bool:
    """Change la langue du module Snap Circle"""
    return _manager.set_language(lang_code)


def get_language() -> str:
    """Retourne la langue actuelle"""
    return _manager.get_current_language()


def get_available_languages() -> list:
    """Liste les langues disponibles"""
    return _manager.get_available_languages()


def reload_translations():
    """Recharge les traductions"""
    _manager.reload()


# ══════════════════════════════════════════════════════════════════════════════
# AUTO-DÉTECTION DE LA LANGUE BLENDER
# ══════════════════════════════════════════════════════════════════════════════

def sync_with_blender_language():
    """Synchronise avec la langue de Blender"""
    try:
        blender_lang = bpy.context.preferences.view.language
        
        # Mapping des codes Blender vers nos fichiers
        lang_map = {
            'fr_FR': 'fr',
            'en_US': 'en',
            'DEFAULT': 'en',
        }
        
        lang_code = lang_map.get(blender_lang, 'en')
        
        if lang_code in get_available_languages():
            set_language(lang_code)
    except:
        pass  # Ignorer si Blender n'est pas prêt


# ══════════════════════════════════════════════════════════════════════════════
# INITIALISATION
# ══════════════════════════════════════════════════════════════════════════════

def initialize():
    """Initialise le système de traduction"""
    sync_with_blender_language()
