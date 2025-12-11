# ══════════════════════════════════════════════════════════════════════════════
# CANOPY V2 - Snap Circle - Système d'Animations
# Animations pédagogiques : rebond, déplacement, survol
# ══════════════════════════════════════════════════════════════════════════════

import bpy
import gpu
from gpu_extras.batch import batch_for_shader
import math
import time
from mathutils import Vector, Matrix
from typing import Optional, Tuple, List
from dataclasses import dataclass, field
from enum import Enum, auto

# ══════════════════════════════════════════════════════════════════════════════
# IMPORTS CANOPY (compatible standalone et intégré)
# ══════════════════════════════════════════════════════════════════════════════

import sys
from pathlib import Path

_CURRENT_DIR = Path(__file__).parent.resolve()

def _get_parent():
    """Trouve le module parent (__init__.py)"""
    for name, module in sys.modules.items():
        if hasattr(module, '__file__') and module.__file__:
            if Path(module.__file__).resolve() == _CURRENT_DIR / "__init__.py":
                return module
    return None

# Essayer d'importer depuis canopy.core, sinon depuis le parent
try:
    from canopy.core import canopy_state, redraw_viewport
except ImportError:
    _parent = _get_parent()
    if _parent:
        canopy_state = _parent.canopy_state
        redraw_viewport = _parent.redraw_viewport
    else:
        # Fallback minimal
        class _MockSnapCircle:
            is_active = False
            primary_location = None
            secondary_location = None
            primary_object = None
            secondary_object = None
            _primary_bounce_scale = 1.0
            _secondary_bounce_scale = 1.0
        class _MockState:
            snap_circle = _MockSnapCircle()
        canopy_state = _MockState()
        def redraw_viewport():
            try:
                for area in bpy.context.screen.areas:
                    if area.type == 'VIEW_3D':
                        area.tag_redraw()
            except:
                pass


# ══════════════════════════════════════════════════════════════════════════════
# CONSTANTES
# ══════════════════════════════════════════════════════════════════════════════

# Durées en secondes
BOUNCE_DURATION = 0.3
MOVE_DURATION = 0.25
LINE_DRAW_DURATION = 0.15
LINE_HOLD_DURATION = 0.08
LINE_ERASE_DURATION = 0.15
ROTATION_PHASE_DURATION = 0.2

# Visuel
LINE_WIDTH = 2.5
BOUNCE_SCALE_MAX = 1.4
BOUNCE_SCALE_MIN = 0.85

# Décalage pour animation secondaire (éviter croisement)
SECONDARY_DELAY = 0.04


# ══════════════════════════════════════════════════════════════════════════════
# FONCTIONS UTILITAIRES
# ══════════════════════════════════════════════════════════════════════════════

def is_animation_enabled() -> bool:
    """Vérifie si les animations sont activées - BYPASS CENTRAL"""
    try:
        return bpy.context.scene.snap_circle_props.show_animations
    except:
        return True  # Par défaut activé

def get_animation_color() -> Tuple[float, float, float, float]:
    """Récupère la couleur des animations"""
    try:
        c = bpy.context.scene.snap_circle_props.animation_color
        return (c[0], c[1], c[2], c[3])
    except:
        return (0.75, 0.75, 0.75, 0.9)


# ══════════════════════════════════════════════════════════════════════════════
# FONCTIONS D'INTERPOLATION (EASING)
# ══════════════════════════════════════════════════════════════════════════════

def ease_out_elastic(t: float) -> float:
    """Rebond élastique - pour le placement"""
    if t <= 0: return 0
    if t >= 1: return 1
    p = 0.4
    return pow(2, -10 * t) * math.sin((t - p/4) * (2 * math.pi) / p) + 1

def ease_out_quad(t: float) -> float:
    """Sortie douce"""
    return 1 - (1 - t) * (1 - t)

def ease_in_quad(t: float) -> float:
    """Entrée douce"""
    return t * t

def ease_in_out_quad(t: float) -> float:
    """Entrée et sortie douces"""
    return 2 * t * t if t < 0.5 else 1 - pow(-2 * t + 2, 2) / 2

def ease_out_back(t: float) -> float:
    """Dépassement léger puis retour"""
    c1 = 1.70158
    c3 = c1 + 1
    return 1 + c3 * pow(t - 1, 3) + c1 * pow(t - 1, 2)


# ══════════════════════════════════════════════════════════════════════════════
# CLASSES D'ANIMATION
# ══════════════════════════════════════════════════════════════════════════════

@dataclass
class Animation:
    """Classe de base pour les animations"""
    start_time: float = field(default_factory=time.time)
    duration: float = 1.0
    is_complete: bool = False
    is_preview: bool = False
    
    def get_progress(self) -> float:
        """Retourne la progression [0, 1]"""
        elapsed = time.time() - self.start_time
        t = min(1.0, elapsed / self.duration) if self.duration > 0 else 1.0
        if t >= 1.0:
            self.is_complete = True
        return t
    
    def cancel(self):
        """Annule l'animation"""
        self.is_complete = True


@dataclass
class BounceAnimation(Animation):
    """Animation de rebond au placement d'un cercle"""
    is_primary: bool = True
    
    def __post_init__(self):
        self.duration = BOUNCE_DURATION
    
    def get_scale(self) -> float:
        """Retourne le facteur d'échelle actuel"""
        t = self.get_progress()
        
        # Phase 1: Grossissement rapide (0 -> 0.2)
        if t < 0.2:
            return 1.0 + (BOUNCE_SCALE_MAX - 1.0) * ease_out_quad(t / 0.2)
        
        # Phase 2: Rebond élastique (0.2 -> 1.0)
        sub_t = (t - 0.2) / 0.8
        overshoot = BOUNCE_SCALE_MAX - 1.0
        return 1.0 + overshoot * (1.0 - ease_out_elastic(sub_t))


@dataclass
class CircleMoveAnimation(Animation):
    """Animation de déplacement d'un cercle (avec évitement)"""
    start_pos: Vector = field(default_factory=lambda: Vector((0, 0, 0)))
    end_pos: Vector = field(default_factory=lambda: Vector((0, 0, 0)))
    other_start: Optional[Vector] = None  # Position de l'autre cercle (pour évitement)
    other_end: Optional[Vector] = None
    is_primary: bool = True
    delay: float = 0.0  # Décalage au démarrage
    
    def __post_init__(self):
        self.duration = MOVE_DURATION + self.delay
    
    def get_current_position(self) -> Tuple[Vector, float]:
        """Retourne (position actuelle, scale)"""
        elapsed = time.time() - self.start_time
        
        # Appliquer le délai
        if elapsed < self.delay:
            return (self.start_pos.copy(), 1.0)
        
        t = min(1.0, (elapsed - self.delay) / MOVE_DURATION) if MOVE_DURATION > 0 else 1.0
        if t >= 1.0:
            self.is_complete = True
        
        eased_t = ease_out_back(t)
        
        # Calcul de la position avec courbe d'évitement
        if self.other_start is not None and self.other_end is not None:
            # Calculer le point de contrôle pour la courbe de Bézier
            mid = (self.start_pos + self.end_pos) / 2
            
            # Direction perpendiculaire pour l'évitement
            direction = self.end_pos - self.start_pos
            perp = Vector((-direction.y, direction.x, direction.z)).normalized()
            
            # Décaler le point de contrôle
            offset = direction.length * 0.3
            if self.is_primary:
                control = mid + perp * offset
            else:
                control = mid - perp * offset
            
            # Interpolation quadratique de Bézier
            inv_t = 1 - eased_t
            pos = (inv_t * inv_t * self.start_pos + 
                   2 * inv_t * eased_t * control + 
                   eased_t * eased_t * self.end_pos)
        else:
            # Interpolation linéaire simple
            pos = self.start_pos.lerp(self.end_pos, eased_t)
        
        # Petit effet de scale pendant le mouvement
        scale = 1.0 + 0.1 * math.sin(t * math.pi)
        
        return (pos, scale)


@dataclass
class LineDrawAnimation(Animation):
    """Animation de ligne: tracé → maintien → effacement"""
    start_point: Vector = field(default_factory=lambda: Vector((0, 0, 0)))
    end_point: Vector = field(default_factory=lambda: Vector((0, 0, 0)))
    erase_from_start: bool = True
    
    def __post_init__(self):
        self.duration = LINE_DRAW_DURATION + LINE_HOLD_DURATION + LINE_ERASE_DURATION
    
    def get_segment(self) -> Tuple[Vector, Vector, float]:
        """Retourne (début visible, fin visible, opacité)"""
        elapsed = time.time() - self.start_time
        
        # Phase 1: Tracé
        if elapsed < LINE_DRAW_DURATION:
            t = ease_out_quad(elapsed / LINE_DRAW_DURATION)
            visible_end = self.start_point.lerp(self.end_point, t)
            return (self.start_point.copy(), visible_end, 1.0)
        
        # Phase 2: Maintien
        elif elapsed < LINE_DRAW_DURATION + LINE_HOLD_DURATION:
            return (self.start_point.copy(), self.end_point.copy(), 1.0)
        
        # Phase 3: Effacement
        elif elapsed < self.duration:
            t = ease_in_quad((elapsed - LINE_DRAW_DURATION - LINE_HOLD_DURATION) / LINE_ERASE_DURATION)
            if self.erase_from_start:
                visible_start = self.start_point.lerp(self.end_point, t)
                return (visible_start, self.end_point.copy(), 1.0 - t * 0.4)
            else:
                visible_end = self.end_point.lerp(self.start_point, t)
                return (self.start_point.copy(), visible_end, 1.0 - t * 0.4)
        
        self.is_complete = True
        return (self.end_point.copy(), self.end_point.copy(), 0.0)


@dataclass
class RotationPreviewAnimation(Animation):
    """Animation de rotation: tracé → rotation porte → effacement"""
    pivot: Vector = field(default_factory=lambda: Vector((0, 0, 0)))
    start_point: Vector = field(default_factory=lambda: Vector((0, 0, 0)))
    target_point: Vector = field(default_factory=lambda: Vector((0, 0, 0)))
    
    # Calculés dans __post_init__
    _radius: float = 0.0
    _angle: float = 0.0
    _axis: Vector = field(default_factory=lambda: Vector((0, 0, 1)))
    
    def __post_init__(self):
        self.duration = LINE_DRAW_DURATION + ROTATION_PHASE_DURATION + LINE_ERASE_DURATION
        
        # Calculer les paramètres de rotation
        self._radius = (self.start_point - self.pivot).length
        
        vec_start = (self.start_point - self.pivot).normalized()
        vec_target = (self.target_point - self.pivot).normalized()
        
        if vec_start.length > 0.001 and vec_target.length > 0.001:
            dot = max(-1.0, min(1.0, vec_start.dot(vec_target)))
            self._angle = math.acos(dot)
            
            self._axis = vec_start.cross(vec_target)
            if self._axis.length < 0.001:
                self._axis = Vector((0, 0, 1))
            else:
                self._axis.normalize()
    
    def get_segment(self) -> Tuple[Vector, Vector, float]:
        """Retourne le segment de ligne actuel"""
        elapsed = time.time() - self.start_time
        direction = (self.start_point - self.pivot)
        if direction.length > 0.001:
            direction = direction.normalized()
        
        # Phase 1: Tracé de la ligne (du pivot vers l'extérieur)
        if elapsed < LINE_DRAW_DURATION:
            t = ease_out_quad(elapsed / LINE_DRAW_DURATION)
            end = self.pivot + direction * self._radius * t
            return (self.pivot.copy(), end, 1.0)
        
        # Phase 2: Rotation (comme une porte)
        elif elapsed < LINE_DRAW_DURATION + ROTATION_PHASE_DURATION:
            rt = (elapsed - LINE_DRAW_DURATION) / ROTATION_PHASE_DURATION
            current_angle = self._angle * ease_in_out_quad(rt)
            
            rot_matrix = Matrix.Rotation(current_angle, 4, self._axis)
            rotated_offset = rot_matrix @ (self.start_point - self.pivot)
            end = self.pivot + rotated_offset
            
            return (self.pivot.copy(), end, 1.0)
        
        # Phase 3: Effacement (du pivot vers l'extérieur)
        elif elapsed < self.duration:
            et = (elapsed - LINE_DRAW_DURATION - ROTATION_PHASE_DURATION) / LINE_ERASE_DURATION
            t = ease_in_quad(et)
            
            # Position finale après rotation
            rot_matrix = Matrix.Rotation(self._angle, 4, self._axis)
            final_offset = rot_matrix @ (self.start_point - self.pivot)
            final_end = self.pivot + final_offset
            
            # Effacement progressif
            visible_start = self.pivot.lerp(final_end, t)
            return (visible_start, final_end, 1.0 - t * 0.5)
        
        self.is_complete = True
        return (self.pivot.copy(), self.pivot.copy(), 0.0)


@dataclass
class EdgeRotationPreviewAnimation(Animation):
    """Animation de rotation d'arête autour de son centre"""
    edge_center: Vector = field(default_factory=lambda: Vector((0, 0, 0)))
    start_direction: Vector = field(default_factory=lambda: Vector((1, 0, 0)))
    target_direction: Vector = field(default_factory=lambda: Vector((0, 1, 0)))
    edge_length: float = 1.0
    
    def __post_init__(self):
        self.duration = LINE_DRAW_DURATION + ROTATION_PHASE_DURATION + LINE_ERASE_DURATION
        # Normaliser les directions
        if self.start_direction.length > 0.001:
            self.start_direction = self.start_direction.normalized()
        if self.target_direction.length > 0.001:
            self.target_direction = self.target_direction.normalized()
    
    def get_segment(self) -> Tuple[Vector, Vector, float]:
        """Retourne le segment visible"""
        elapsed = time.time() - self.start_time
        half = self.edge_length / 2
        
        # Phase 1: Tracé (du centre vers les extrémités)
        if elapsed < LINE_DRAW_DURATION:
            t = ease_out_quad(elapsed / LINE_DRAW_DURATION)
            current_half = half * t
            start = self.edge_center - self.start_direction * current_half
            end = self.edge_center + self.start_direction * current_half
            return (start, end, 1.0)
        
        # Phase 2: Rotation
        elif elapsed < LINE_DRAW_DURATION + ROTATION_PHASE_DURATION:
            rt = (elapsed - LINE_DRAW_DURATION) / ROTATION_PHASE_DURATION
            current_dir = self.start_direction.lerp(self.target_direction, ease_in_out_quad(rt))
            if current_dir.length > 0.001:
                current_dir = current_dir.normalized()
            start = self.edge_center - current_dir * half
            end = self.edge_center + current_dir * half
            return (start, end, 1.0)
        
        # Phase 3: Effacement (des extrémités vers le centre)
        elif elapsed < self.duration:
            et = (elapsed - LINE_DRAW_DURATION - ROTATION_PHASE_DURATION) / LINE_ERASE_DURATION
            t = ease_in_quad(et)
            current_half = half * (1.0 - t)
            start = self.edge_center - self.target_direction * current_half
            end = self.edge_center + self.target_direction * current_half
            return (start, end, 1.0 - t * 0.5)
        
        self.is_complete = True
        return (self.edge_center.copy(), self.edge_center.copy(), 0.0)


# ══════════════════════════════════════════════════════════════════════════════
# GESTIONNAIRE D'ANIMATIONS (SINGLETON)
# ══════════════════════════════════════════════════════════════════════════════

class AnimationManager:
    """Gestionnaire centralisé des animations"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._animations: List[Animation] = []
            cls._instance._preview: Optional[Animation] = None
            cls._instance._timer = None
            cls._instance._initialized = False
        return cls._instance
    
    @classmethod
    def get(cls) -> 'AnimationManager':
        """Retourne l'instance singleton"""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    def add(self, anim: Animation):
        """Ajoute une animation"""
        if not is_animation_enabled():
            return
        self._animations.append(anim)
        self._ensure_timer()
    
    def set_preview(self, anim: Optional[Animation]):
        """Définit l'animation de prévisualisation (survol)"""
        if not is_animation_enabled():
            return
        
        # Annuler la preview précédente
        if self._preview:
            self._preview.cancel()
        
        self._preview = anim
        if anim:
            anim.is_preview = True
            self._ensure_timer()
        redraw_viewport()
    
    def cancel_preview(self):
        """Annule la prévisualisation en cours"""
        if self._preview:
            self._preview.cancel()
            self._preview = None
            redraw_viewport()
    
    def clear(self):
        """Efface toutes les animations"""
        for a in self._animations:
            a.cancel()
        self._animations.clear()
        self.cancel_preview()
        
        # Réinitialiser les positions de dessin animées
        try:
            state = canopy_state.snap_circle
            state._primary_draw_pos = None
            state._secondary_draw_pos = None
            state._primary_bounce_scale = 1.0
            state._secondary_bounce_scale = 1.0
        except:
            pass
    
    def _ensure_timer(self):
        """Lance le timer si nécessaire"""
        if self._timer is None:
            try:
                self._timer = bpy.app.timers.register(
                    self._tick, 
                    first_interval=0.016,
                    persistent=True
                )
            except:
                pass
    
    def _tick(self) -> Optional[float]:
        """Tick du timer (~60 FPS)"""
        # Bypass si désactivé
        if not is_animation_enabled():
            self.clear()
            self._timer = None
            return None
        
        # Nettoyer les animations terminées
        self._animations = [a for a in self._animations if not a.is_complete]
        
        # Vérifier la preview
        if self._preview and self._preview.is_complete:
            self._preview = None
        
        # Appliquer les animations au state
        state = canopy_state.snap_circle
        
        # Reset des positions de dessin (seront recalculées si animation active)
        state._primary_draw_pos = None
        state._secondary_draw_pos = None
        
        for anim in self._animations:
            if isinstance(anim, BounceAnimation):
                # Animation de rebond - modifier le scale
                scale = anim.get_scale()
                if anim.is_primary:
                    state._primary_bounce_scale = scale
                else:
                    state._secondary_bounce_scale = scale
            
            elif isinstance(anim, CircleMoveAnimation):
                # Animation de déplacement - modifier la position de dessin
                pos, scale = anim.get_current_position()
                if anim.is_primary:
                    state._primary_draw_pos = pos
                    state._primary_bounce_scale = scale
                else:
                    state._secondary_draw_pos = pos
                    state._secondary_bounce_scale = scale
        
        # Rafraîchir l'affichage
        redraw_viewport()
        
        # Continuer si des animations sont actives
        if self._animations or self._preview:
            return 0.016  # ~60 FPS
        
        self._timer = None
        return None
    
    def draw(self, context):
        """Dessine les animations (appelé par le renderer)"""
        if not is_animation_enabled():
            return
        
        color = get_animation_color()
        
        # Dessiner les animations de ligne
        for anim in self._animations:
            if hasattr(anim, 'get_segment'):
                self._draw_line_animation(anim, color)
        
        # Dessiner la preview
        if self._preview and hasattr(self._preview, 'get_segment'):
            self._draw_line_animation(self._preview, color)
    
    def _draw_line_animation(self, anim, base_color):
        """Dessine une animation de type ligne"""
        start, end, opacity = anim.get_segment()
        
        # Ne pas dessiner si trop court ou invisible
        if (end - start).length < 0.001 or opacity < 0.01:
            return
        
        color = (base_color[0], base_color[1], base_color[2], base_color[3] * opacity)
        
        # Dessiner la ligne
        shader = gpu.shader.from_builtin('UNIFORM_COLOR')
        batch = batch_for_shader(shader, 'LINES', {"pos": [start[:], end[:]]})
        
        gpu.state.blend_set('ALPHA')
        gpu.state.line_width_set(LINE_WIDTH)
        
        shader.bind()
        shader.uniform_float("color", color)
        batch.draw(shader)
        
        gpu.state.line_width_set(1.0)
        gpu.state.blend_set('NONE')
        
        # Dessiner un point au pivot pour les rotations
        if isinstance(anim, RotationPreviewAnimation):
            self._draw_point(anim.pivot, color)
        elif isinstance(anim, EdgeRotationPreviewAnimation):
            self._draw_point(anim.edge_center, color)
    
    def _draw_point(self, position: Vector, color: Tuple):
        """Dessine un point"""
        shader = gpu.shader.from_builtin('UNIFORM_COLOR')
        batch = batch_for_shader(shader, 'POINTS', {"pos": [position[:]]})
        
        gpu.state.blend_set('ALPHA')
        gpu.state.point_size_set(8.0)
        
        shader.bind()
        shader.uniform_float("color", color)
        batch.draw(shader)
        
        gpu.state.point_size_set(1.0)
        gpu.state.blend_set('NONE')


# ══════════════════════════════════════════════════════════════════════════════
# API PUBLIQUE - Fonctions simples à appeler
# ══════════════════════════════════════════════════════════════════════════════

def create_bounce(is_primary: bool = True):
    """Crée une animation de rebond"""
    if not is_animation_enabled():
        return
    anim = BounceAnimation(is_primary=is_primary)
    AnimationManager.get().add(anim)

def create_move_animation(start: Vector, end: Vector, is_primary: bool, 
                          other_start: Vector = None, other_end: Vector = None,
                          delay: float = 0.0):
    """Crée une animation de déplacement de cercle"""
    if not is_animation_enabled():
        return
    anim = CircleMoveAnimation(
        start_pos=start.copy(),
        end_pos=end.copy(),
        other_start=other_start.copy() if other_start else None,
        other_end=other_end.copy() if other_end else None,
        is_primary=is_primary,
        delay=delay
    )
    AnimationManager.get().add(anim)

def create_swap_animations(pos_a: Vector, pos_b: Vector):
    """Crée les animations pour un swap (les cercles s'évitent)"""
    if not is_animation_enabled():
        return
    
    # Animation du cercle principal (sans délai)
    create_move_animation(
        pos_a, pos_b, 
        is_primary=True,
        other_start=pos_b, 
        other_end=pos_a
    )
    
    # Animation du cercle secondaire (avec délai)
    create_move_animation(
        pos_b, pos_a,
        is_primary=False,
        other_start=pos_a,
        other_end=pos_b,
        delay=SECONDARY_DELAY
    )

def preview_line(start: Vector, end: Vector, erase_from_start: bool = True):
    """Prévisualise une ligne (survol bouton déplacement)"""
    if not is_animation_enabled():
        return
    anim = LineDrawAnimation(
        start_point=start.copy(),
        end_point=end.copy(),
        erase_from_start=erase_from_start
    )
    AnimationManager.get().set_preview(anim)

def preview_rotation(pivot: Vector, start: Vector, target: Vector):
    """Prévisualise une rotation (survol bouton rotation)"""
    if not is_animation_enabled():
        return
    anim = RotationPreviewAnimation(
        pivot=pivot.copy(),
        start_point=start.copy(),
        target_point=target.copy()
    )
    AnimationManager.get().set_preview(anim)

def preview_edge_rotation(center: Vector, start_dir: Vector, target_dir: Vector, length: float):
    """Prévisualise une rotation d'arête"""
    if not is_animation_enabled():
        return
    anim = EdgeRotationPreviewAnimation(
        edge_center=center.copy(),
        start_direction=start_dir.copy(),
        target_direction=target_dir.copy(),
        edge_length=length
    )
    AnimationManager.get().set_preview(anim)

def cancel_preview():
    """Annule la prévisualisation en cours"""
    AnimationManager.get().cancel_preview()


# ══════════════════════════════════════════════════════════════════════════════
# INITIALISATION / NETTOYAGE
# ══════════════════════════════════════════════════════════════════════════════

def initialize():
    """Initialise le système d'animations"""
    mgr = AnimationManager.get()
    mgr._initialized = True
    print("[Snap Circle] Système d'animations initialisé")

def cleanup():
    """Nettoie le système"""
    mgr = AnimationManager.get()
    mgr.clear()
    
    if mgr._timer:
        try:
            bpy.app.timers.unregister(mgr._timer)
        except:
            pass
        mgr._timer = None
    
    mgr._initialized = False


# Fonctions legacy (pour compatibilité)
def start_hover_monitor():
    """Obsolète - gardé pour compatibilité"""
    pass

def stop_hover_monitor():
    """Obsolète - gardé pour compatibilité"""
    pass
