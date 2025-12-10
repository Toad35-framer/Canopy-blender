# ══════════════════════════════════════════════════════════════════════════════
# CANOPY V2 - Core - Système d'Événements
# Communication inter-modules via événements
# ══════════════════════════════════════════════════════════════════════════════
#
# Ce module fournit un système d'événements pour permettre aux modules
# de communiquer entre eux sans dépendances directes.
#
# UTILISATION:
#   from canopy.core.events import canopy_events
#   
#   # S'abonner à un événement
#   def on_circle_placed(data):
#       print(f"Cercle placé à {data['location']}")
#   
#   canopy_events.subscribe('snap_circle.placed', on_circle_placed)
#   
#   # Émettre un événement
#   canopy_events.emit('snap_circle.placed', {'location': Vector((1, 2, 3))})
#
# ══════════════════════════════════════════════════════════════════════════════

from typing import Callable, Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum, auto


# ══════════════════════════════════════════════════════════════════════════════
# TYPES D'ÉVÉNEMENTS PRÉDÉFINIS
# ══════════════════════════════════════════════════════════════════════════════

class EventType(Enum):
    """Types d'événements prédéfinis pour CANOPY"""
    
    # ──────────────────────────────────────────────────────────────────────────
    # Snap Circle
    # ──────────────────────────────────────────────────────────────────────────
    SNAP_CIRCLE_STARTED = auto()
    SNAP_CIRCLE_STOPPED = auto()
    SNAP_CIRCLE_PRIMARY_PLACED = auto()
    SNAP_CIRCLE_SECONDARY_PLACED = auto()
    SNAP_CIRCLE_RESET = auto()
    
    # ──────────────────────────────────────────────────────────────────────────
    # Plan Manager
    # ──────────────────────────────────────────────────────────────────────────
    PLAN_MODE_ENTERED = auto()
    PLAN_MODE_EXITED = auto()
    PROJECTION_SAVED = auto()
    PROJECTION_LOADED = auto()
    
    # ──────────────────────────────────────────────────────────────────────────
    # REC
    # ──────────────────────────────────────────────────────────────────────────
    REC_LINE_CREATED = auto()
    REC_VERTEX_CREATED = auto()
    REC_CIRCLE_CREATED = auto()
    REC_ELEMENT_DELETED = auto()
    REC_ALL_CLEARED = auto()
    
    # ──────────────────────────────────────────────────────────────────────────
    # Cut/Souder
    # ──────────────────────────────────────────────────────────────────────────
    CUT_STARTED = auto()
    CUT_COMPLETED = auto()
    WELD_STARTED = auto()
    WELD_COMPLETED = auto()
    
    # ──────────────────────────────────────────────────────────────────────────
    # Général
    # ──────────────────────────────────────────────────────────────────────────
    CANOPY_INITIALIZED = auto()
    CANOPY_SHUTDOWN = auto()
    VIEWPORT_REDRAW_NEEDED = auto()


# ══════════════════════════════════════════════════════════════════════════════
# CLASSE ÉVÉNEMENT
# ══════════════════════════════════════════════════════════════════════════════

@dataclass
class Event:
    """Représente un événement émis"""
    event_type: str
    data: Dict[str, Any]
    source_module: Optional[str] = None
    timestamp: float = 0.0


# ══════════════════════════════════════════════════════════════════════════════
# GESTIONNAIRE D'ÉVÉNEMENTS
# ══════════════════════════════════════════════════════════════════════════════

class EventManager:
    """
    Gestionnaire d'événements centralisé pour CANOPY.
    
    Permet aux modules de s'abonner à des événements et d'émettre des
    événements sans avoir de dépendances directes entre eux.
    """
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        # Dictionnaire des abonnés: event_type -> [callbacks]
        self._subscribers: Dict[str, List[Callable]] = {}
        
        # Historique des événements (pour debug)
        self._history: List[Event] = []
        self._max_history_size = 100
        
        # Flag pour éviter les émissions récursives
        self._is_emitting = False
        self._pending_events: List[Event] = []
        
        self._initialized = True
    
    def subscribe(self, event_type: str, callback: Callable[[Dict[str, Any]], None]) -> None:
        """
        S'abonner à un événement.
        
        Args:
            event_type: Type d'événement (string ou EventType.name)
            callback: Fonction à appeler quand l'événement est émis
                     Signature: callback(data: Dict[str, Any]) -> None
        
        Example:
            def on_circle_placed(data):
                print(f"Cercle à {data['location']}")
            
            canopy_events.subscribe('SNAP_CIRCLE_PRIMARY_PLACED', on_circle_placed)
        """
        # Normaliser le type d'événement
        if isinstance(event_type, EventType):
            event_type = event_type.name
        
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        
        if callback not in self._subscribers[event_type]:
            self._subscribers[event_type].append(callback)
    
    def unsubscribe(self, event_type: str, callback: Callable) -> bool:
        """
        Se désabonner d'un événement.
        
        Args:
            event_type: Type d'événement
            callback: La fonction précédemment enregistrée
        
        Returns:
            True si le callback a été trouvé et supprimé
        """
        if isinstance(event_type, EventType):
            event_type = event_type.name
        
        if event_type in self._subscribers:
            try:
                self._subscribers[event_type].remove(callback)
                return True
            except ValueError:
                return False
        return False
    
    def emit(self, event_type: str, data: Optional[Dict[str, Any]] = None, 
             source_module: Optional[str] = None) -> None:
        """
        Émettre un événement.
        
        Args:
            event_type: Type d'événement
            data: Données associées à l'événement
            source_module: Nom du module émetteur (optionnel)
        
        Example:
            canopy_events.emit('SNAP_CIRCLE_PRIMARY_PLACED', {
                'location': Vector((1, 2, 3)),
                'object': some_object,
                'element_type': 'VERTEX'
            }, source_module='snap_circle')
        """
        import time
        
        if isinstance(event_type, EventType):
            event_type = event_type.name
        
        if data is None:
            data = {}
        
        event = Event(
            event_type=event_type,
            data=data,
            source_module=source_module,
            timestamp=time.time()
        )
        
        # Gérer les émissions pendant une émission (éviter récursion infinie)
        if self._is_emitting:
            self._pending_events.append(event)
            return
        
        self._is_emitting = True
        
        try:
            self._process_event(event)
            
            # Traiter les événements en attente
            while self._pending_events:
                pending = self._pending_events.pop(0)
                self._process_event(pending)
        finally:
            self._is_emitting = False
    
    def _process_event(self, event: Event) -> None:
        """Traite un événement et notifie les abonnés"""
        # Ajouter à l'historique
        self._history.append(event)
        if len(self._history) > self._max_history_size:
            self._history.pop(0)
        
        # Notifier les abonnés
        if event.event_type in self._subscribers:
            for callback in self._subscribers[event.event_type]:
                try:
                    callback(event.data)
                except Exception as e:
                    print(f"[CANOPY Events] Erreur dans callback pour {event.event_type}: {e}")
    
    def clear_subscribers(self, event_type: Optional[str] = None) -> None:
        """
        Supprime tous les abonnés pour un type d'événement ou tous.
        
        Args:
            event_type: Si fourni, ne supprime que pour ce type
        """
        if event_type:
            if isinstance(event_type, EventType):
                event_type = event_type.name
            if event_type in self._subscribers:
                self._subscribers[event_type].clear()
        else:
            self._subscribers.clear()
    
    def get_history(self, event_type: Optional[str] = None, limit: int = 10) -> List[Event]:
        """
        Récupère l'historique des événements.
        
        Args:
            event_type: Filtrer par type (optionnel)
            limit: Nombre maximum d'événements à retourner
        
        Returns:
            Liste des derniers événements
        """
        if event_type:
            if isinstance(event_type, EventType):
                event_type = event_type.name
            filtered = [e for e in self._history if e.event_type == event_type]
            return filtered[-limit:]
        return self._history[-limit:]
    
    def get_subscriber_count(self, event_type: str) -> int:
        """Retourne le nombre d'abonnés pour un type d'événement"""
        if isinstance(event_type, EventType):
            event_type = event_type.name
        return len(self._subscribers.get(event_type, []))


# ══════════════════════════════════════════════════════════════════════════════
# INSTANCE SINGLETON
# ══════════════════════════════════════════════════════════════════════════════

# Instance globale unique - à importer dans les autres modules
canopy_events = EventManager()


# ══════════════════════════════════════════════════════════════════════════════
# DÉCORATEUR POUR ABONNEMENT FACILE
# ══════════════════════════════════════════════════════════════════════════════

def on_event(event_type: str):
    """
    Décorateur pour s'abonner facilement à un événement.
    
    Usage:
        @on_event('SNAP_CIRCLE_PRIMARY_PLACED')
        def handle_circle_placed(data):
            print(f"Cercle placé à {data['location']}")
    """
    def decorator(func: Callable):
        canopy_events.subscribe(event_type, func)
        return func
    return decorator
