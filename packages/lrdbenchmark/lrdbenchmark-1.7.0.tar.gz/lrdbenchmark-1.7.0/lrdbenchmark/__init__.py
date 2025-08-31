"""
LRDBench: Long-Range Dependence Benchmarking Toolkit

A comprehensive toolkit for benchmarking long-range dependence estimators
on synthetic and real-world time series data.
"""

__version__ = "1.6.1"
__author__ = "LRDBench Development Team"
__email__ = "lrdbench@example.com"

# Core components - using relative imports
try:
    from .analysis.benchmark import ComprehensiveBenchmark
    from .models.data_models import FBMModel, FGNModel, ARFIMAModel, MRWModel
except ImportError:
    # These modules may not exist yet, so we'll define placeholders
    ComprehensiveBenchmark = None
    FBMModel = None
    FGNModel = None
    ARFIMAModel = None
    MRWModel = None

# Machine Learning and Neural Network Estimators
try:
    from .analysis.machine_learning import (
        CNNEstimator,
        LSTMEstimator,
        GRUEstimator,
        TransformerEstimator,
        RandomForestEstimator,
        SVREstimator,
        GradientBoostingEstimator,
    )
except ImportError:
    # Placeholder values for modules that don't exist yet
    CNNEstimator = None
    LSTMEstimator = None
    GRUEstimator = None
    TransformerEstimator = None
    RandomForestEstimator = None
    SVREstimator = None
    GradientBoostingEstimator = None

# Analytics components
try:
    from .analytics import (
        UsageTracker,
        PerformanceMonitor,
        ErrorAnalyzer,
        WorkflowAnalyzer,
        AnalyticsDashboard,
    )
except ImportError:
    # Placeholder values for modules that don't exist yet
    UsageTracker = None
    PerformanceMonitor = None
    ErrorAnalyzer = None
    WorkflowAnalyzer = None
    AnalyticsDashboard = None

# Convenience functions
try:
    from .analytics.dashboard import quick_analytics_summary, get_analytics_dashboard
    from .analytics.usage_tracker import get_usage_tracker, track_usage
    from .analytics.performance_monitor import get_performance_monitor, monitor_performance
    from .analytics.error_analyzer import get_error_analyzer, track_errors
    from .analytics.workflow_analyzer import get_workflow_analyzer, track_workflow
except ImportError:
    # Placeholder functions for modules that don't exist yet
    def quick_analytics_summary(days=30):
        return f"Analytics summary for {days} days (module not available)"
    
    def get_analytics_dashboard():
        return None
    
    def get_usage_tracker():
        return None
    
    def track_usage():
        pass
    
    def get_performance_monitor():
        return None
    
    def monitor_performance():
        pass
    
    def get_error_analyzer():
        return None
    
    def track_errors():
        pass
    
    def get_workflow_analyzer():
        return None
    
    def track_workflow():
        pass

# High-level API
def enable_analytics(enable: bool = True, privacy_mode: bool = True):
    """
    Enable or disable analytics tracking
    """
    if enable:
        tracker = get_usage_tracker()
        if tracker:
            tracker.enable_tracking = True
            tracker.privacy_mode = privacy_mode
            print("✅ Analytics tracking enabled")
        else:
            print("⚠️  Analytics tracking not available")
    else:
        tracker = get_usage_tracker()
        if tracker:
            tracker.enable_tracking = False
            print("❌ Analytics tracking disabled")
        else:
            print("⚠️  Analytics tracking not available")

def get_analytics_summary(days: int = 30) -> str:
    """
    Get a quick summary of analytics data
    """
    return quick_analytics_summary(days)

def generate_analytics_report(days: int = 30, output_dir: str = None) -> str:
    """
    Generate comprehensive analytics report
    """
    dashboard = get_analytics_dashboard()
    if dashboard:
        return dashboard.generate_comprehensive_report(days, output_dir)
    else:
        return "Analytics dashboard not available"

# Main exports
__all__ = [
    "ComprehensiveBenchmark",
    "FBMModel",
    "FGNModel",
    "ARFIMAModel",
    "MRWModel",
    # Enhanced ML and Neural Network Estimators
    "CNNEstimator",
    "LSTMEstimator",
    "GRUEstimator",
    "TransformerEstimator",
    "RandomForestEstimator",
    "SVREstimator",
    "GradientBoostingEstimator",
    # Analytics
    "UsageTracker",
    "PerformanceMonitor",
    "ErrorAnalyzer",
    "WorkflowAnalyzer",
    "AnalyticsDashboard",
    "enable_analytics",
    "get_analytics_summary",
    "generate_analytics_report",
    "track_usage",
    "monitor_performance",
    "track_errors",
    "track_workflow",
    "__version__",
    "__author__",
    "__email__",
]

# Enable analytics by default (can be disabled by user)
try:
    enable_analytics(True, True)
except Exception as e:
    print(f"Warning: Could not initialize analytics: {e}")
