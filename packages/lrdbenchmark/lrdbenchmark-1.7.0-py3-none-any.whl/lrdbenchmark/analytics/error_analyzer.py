"""
Error Analyzer for LRDBench

Analyzes error patterns and failure modes to improve reliability:
- Error categorization and frequency analysis
- Failure mode identification
- Error correlation analysis
- Reliability metrics
- Improvement recommendations
"""

import re
import json
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from collections import defaultdict, Counter
import threading
from pathlib import Path


@dataclass
class ErrorEvent:
    """Represents a single error event"""

    timestamp: str
    estimator_name: str
    error_type: str
    error_message: str
    stack_trace: Optional[str]
    parameters: Dict[str, str]
    data_length: int
    user_id: Optional[str]
    session_id: str


@dataclass
class ErrorSummary:
    """Aggregated error statistics"""

    total_errors: int
    unique_errors: int
    error_rate: float
    most_common_errors: List[Tuple[str, int]]
    error_by_estimator: Dict[str, int]
    error_by_type: Dict[str, int]
    error_trends: Dict[str, str]  # "increasing", "decreasing", "stable"
    reliability_score: float


class ErrorAnalyzer:
    """
    Comprehensive error analysis system

    Features:
    - Error pattern recognition
    - Failure mode analysis
    - Reliability scoring
    - Trend analysis
    - Improvement recommendations
    """

    def __init__(self, storage_path: str = "~/.lrdbench/analytics"):
        """Initialize the error analyzer"""
        self.storage_path = Path(storage_path).expanduser()
        self.storage_path.mkdir(parents=True, exist_ok=True)

        self._lock = threading.Lock()
        self._errors: List[ErrorEvent] = []

        # Error categorization patterns
        self._error_patterns = {
            "convergence": [
                r"convergence",
                r"converge",
                r"diverg",
                r"iterations",
                r"maximum.*iterations",
                r"failed.*converge",
            ],
            "numerical": [
                r"overflow",
                r"underflow",
                r"nan",
                r"inf",
                r"division.*zero",
                r"singular",
                r"ill.*conditioned",
                r"numerical.*error",
            ],
            "memory": [
                r"memory",
                r"out.*memory",
                r"insufficient.*memory",
                r"allocation.*failed",
                r"oom",
            ],
            "parameter": [
                r"invalid.*parameter",
                r"parameter.*error",
                r"bad.*parameter",
                r"parameter.*out.*range",
                r"unsupported.*parameter",
            ],
            "data": [
                r"data.*error",
                r"invalid.*data",
                r"data.*length",
                r"insufficient.*data",
                r"data.*format",
            ],
            "algorithm": [
                r"algorithm.*error",
                r"method.*failed",
                r"estimation.*failed",
                r"computation.*error",
                r"calculation.*error",
            ],
        }

        # Load existing data
        self._load_existing_data()

    def _load_existing_data(self):
        """Load existing error data"""
        try:
            errors_file = self.storage_path / "error_events.json"
            if errors_file.exists():
                with open(errors_file, "r") as f:
                    data = json.load(f)
                    for error_data in data:
                        error = ErrorEvent(**error_data)
                        self._errors.append(error)
        except Exception as e:
            print(f"Warning: Could not load existing error data: {e}")

    def record_error(
        self,
        estimator_name: str,
        error_message: str,
        stack_trace: Optional[str] = None,
        parameters: Optional[Dict[str, str]] = None,
        data_length: int = 0,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
    ) -> None:
        """
        Record a new error event

        Args:
            estimator_name: Name of the estimator that failed
            error_message: Error message
            stack_trace: Optional stack trace
            parameters: Estimator parameters
            data_length: Length of input data
            user_id: Optional user identifier
            session_id: Optional session identifier
        """
        # Categorize error
        error_type = self._categorize_error(error_message)

        # Create error event
        error = ErrorEvent(
            timestamp=datetime.now().isoformat(),
            estimator_name=estimator_name,
            error_type=error_type,
            error_message=error_message,
            stack_trace=stack_trace,
            parameters=parameters or {},
            data_length=data_length,
            user_id=user_id,
            session_id=session_id or "unknown",
        )

        # Store error
        with self._lock:
            self._errors.append(error)

    def _categorize_error(self, error_message: str) -> str:
        """Categorize error based on message patterns"""
        error_message_lower = error_message.lower()

        for category, patterns in self._error_patterns.items():
            for pattern in patterns:
                if re.search(pattern, error_message_lower):
                    return category

        return "unknown"

    def get_error_summary(self, days: int = 30) -> ErrorSummary:
        """
        Get error summary for the specified time period

        Args:
            days: Number of days to analyze

        Returns:
            ErrorSummary object
        """
        cutoff_time = datetime.now() - timedelta(days=days)

        with self._lock:
            recent_errors = [
                e
                for e in self._errors
                if datetime.fromisoformat(e.timestamp) > cutoff_time
            ]

        if not recent_errors:
            return ErrorSummary(
                total_errors=0,
                unique_errors=0,
                error_rate=0.0,
                most_common_errors=[],
                error_by_estimator={},
                error_by_type={},
                error_trends={},
                reliability_score=1.0,
            )

        # Calculate statistics
        total_errors = len(recent_errors)
        unique_errors = len(set(e.error_message for e in recent_errors))

        # Error by estimator
        error_by_estimator = Counter(e.estimator_name for e in recent_errors)

        # Error by type
        error_by_type = Counter(e.error_type for e in recent_errors)

        # Most common errors
        error_messages = Counter(e.error_message for e in recent_errors)
        most_common_errors = error_messages.most_common(10)

        # Error trends
        error_trends = self._analyze_error_trends(recent_errors)

        # Reliability score (1.0 = no errors, 0.0 = all failures)
        # This is a simplified calculation - in practice you'd need total attempts
        reliability_score = max(0.0, 1.0 - (total_errors / 1000))  # Normalize

        return ErrorSummary(
            total_errors=total_errors,
            unique_errors=unique_errors,
            error_rate=0.0,  # Would need total attempts to calculate
            most_common_errors=most_common_errors,
            error_by_estimator=dict(error_by_estimator),
            error_by_type=dict(error_by_type),
            error_trends=error_trends,
            reliability_score=reliability_score,
        )

    def _analyze_error_trends(self, errors: List[ErrorEvent]) -> Dict[str, str]:
        """Analyze error trends over time"""
        if len(errors) < 10:
            return {}

        # Sort by timestamp
        sorted_errors = sorted(errors, key=lambda e: e.timestamp)

        # Split into early and late periods
        mid_point = len(sorted_errors) // 2
        early_errors = sorted_errors[:mid_point]
        late_errors = sorted_errors[mid_point:]

        trends = {}

        # Analyze by estimator
        estimators = set(e.estimator_name for e in errors)
        for estimator in estimators:
            early_count = len(
                [e for e in early_errors if e.estimator_name == estimator]
            )
            late_count = len([e for e in late_errors if e.estimator_name == estimator])

            if late_count < early_count * 0.8:  # 20% reduction
                trends[estimator] = "decreasing"
            elif late_count > early_count * 1.2:  # 20% increase
                trends[estimator] = "increasing"
            else:
                trends[estimator] = "stable"

        # Analyze by error type
        error_types = set(e.error_type for e in errors)
        for error_type in error_types:
            early_count = len([e for e in early_errors if e.error_type == error_type])
            late_count = len([e for e in late_errors if e.error_type == error_type])

            if late_count < early_count * 0.8:
                trends[f"type_{error_type}"] = "decreasing"
            elif late_count > early_count * 1.2:
                trends[f"type_{error_type}"] = "increasing"
            else:
                trends[f"type_{error_type}"] = "stable"

        return trends

    def get_estimator_reliability(
        self, estimator_name: str, days: int = 30
    ) -> Dict[str, float]:
        """Get reliability metrics for a specific estimator"""
        cutoff_time = datetime.now() - timedelta(days=days)

        with self._lock:
            estimator_errors = [
                e
                for e in self._errors
                if e.estimator_name == estimator_name
                and datetime.fromisoformat(e.timestamp) > cutoff_time
            ]

        if not estimator_errors:
            return {"reliability_score": 1.0, "total_errors": 0}

        # Group by error type
        error_by_type = Counter(e.error_type for e in estimator_errors)

        # Calculate reliability score based on error types
        # Different error types have different weights
        error_weights = {
            "convergence": 0.3,  # Less critical
            "numerical": 0.8,  # More critical
            "memory": 0.9,  # Very critical
            "parameter": 0.4,  # User error
            "data": 0.5,  # Data issue
            "algorithm": 0.7,  # Algorithm failure
            "unknown": 0.6,  # Unknown severity
        }

        weighted_errors = sum(
            error_by_type.get(error_type, 0) * error_weights.get(error_type, 0.5)
            for error_type in error_by_type
        )

        # Normalize reliability score
        reliability_score = max(0.0, 1.0 - (weighted_errors / 100))

        return {
            "reliability_score": reliability_score,
            "total_errors": len(estimator_errors),
            "error_by_type": dict(error_by_type),
        }

    def get_improvement_recommendations(self, days: int = 30) -> List[str]:
        """Get recommendations for improving reliability"""
        summary = self.get_error_summary(days)
        recommendations = []

        # Analyze error patterns
        if summary.error_by_type.get("convergence", 0) > 10:
            recommendations.append(
                "High convergence failures detected. Consider adjusting convergence "
                "parameters or implementing fallback methods."
            )

        if summary.error_by_type.get("numerical", 0) > 5:
            recommendations.append(
                "Numerical errors detected. Review data preprocessing and "
                "implement numerical stability improvements."
            )

        if summary.error_by_type.get("memory", 0) > 3:
            recommendations.append(
                "Memory issues detected. Consider implementing memory-efficient "
                "algorithms or chunking for large datasets."
            )

        # Analyze estimator-specific issues
        for estimator, error_count in summary.error_by_estimator.items():
            if error_count > 20:
                reliability = self.get_estimator_reliability(estimator, days)
                if reliability["reliability_score"] < 0.7:
                    recommendations.append(
                        f"Estimator '{estimator}' has low reliability. "
                        "Consider algorithm improvements or parameter tuning."
                    )

        # General recommendations
        if summary.total_errors > 100:
            recommendations.append(
                "High error rate detected. Implement comprehensive error handling "
                "and user input validation."
            )

        if not recommendations:
            recommendations.append("No specific issues detected. Continue monitoring.")

        return recommendations

    def export_errors(self, output_path: str, days: int = 30) -> None:
        """Export error data to file"""
        cutoff_time = datetime.now() - timedelta(days=days)

        with self._lock:
            recent_errors = [
                e
                for e in self._errors
                if datetime.fromisoformat(e.timestamp) > cutoff_time
            ]

        errors_data = [asdict(e) for e in recent_errors]

        with open(output_path, "w") as f:
            json.dump(errors_data, f, indent=2)

    def get_error_correlation(self, days: int = 30) -> Dict[str, Dict[str, float]]:
        """Analyze correlations between different error types"""
        cutoff_time = datetime.now() - timedelta(days=days)

        with self._lock:
            recent_errors = [
                e
                for e in self._errors
                if datetime.fromisoformat(e.timestamp) > cutoff_time
            ]

        if len(recent_errors) < 20:
            return {}

        # Group errors by session to find correlations
        session_errors = defaultdict(list)
        for error in recent_errors:
            session_errors[error.session_id].append(error.error_type)

        # Calculate correlation matrix
        error_types = list(set(e.error_type for e in recent_errors))
        correlation_matrix = {}

        for error_type1 in error_types:
            correlation_matrix[error_type1] = {}
            for error_type2 in error_types:
                if error_type1 == error_type2:
                    correlation_matrix[error_type1][error_type2] = 1.0
                else:
                    # Calculate correlation coefficient
                    correlation = self._calculate_correlation(
                        session_errors, error_type1, error_type2
                    )
                    correlation_matrix[error_type1][error_type2] = correlation

        return correlation_matrix

    def _calculate_correlation(
        self, session_errors: Dict, error_type1: str, error_type2: str
    ) -> float:
        """Calculate correlation between two error types"""
        # Simple correlation calculation
        # In practice, you might want to use more sophisticated methods

        sessions_with_type1 = sum(
            1 for errors in session_errors.values() if error_type1 in errors
        )
        sessions_with_type2 = sum(
            1 for errors in session_errors.values() if error_type2 in errors
        )
        sessions_with_both = sum(
            1
            for errors in session_errors.values()
            if error_type1 in errors and error_type2 in errors
        )

        total_sessions = len(session_errors)

        if total_sessions == 0:
            return 0.0

        # Calculate correlation using co-occurrence
        expected_both = (sessions_with_type1 * sessions_with_type2) / total_sessions
        if expected_both == 0:
            return 0.0

        correlation = (sessions_with_both - expected_both) / expected_both
        return max(-1.0, min(1.0, correlation))


# Global error analyzer instance
_global_error_analyzer: Optional[ErrorAnalyzer] = None


def get_error_analyzer() -> ErrorAnalyzer:
    """Get the global error analyzer instance"""
    global _global_error_analyzer
    if _global_error_analyzer is None:
        _global_error_analyzer = ErrorAnalyzer()
    return _global_error_analyzer


def track_errors(estimator_name: str):
    """Decorator for tracking estimator errors"""

    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                # Record error
                analyzer = get_error_analyzer()
                analyzer.record_error(
                    estimator_name=estimator_name,
                    error_message=str(e),
                    stack_trace=None,  # Could capture full traceback
                    parameters={k: str(v) for k, v in kwargs.items()},
                    data_length=len(args[0]) if args else 0,
                )
                raise

        return wrapper

    return decorator
