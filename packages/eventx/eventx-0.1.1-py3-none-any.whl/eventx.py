"""
EventX - Event-driven messaging via exceptions
Ultra-lightweight event system for Python

Version: 0.1.1 (Refactored & Stabilized)
Author: Anzize Daouda (Tryboy869)
Contact: nexusstudio100@gmail.com
Powered by Nexus Studio
"""

__version__ = "0.1.1"
__author__ = "Anzize Daouda"
__email__ = "nexusstudio100@gmail.com"
__title__ = "EventX"
__description__ = "Event-driven messaging via exceptions - Ultra-lightweight event system"
__url__ = "https://github.com/Tryboy869/eventx"

import threading
import time
import traceback
import weakref
from typing import Any, Callable, Dict, List, Optional, Set
from collections import defaultdict


class EventXError(Exception):
    """Base exception pour EventX"""
    pass


class Event(Exception):
    """
    Exception utilisée comme événement
    
    Hérite d'Exception pour être 'raise'-able tout en portant des données
    Distingue clairement les events des vraies erreurs via l'attribut is_event
    """
    
    def __init__(self, name: str, data: Any = None, **metadata):
        if not isinstance(name, str) or not name.strip():
            raise EventXError("Event name must be a non-empty string")
        
        super().__init__(f"Event: {name}")
        self.name = name.strip()
        self.data = data
        self.metadata = metadata or {}
        self.timestamp = time.time()
        self.handled = False
        self.is_event = True  # Flag critique pour distinction
        self.handlers_called = 0
        self.source_info = self._capture_source()
    
    def _capture_source(self) -> str:
        """Capture info source pour debugging"""
        try:
            stack = traceback.extract_stack()
            # Remonter la stack pour trouver l'appel utilisateur
            for frame in reversed(stack[:-2]):
                if 'eventx' not in frame.filename:
                    return f"{frame.filename.split('/')[-1]}:{frame.lineno}"
        except:
            pass
        return "unknown"
    
    def mark_handled(self):
        """Marque l'événement comme traité"""
        self.handled = True
        
    def increment_handler_count(self):
        """Incrémente le compteur de handlers"""
        self.handlers_called += 1
    
    def __repr__(self):
        return f"Event(name='{self.name}', data={repr(self.data)}, handlers_called={self.handlers_called})"
    
    def __str__(self):
        return f"Event '{self.name}' from {self.source_info}"


class EventBus:
    """
    Bus d'événements principal utilisant les exceptions comme transport
    
    Thread-safe, performant, avec gestion d'erreurs robuste
    """
    
    def __init__(self, name: str = "default", max_cascade: int = 100):
        if not isinstance(name, str) or not name.strip():
            raise EventXError("Bus name must be a non-empty string")
        
        self.name = name.strip()
        self.max_cascade = max_cascade
        self._handlers: Dict[str, List[Callable]] = defaultdict(list)
        self._wildcard_handlers: List[Callable] = []
        self._cascade_depth = 0
        self._processing = False
        
        # Thread safety
        self._lock = threading.RLock()
        
        # Statistics tracking
        self.stats = {
            "events_raised": 0,
            "handlers_executed": 0,
            "errors_caught": 0,
            "cascade_events": 0,
            "max_cascade_depth": 0
        }
        
        # Event history pour debugging (limite à 1000 derniers)
        self._event_history: List[Event] = []
        self._max_history = 1000
    
    def on(self, event_name: str, handler: Optional[Callable] = None):
        """
        Enregistre un handler pour un événement
        
        Usage comme décorateur:
        @bus.on("user_created")
        def handle_user(event): ...
        
        Usage direct:
        bus.on("user_created", lambda e: print(e.data))
        """
        if not isinstance(event_name, str) or not event_name.strip():
            raise EventXError("Event name must be a non-empty string")
        
        def decorator(func: Callable):
            if not callable(func):
                raise EventXError("Handler must be callable")
            
            with self._lock:
                self._handlers[event_name.strip()].append(func)
            return func
        
        if handler is not None:
            return decorator(handler)
        return decorator
    
    def on_any(self, handler: Callable):
        """
        Handler qui écoute TOUS les événements (wildcard)
        
        @bus.on_any
        def log_all_events(event): ...
        """
        if not callable(handler):
            raise EventXError("Handler must be callable")
        
        with self._lock:
            self._wildcard_handlers.append(handler)
        return handler
    
    def dispatch(self, func: Callable):
        """
        Exécute une fonction et capture les Events qu'elle raise
        
        Gère automatiquement les cascades et la propagation d'erreurs
        """
        if not callable(func):
            raise EventXError("Function must be callable")
        
        if self._processing:
            # Déjà en train de traiter - éviter récursion infinie
            return self._execute_function(func)
        
        self._processing = True
        self._cascade_depth = 0
        
        try:
            return self._execute_function(func)
        finally:
            self._processing = False
    
    def _execute_function(self, func: Callable):
        """Exécute une fonction et gère les exceptions/events"""
        try:
            return func()
        except Exception as error:
            if isinstance(error, Event) and hasattr(error, 'is_event'):
                # C'est un Event, pas une vraie erreur
                self.stats["events_raised"] += 1
                self._handle_event(error)
                return error
            else:
                # Vraie erreur - la re-raise
                self.stats["errors_caught"] += 1
                raise
    
    def _handle_event(self, event: Event):
        """
        Traite un événement et exécute tous ses handlers
        
        Gère les cascades et limite la profondeur pour éviter boucles infinies
        """
        if self._cascade_depth >= self.max_cascade:
            raise EventXError(
                f"Cascade depth exceeded ({self._cascade_depth} >= {self.max_cascade}) "
                f"for event '{event.name}'. Possible infinite loop detected."
            )
        
        # Tracking
        self._cascade_depth += 1
        self.stats["max_cascade_depth"] = max(self.stats["max_cascade_depth"], self._cascade_depth)
        
        # Historique pour debugging
        with self._lock:
            self._event_history.append(event)
            if len(self._event_history) > self._max_history:
                self._event_history.pop(0)
        
        # Exécution des handlers spécifiques
        specific_handlers = self._handlers.get(event.name, [])
        
        # Exécution des handlers wildcard
        all_handlers = specific_handlers + self._wildcard_handlers
        
        if not all_handlers:
            # Aucun handler - log pour debugging
            print(f"⚠️ No handlers for event '{event.name}'")
        
        for handler in all_handlers:
            try:
                handler(event)
                event.increment_handler_count()
                self.stats["handlers_executed"] += 1
                
            except Exception as handler_error:
                if isinstance(handler_error, Event) and hasattr(handler_error, 'is_event'):
                    # Handler a déclenché un nouvel event (cascade)
                    self.stats["cascade_events"] += 1
                    self._handle_event(handler_error)
                else:
                    # Erreur dans le handler
                    self.stats["errors_caught"] += 1
                    self._handle_handler_error(handler_error, event, handler)
        
        event.mark_handled()
        self._cascade_depth -= 1
    
    def _handle_handler_error(self, error: Exception, event: Event, handler: Callable):
        """Gère les erreurs dans les handlers sans casser le système"""
        handler_name = getattr(handler, '__name__', 'anonymous')
        error_msg = (
            f"Error in handler '{handler_name}' for event '{event.name}': {error}\n"
            f"Event source: {event.source_info}"
        )
        print(f"❌ {error_msg}")
        
        # Option : émettre un event d'erreur pour monitoring
        try:
            error_event = Event("handler_error", {
                "original_event": event.name,
                "handler_name": handler_name,
                "error_message": str(error),
                "error_type": type(error).__name__
            })
            # Éviter récursion infinie sur les erreurs
            if event.name != "handler_error":
                self._handle_event(error_event)
        except:
            pass  # Si même l'event d'erreur échoue, on abandonne silencieusement
    
    def emit(self, event_name: str, data: Any = None, **metadata):
        """
        Alternative fluide pour émettre un événement directement
        
        Usage: bus.emit("user_created", user_data)
        """
        event = Event(event_name, data, **metadata)
        self._handle_event(event)
        return self
    
    def remove_handler(self, event_name: str, handler: Callable):
        """Supprime un handler spécifique"""
        with self._lock:
            if event_name in self._handlers:
                try:
                    self._handlers[event_name].remove(handler)
                    if not self._handlers[event_name]:
                        del self._handlers[event_name]
                except ValueError:
                    pass  # Handler pas trouvé
    
    def clear_handlers(self, event_name: Optional[str] = None):
        """Supprime tous les handlers (ou pour un événement spécifique)"""
        with self._lock:
            if event_name:
                self._handlers.pop(event_name, None)
            else:
                self._handlers.clear()
                self._wildcard_handlers.clear()
    
    def get_stats(self) -> Dict[str, Any]:
        """Retourne une copie des statistiques"""
        with self._lock:
            return {
                **self.stats,
                "active_event_types": len(self._handlers),
                "total_handlers": sum(len(handlers) for handlers in self._handlers.values()),
                "wildcard_handlers": len(self._wildcard_handlers),
                "recent_events": len(self._event_history)
            }
    
    def get_event_history(self, limit: int = 10) -> List[Event]:
        """Retourne l'historique récent des événements"""
        with self._lock:
            return self._event_history[-limit:].copy()
    
    def get_registered_events(self) -> Set[str]:
        """Retourne la liste des types d'événements enregistrés"""
        with self._lock:
            return set(self._handlers.keys())
    
    def __repr__(self):
        return f"EventBus(name='{self.name}', handlers={len(self._handlers)}, stats={self.stats})"


# Instance globale pour usage simple
global_bus = EventBus("global")


# API de convenance pour usage global
def on(event_name: str):
    """Décorateur global utilisant le bus par défaut"""
    return global_bus.on(event_name)


def on_any(handler: Callable):
    """Handler global wildcard"""
    return global_bus.on_any(handler)


def dispatch(func: Callable):
    """Fonction globale de dispatch"""
    return global_bus.dispatch(func)


def emit(event_name: str, data: Any = None, **metadata):
    """Fonction globale d'émission"""
    return global_bus.emit(event_name, data, **metadata)


def clear_all():
    """Nettoie le bus global"""
    global_bus.clear_handlers()


def stats():
    """Stats du bus global"""
    return global_bus.get_stats()


# Exports publics
__all__ = [
    # Classes principales
    "Event",
    "EventBus",
    "EventXError",
    
    # Instance globale
    "global_bus",
    
    # API de convenance
    "on",
    "on_any", 
    "dispatch",
    "emit",
    "clear_all",
    "stats",
    
    # Métadonnées
    "__version__",
    "__author__",
    "__email__"
]


# Validation à l'import
def _validate_installation():
    """Valide que EventX fonctionne correctement à l'import"""
    try:
        # Test rapide de fonctionnement
        test_bus = EventBus("validation")
        test_event = Event("validation_test", "ok")
        
        worked = False
        
        @test_bus.on("validation_test")
        def validation_handler(event):
            nonlocal worked
            worked = (event.data == "ok")
        
        test_bus.dispatch(lambda: (_ for _ in ()).throw(test_event))
        
        if not worked:
            raise EventXError("EventX validation failed during import")
            
    except Exception as e:
        if not isinstance(e, Event):
            raise EventXError(f"EventX installation validation failed: {e}")


# Auto-validation à l'import (désactivable)
import os
if os.environ.get("EVENTX_SKIP_VALIDATION") != "1":
    _validate_installation()