"""
Layout Conflict Detector
========================

This utility monitors for layout conflicts in the SNID SAGE GUI and provides
warnings when multiple systems attempt to modify the same widget properties.

Features:
- Real-time conflict detection
- Detailed logging of conflicts
- Prevention of duplicate layout applications
- Performance monitoring for layout operations

Developed by Fiorenzo Stoppa for SNID SAGE
"""

import logging
import time
from typing import Dict, Set, Optional, Any, List
from dataclasses import dataclass
from PySide6 import QtWidgets

# Import logging
try:
    from snid_sage.shared.utils.logging import get_logger
    _LOGGER = get_logger('gui.conflict_detector')
except ImportError:
    import logging
    _LOGGER = logging.getLogger('gui.conflict_detector')


@dataclass
class LayoutOperation:
    """Represents a layout operation"""
    widget_id: str
    operation: str
    value: Any
    timestamp: float
    source: str


class LayoutConflictDetector:
    """
    Detects and logs layout conflicts in real-time
    """
    
    def __init__(self):
        self.applied_operations: Dict[str, List[LayoutOperation]] = {}
        self.widget_registry: Dict[str, QtWidgets.QWidget] = {}
        self.conflict_count = 0
        self.operation_count = 0
        
        _LOGGER.info("Layout conflict detector initialized")
    
    def register_widget(self, widget: QtWidgets.QWidget, widget_id: str):
        """Register a widget for conflict monitoring"""
        self.widget_registry[widget_id] = widget
        _LOGGER.debug(f"Registered widget for monitoring: {widget_id}")
    
    def log_operation(self, widget_id: str, operation: str, value: Any, source: str = "unknown"):
        """Log a layout operation and check for conflicts"""
        current_time = time.time()
        operation_obj = LayoutOperation(widget_id, operation, value, current_time, source)
        
        # Create key for this specific operation type on this widget
        operation_key = f"{widget_id}:{operation}"
        
        # Initialize list if not exists
        if operation_key not in self.applied_operations:
            self.applied_operations[operation_key] = []
        
        # Check for conflicts (same operation applied multiple times)
        existing_operations = self.applied_operations[operation_key]
        if existing_operations:
            last_operation = existing_operations[-1]
            time_diff = current_time - last_operation.timestamp
            
            
            if time_diff < 1.0 and last_operation.value != value:
                self.conflict_count += 1
                _LOGGER.warning(
                    f"LAYOUT CONFLICT #{self.conflict_count}: "
                    f"Widget '{widget_id}' operation '{operation}' "
                    f"changed from {last_operation.value} to {value} "
                    f"within {time_diff:.3f}s "
                    f"(previous source: {last_operation.source}, current source: {source})"
                )
                
                # Log stack trace for debugging
                import traceback
                _LOGGER.debug("Conflict stack trace:", exc_info=True)
        
        # Add the operation to history
        self.applied_operations[operation_key].append(operation_obj)
        self.operation_count += 1
        
        # Keep only recent operations (last 10 per operation type)
        if len(self.applied_operations[operation_key]) > 10:
            self.applied_operations[operation_key] = self.applied_operations[operation_key][-10:]
    
    def check_widget_consistency(self, widget_id: str) -> bool:
        """Check if a widget's current state is consistent with logged operations"""
        if widget_id not in self.widget_registry:
            _LOGGER.warning(f"Cannot check consistency for unregistered widget: {widget_id}")
            return False
        
        widget = self.widget_registry[widget_id]
        consistent = True
        
        # Check common size operations
        size_operations = [
            ('setFixedWidth', lambda w: w.width()),
            ('setFixedHeight', lambda w: w.height()),
            ('setMinimumSize', lambda w: (w.minimumWidth(), w.minimumHeight())),
            ('setMaximumSize', lambda w: (w.maximumWidth(), w.maximumHeight()))
        ]
        
        for operation, getter in size_operations:
            operation_key = f"{widget_id}:{operation}"
            if operation_key in self.applied_operations:
                operations = self.applied_operations[operation_key]
                if operations:
                    last_operation = operations[-1]
                    try:
                        current_value = getter(widget)
                        expected_value = last_operation.value
                        
                        if current_value != expected_value:
                            _LOGGER.warning(
                                f"Inconsistent state for {widget_id}.{operation}: "
                                f"expected {expected_value}, got {current_value}"
                            )
                            consistent = False
                    except Exception as e:
                        _LOGGER.debug(f"Could not check {operation} for {widget_id}: {e}")
        
        return consistent
    
    def get_conflict_summary(self) -> Dict[str, Any]:
        """Get summary of detected conflicts"""
        return {
            'total_conflicts': self.conflict_count,
            'total_operations': self.operation_count,
            'widgets_monitored': len(self.widget_registry),
            'operation_types': len(self.applied_operations),
            'conflict_rate': self.conflict_count / max(1, self.operation_count) * 100
        }
    
    def reset_monitoring(self):
        """Reset all monitoring data"""
        self.applied_operations.clear()
        self.widget_registry.clear()
        self.conflict_count = 0
        self.operation_count = 0
        _LOGGER.info("Layout conflict monitoring reset")


# Global instance
_conflict_detector = None


def get_conflict_detector() -> LayoutConflictDetector:
    """Get the global conflict detector instance"""
    global _conflict_detector
    if _conflict_detector is None:
        _conflict_detector = LayoutConflictDetector()
    return _conflict_detector


def monitor_widget_operation(widget: QtWidgets.QWidget, widget_id: str, 
                           operation: str, value: Any, source: str = "unknown"):
    """
    Monitor a widget operation for conflicts
    
    Args:
        widget: The widget being modified
        widget_id: Unique identifier for the widget
        operation: The operation being performed (e.g., 'setFixedWidth')
        value: The value being set
        source: Source of the operation (e.g., 'UnifiedLayoutManager')
    """
    detector = get_conflict_detector()
    detector.register_widget(widget, widget_id)
    detector.log_operation(widget_id, operation, value, source)


def check_layout_consistency(widget_id: str) -> bool:
    """Check if a widget's layout is consistent"""
    detector = get_conflict_detector()
    return detector.check_widget_consistency(widget_id)


def get_layout_conflict_summary() -> Dict[str, Any]:
    """Get summary of layout conflicts"""
    detector = get_conflict_detector()
    return detector.get_conflict_summary()


def reset_conflict_monitoring():
    """Reset conflict monitoring"""
    detector = get_conflict_detector()
    detector.reset_monitoring()


# Decorator for monitoring layout operations
def monitor_layout_operation(source: str = "unknown"):
    """
    Decorator to automatically monitor layout operations
    
    Usage:
        @monitor_layout_operation("MyLayoutManager")
        def apply_widget_size(self, widget, size):
            widget.setFixedSize(*size)
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            # Try to extract widget and operation info
            result = func(*args, **kwargs)
            
            # Log the operation if we can identify the widget
            if len(args) >= 2 and hasattr(args[1], 'objectName'):
                widget = args[1]
                widget_id = widget.objectName() or f"widget_{id(widget)}"
                operation = func.__name__
                
                # Try to extract value from args/kwargs
                value = args[2] if len(args) > 2 else kwargs.get('value', 'unknown')
                
                monitor_widget_operation(widget, widget_id, operation, value, source)
            
            return result
        return wrapper
    return decorator 