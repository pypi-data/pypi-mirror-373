"""
Usage Tracker for LRDBench

Tracks comprehensive usage patterns including:
- Estimator popularity and usage frequency
- Parameter combinations and common values
- User workflow patterns
- Performance metrics
- Error rates and types
"""

import time
import json
import hashlib
from datetime import datetime
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict
import threading
import os
from pathlib import Path


@dataclass
class UsageEvent:
    """Represents a single usage event"""

    timestamp: str
    event_type: str
    estimator_name: str
    parameters: Dict[str, Any]
    execution_time: float
    success: bool
    error_message: Optional[str]
    data_length: int
    user_id: Optional[str]
    session_id: str


@dataclass
class UsageSummary:
    """Aggregated usage statistics"""

    total_events: int
    unique_users: int
    estimator_usage: Dict[str, int]
    parameter_frequency: Dict[str, Dict[str, int]]
    success_rate: float
    avg_execution_time: float
    common_errors: Dict[str, int]
    data_length_distribution: Dict[str, int]


class UsageTracker:
    """
    Comprehensive usage tracking system for LRDBench

    Features:
    - Real-time event tracking
    - Privacy-preserving user identification
    - Performance monitoring
    - Error analysis
    - Usage pattern detection
    """

    def __init__(
        self,
        storage_path: str = "~/.lrdbench/analytics",
        enable_tracking: bool = True,
        privacy_mode: bool = True,
    ):
        """
        Initialize the usage tracker

        Args:
            storage_path: Directory to store analytics data
            enable_tracking: Whether to enable usage tracking
            privacy_mode: Enable privacy-preserving features
        """
        self.enable_tracking = enable_tracking
        self.privacy_mode = privacy_mode
        self.storage_path = Path(storage_path).expanduser()
        self.storage_path.mkdir(parents=True, exist_ok=True)

        # Thread-safe storage
        self._lock = threading.Lock()
        self._events: List[UsageEvent] = []
        self._session_id = self._generate_session_id()

        # Load existing data
        self._load_existing_data()

        # Start background processing
        self._start_background_processing()

    def _generate_session_id(self) -> str:
        """Generate a unique session ID"""
        return hashlib.md5(f"{time.time()}_{os.getpid()}".encode()).hexdigest()[:8]

    def _load_existing_data(self):
        """Load existing analytics data from storage"""
        try:
            events_file = self.storage_path / "usage_events.json"
            if events_file.exists():
                with open(events_file, "r") as f:
                    data = json.load(f)
                    for event_data in data:
                        event = UsageEvent(**event_data)
                        self._events.append(event)
        except Exception as e:
            print(f"Warning: Could not load existing analytics data: {e}")

    def _start_background_processing(self):
        """Start background thread for data processing"""
        if not self.enable_tracking:
            return

        def background_worker():
            while True:
                try:
                    time.sleep(300)  # Process every 5 minutes
                    self._save_data()
                    self._cleanup_old_data()
                except Exception as e:
                    print(f"Analytics background worker error: {e}")

        thread = threading.Thread(target=background_worker, daemon=True)
        thread.start()

    def track_estimator_usage(
        self,
        estimator_name: str,
        parameters: Dict[str, Any],
        execution_time: float,
        success: bool,
        error_message: Optional[str] = None,
        data_length: int = 0,
        user_id: Optional[str] = None,
    ) -> None:
        """
        Track usage of an estimator

        Args:
            estimator_name: Name of the estimator used
            parameters: Parameters passed to the estimator
            execution_time: Time taken for execution
            success: Whether the estimation was successful
            error_message: Error message if failed
            data_length: Length of input data
            user_id: Optional user identifier
        """
        if not self.enable_tracking:
            return

        # Create usage event
        event = UsageEvent(
            timestamp=datetime.now().isoformat(),
            event_type="estimator_usage",
            estimator_name=estimator_name,
            parameters=self._sanitize_parameters(parameters),
            execution_time=execution_time,
            success=success,
            error_message=error_message,
            data_length=data_length,
            user_id=self._hash_user_id(user_id) if user_id else None,
            session_id=self._session_id,
        )

        # Store event
        with self._lock:
            self._events.append(event)

    def track_benchmark_run(
        self,
        benchmark_type: str,
        estimators_used: List[str],
        total_time: float,
        success_count: int,
        total_count: int,
        data_models: List[str],
    ) -> None:
        """
        Track benchmark execution

        Args:
            benchmark_type: Type of benchmark run
            estimators_used: List of estimators used
            total_time: Total execution time
            success_count: Number of successful runs
            total_count: Total number of runs
            data_models: Data models tested
        """
        if not self.enable_tracking:
            return

        event = UsageEvent(
            timestamp=datetime.now().isoformat(),
            event_type="benchmark_run",
            estimator_name=",".join(estimators_used),
            parameters={
                "benchmark_type": benchmark_type,
                "estimators_count": len(estimators_used),
                "data_models": data_models,
                "success_rate": success_count / total_count if total_count > 0 else 0,
            },
            execution_time=total_time,
            success=success_count > 0,
            error_message=None,
            data_length=0,
            user_id=None,
            session_id=self._session_id,
        )

        with self._lock:
            self._events.append(event)

    def _sanitize_parameters(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Sanitize parameters for privacy and storage"""
        sanitized = {}
        for key, value in params.items():
            if isinstance(value, (int, float, str, bool)):
                sanitized[key] = value
            elif isinstance(value, (list, tuple)):
                sanitized[key] = [str(v) for v in value[:10]]  # Limit list length
            else:
                sanitized[key] = str(type(value).__name__)
        return sanitized

    def _hash_user_id(self, user_id: str) -> str:
        """Hash user ID for privacy"""
        if not self.privacy_mode:
            return user_id
        return hashlib.sha256(user_id.encode()).hexdigest()[:16]

    def get_usage_summary(self, days: int = 30) -> UsageSummary:
        """
        Get usage summary for the specified time period

        Args:
            days: Number of days to analyze

        Returns:
            UsageSummary object with aggregated statistics
        """
        cutoff_time = datetime.now().timestamp() - (days * 24 * 3600)

        with self._lock:
            recent_events = [
                e
                for e in self._events
                if datetime.fromisoformat(e.timestamp).timestamp() > cutoff_time
            ]

        if not recent_events:
            return UsageSummary(
                total_events=0,
                unique_users=0,
                estimator_usage={},
                parameter_frequency={},
                success_rate=0.0,
                avg_execution_time=0.0,
                common_errors={},
                data_length_distribution={},
            )

        # Calculate statistics
        estimator_usage = {}
        parameter_frequency = {}
        success_count = 0
        total_time = 0.0
        errors = {}
        data_lengths = {}
        user_ids = set()

        for event in recent_events:
            # Estimator usage
            estimator_usage[event.estimator_name] = (
                estimator_usage.get(event.estimator_name, 0) + 1
            )

            # Parameters
            for key, value in event.parameters.items():
                if key not in parameter_frequency:
                    parameter_frequency[key] = {}
                str_value = str(value)
                parameter_frequency[key][str_value] = (
                    parameter_frequency[key].get(str_value, 0) + 1
                )

            # Success rate
            if event.success:
                success_count += 1

            # Execution time
            total_time += event.execution_time

            # Errors
            if event.error_message:
                errors[event.error_message] = errors.get(event.error_message, 0) + 1

            # Data length
            if event.data_length > 0:
                length_range = self._get_length_range(event.data_length)
                data_lengths[length_range] = data_lengths.get(length_range, 0) + 1

            # Users
            if event.user_id:
                user_ids.add(event.user_id)

        return UsageSummary(
            total_events=len(recent_events),
            unique_users=len(user_ids),
            estimator_usage=estimator_usage,
            parameter_frequency=parameter_frequency,
            success_rate=success_count / len(recent_events),
            avg_execution_time=total_time / len(recent_events),
            common_errors=errors,
            data_length_distribution=data_lengths,
        )

    def _get_length_range(self, length: int) -> str:
        """Convert data length to range category"""
        if length < 100:
            return "<100"
        elif length < 1000:
            return "100-1000"
        elif length < 10000:
            return "1000-10000"
        else:
            return ">10000"

    def _save_data(self):
        """Save analytics data to storage"""
        try:
            with self._lock:
                events_data = [asdict(event) for event in self._events]

            events_file = self.storage_path / "usage_events.json"
            with open(events_file, "w") as f:
                json.dump(events_data, f, indent=2)

        except Exception as e:
            print(f"Error saving analytics data: {e}")

    def _cleanup_old_data(self, max_age_days: int = 90):
        """Remove old analytics data"""
        cutoff_time = datetime.now().timestamp() - (max_age_days * 24 * 3600)

        with self._lock:
            self._events = [
                e
                for e in self._events
                if datetime.fromisoformat(e.timestamp).timestamp() > cutoff_time
            ]

    def export_summary(self, output_path: str, days: int = 30) -> None:
        """
        Export usage summary to file

        Args:
            output_path: Path to save the summary
            days: Number of days to analyze
        """
        summary = self.get_usage_summary(days)

        with open(output_path, "w") as f:
            json.dump(asdict(summary), f, indent=2)

    def get_popular_estimators(self, top_n: int = 10) -> List[tuple]:
        """Get top N most popular estimators"""
        summary = self.get_usage_summary()
        sorted_estimators = sorted(
            summary.estimator_usage.items(), key=lambda x: x[1], reverse=True
        )
        return sorted_estimators[:top_n]

    def get_performance_trends(self, days: int = 7) -> Dict[str, List[float]]:
        """Get performance trends over time"""
        # Implementation for time-series performance analysis
        # This would show how execution times change over time
        pass


# Global usage tracker instance
_global_tracker: Optional[UsageTracker] = None


def get_usage_tracker() -> UsageTracker:
    """Get the global usage tracker instance"""
    global _global_tracker
    if _global_tracker is None:
        _global_tracker = UsageTracker()
    return _global_tracker


def track_usage(estimator_name: str, **kwargs):
    """Decorator for tracking estimator usage"""

    def decorator(func):
        def wrapper(*args, **func_kwargs):
            start_time = time.time()
            success = False
            error_message = None

            try:
                result = func(*args, **func_kwargs)
                success = True
                return result
            except Exception as e:
                error_message = str(e)
                raise
            finally:
                execution_time = time.time() - start_time
                tracker = get_usage_tracker()
                tracker.track_estimator_usage(
                    estimator_name=estimator_name,
                    parameters=func_kwargs,
                    execution_time=execution_time,
                    success=success,
                    error_message=error_message,
                    **kwargs,
                )

        return wrapper

    return decorator
