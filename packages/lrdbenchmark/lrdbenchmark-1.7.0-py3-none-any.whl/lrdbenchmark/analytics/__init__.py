"""
Analytics Package for LRDBench

This package provides comprehensive usage tracking and analytics capabilities
for monitoring how LRDBench is used in production environments.
"""

# Import analytics components with error handling
try:
    from .usage_tracker import UsageTracker
    from .performance_monitor import PerformanceMonitor
    from .error_analyzer import ErrorAnalyzer
    from .workflow_analyzer import WorkflowAnalyzer
    from .dashboard import AnalyticsDashboard
except ImportError:
    # Placeholder classes for modules that don't exist yet
    class UsageTracker:
        def __init__(self, *args, **kwargs):
            raise ImportError("UsageTracker not available - module not found")
    
    class PerformanceMonitor:
        def __init__(self, *args, **kwargs):
            raise ImportError("PerformanceMonitor not available - module not found")
    
    class ErrorAnalyzer:
        def __init__(self, *args, **kwargs):
            raise ImportError("ErrorAnalyzer not available - module not found")
    
    class WorkflowAnalyzer:
        def __init__(self, *args, **kwargs):
            raise ImportError("WorkflowAnalyzer not available - module not found")
    
    class AnalyticsDashboard:
        def __init__(self, *args, **kwargs):
            raise ImportError("AnalyticsDashboard not available - module not found")

__all__ = [
    "UsageTracker",
    "PerformanceMonitor",
    "ErrorAnalyzer",
    "WorkflowAnalyzer",
    "AnalyticsDashboard",
]
