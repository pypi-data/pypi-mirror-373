"""
Performance Monitor for LRDBench

Monitors and analyzes performance metrics including:
- Execution time tracking
- Memory usage monitoring
- Performance trends over time
- Bottleneck identification
- Resource utilization
"""

import time
import psutil
import threading
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import json
from pathlib import Path
import numpy as np


@dataclass
class PerformanceMetrics:
    """Performance metrics for a single execution"""

    timestamp: str
    estimator_name: str
    execution_time: float
    memory_before: float
    memory_after: float
    memory_peak: float
    cpu_percent: float
    data_length: int
    parameters: Dict[str, str]


@dataclass
class PerformanceSummary:
    """Aggregated performance statistics"""

    total_executions: int
    avg_execution_time: float
    std_execution_time: float
    min_execution_time: float
    max_execution_time: float
    avg_memory_usage: float
    memory_efficiency: float
    performance_trend: str  # "improving", "stable", "degrading"
    bottleneck_estimators: List[str]


class PerformanceMonitor:
    """
    Comprehensive performance monitoring system

    Features:
    - Real-time performance tracking
    - Memory usage monitoring
    - CPU utilization tracking
    - Performance trend analysis
    - Bottleneck identification
    """

    def __init__(self, storage_path: str = "~/.lrdbench/analytics"):
        """Initialize the performance monitor"""
        self.storage_path = Path(storage_path).expanduser()
        self.storage_path.mkdir(parents=True, exist_ok=True)

        self._lock = threading.Lock()
        self._metrics: List[PerformanceMetrics] = []
        self._process = psutil.Process()

        # Load existing data
        self._load_existing_data()

    def _load_existing_data(self):
        """Load existing performance data"""
        try:
            metrics_file = self.storage_path / "performance_metrics.json"
            if metrics_file.exists():
                with open(metrics_file, "r") as f:
                    data = json.load(f)
                    for metric_data in data:
                        metric = PerformanceMetrics(**metric_data)
                        self._metrics.append(metric)
        except Exception as e:
            print(f"Warning: Could not load existing performance data: {e}")

    def start_monitoring(
        self, estimator_name: str, data_length: int, parameters: Dict[str, str]
    ) -> str:
        """
        Start monitoring a new execution

        Args:
            estimator_name: Name of the estimator
            data_length: Length of input data
            parameters: Estimator parameters

        Returns:
            Monitoring session ID
        """
        session_id = f"{estimator_name}_{int(time.time())}"

        # Record initial state
        memory_before = self._process.memory_info().rss / 1024 / 1024  # MB

        # Store session info
        with self._lock:
            self._session_info[session_id] = {
                "estimator_name": estimator_name,
                "start_time": time.time(),
                "memory_before": memory_before,
                "data_length": data_length,
                "parameters": parameters,
            }

        return session_id

    def stop_monitoring(self, session_id: str) -> None:
        """
        Stop monitoring and record metrics

        Args:
            session_id: Monitoring session ID
        """
        if session_id not in self._session_info:
            return

        session = self._session_info[session_id]
        execution_time = time.time() - session["start_time"]

        # Record final state
        memory_after = self._process.memory_info().rss / 1024 / 1024  # MB
        memory_peak = self._process.memory_info().peak_wset / 1024 / 1024  # MB
        cpu_percent = self._process.cpu_percent()

        # Create metrics
        metrics = PerformanceMetrics(
            timestamp=datetime.now().isoformat(),
            estimator_name=session["estimator_name"],
            execution_time=execution_time,
            memory_before=session["memory_before"],
            memory_after=memory_after,
            memory_peak=memory_peak,
            cpu_percent=cpu_percent,
            data_length=session["data_length"],
            parameters=session["parameters"],
        )

        # Store metrics
        with self._lock:
            self._metrics.append(metrics)

        # Clean up session
        del self._session_info[session_id]

    def get_performance_summary(self, days: int = 30) -> PerformanceSummary:
        """
        Get performance summary for the specified time period

        Args:
            days: Number of days to analyze

        Returns:
            PerformanceSummary object
        """
        cutoff_time = datetime.now() - timedelta(days=days)

        with self._lock:
            recent_metrics = [
                m
                for m in self._metrics
                if datetime.fromisoformat(m.timestamp) > cutoff_time
            ]

        if not recent_metrics:
            return PerformanceSummary(
                total_executions=0,
                avg_execution_time=0.0,
                std_execution_time=0.0,
                min_execution_time=0.0,
                max_execution_time=0.0,
                avg_memory_usage=0.0,
                memory_efficiency=0.0,
                performance_trend="stable",
                bottleneck_estimators=[],
            )

        # Calculate statistics
        execution_times = [m.execution_time for m in recent_metrics]
        memory_usage = [m.memory_after - m.memory_before for m in recent_metrics]

        avg_execution_time = np.mean(execution_times)
        std_execution_time = np.std(execution_times)
        min_execution_time = np.min(execution_times)
        max_execution_time = np.max(execution_times)

        avg_memory_usage = np.mean(memory_usage)
        memory_efficiency = (
            avg_memory_usage / avg_execution_time if avg_execution_time > 0 else 0
        )

        # Determine performance trend
        performance_trend = self._analyze_performance_trend(recent_metrics)

        # Identify bottlenecks
        bottleneck_estimators = self._identify_bottlenecks(recent_metrics)

        return PerformanceSummary(
            total_executions=len(recent_metrics),
            avg_execution_time=avg_execution_time,
            std_execution_time=std_execution_time,
            min_execution_time=min_execution_time,
            max_execution_time=max_execution_time,
            avg_memory_usage=avg_memory_usage,
            memory_efficiency=memory_efficiency,
            performance_trend=performance_trend,
            bottleneck_estimators=bottleneck_estimators,
        )

    def _analyze_performance_trend(self, metrics: List[PerformanceMetrics]) -> str:
        """Analyze performance trend over time"""
        if len(metrics) < 10:
            return "stable"

        # Sort by timestamp
        sorted_metrics = sorted(metrics, key=lambda m: m.timestamp)

        # Split into early and late periods
        mid_point = len(sorted_metrics) // 2
        early_times = [m.execution_time for m in sorted_metrics[:mid_point]]
        late_times = [m.execution_time for m in sorted_metrics[mid_point:]]

        early_avg = np.mean(early_times)
        late_avg = np.mean(late_times)

        # Calculate trend
        if late_avg < early_avg * 0.9:  # 10% improvement
            return "improving"
        elif late_avg > early_avg * 1.1:  # 10% degradation
            return "degrading"
        else:
            return "stable"

    def _identify_bottlenecks(self, metrics: List[PerformanceMetrics]) -> List[str]:
        """Identify estimators with performance bottlenecks"""
        if not metrics:
            return []

        # Group by estimator
        estimator_metrics = {}
        for metric in metrics:
            if metric.estimator_name not in estimator_metrics:
                estimator_metrics[metric.estimator_name] = []
            estimator_metrics[metric.estimator_name].append(metric)

        # Calculate average execution time for each estimator
        estimator_avg_times = {}
        for name, est_metrics in estimator_metrics.items():
            avg_time = np.mean([m.execution_time for m in est_metrics])
            estimator_avg_times[name] = avg_time

        # Find estimators above 75th percentile
        if not estimator_avg_times:
            return []

        times = list(estimator_avg_times.values())
        threshold = np.percentile(times, 75)

        bottlenecks = [
            name
            for name, avg_time in estimator_avg_times.items()
            if avg_time > threshold
        ]

        return sorted(bottlenecks, key=lambda x: estimator_avg_times[x], reverse=True)

    def get_estimator_performance(
        self, estimator_name: str, days: int = 30
    ) -> Dict[str, float]:
        """Get performance metrics for a specific estimator"""
        cutoff_time = datetime.now() - timedelta(days=days)

        with self._lock:
            estimator_metrics = [
                m
                for m in self._metrics
                if m.estimator_name == estimator_name
                and datetime.fromisoformat(m.timestamp) > cutoff_time
            ]

        if not estimator_metrics:
            return {}

        execution_times = [m.execution_time for m in estimator_metrics]
        memory_usage = [m.memory_after - m.memory_before for m in estimator_metrics]

        return {
            "avg_execution_time": np.mean(execution_times),
            "std_execution_time": np.std(execution_times),
            "min_execution_time": np.min(execution_times),
            "max_execution_time": np.max(execution_times),
            "avg_memory_usage": np.mean(memory_usage),
            "total_executions": len(estimator_metrics),
        }

    def export_metrics(self, output_path: str, days: int = 30) -> None:
        """Export performance metrics to file"""
        cutoff_time = datetime.now() - timedelta(days=days)

        with self._lock:
            recent_metrics = [
                m
                for m in self._metrics
                if datetime.fromisoformat(m.timestamp) > cutoff_time
            ]

        metrics_data = [asdict(m) for m in recent_metrics]

        with open(output_path, "w") as f:
            json.dump(metrics_data, f, indent=2)

    def get_memory_trends(self, days: int = 7) -> Dict[str, List[float]]:
        """Get memory usage trends over time"""
        cutoff_time = datetime.now() - timedelta(days=days)

        with self._lock:
            recent_metrics = [
                m
                for m in self._metrics
                if datetime.fromisoformat(m.timestamp) > cutoff_time
            ]

        # Group by day
        daily_memory = {}
        for metric in recent_metrics:
            date = metric.timestamp[:10]  # YYYY-MM-DD
            if date not in daily_memory:
                daily_memory[date] = []
            daily_memory[date].append(metric.memory_peak)

        # Calculate daily averages
        trends = {}
        for date, memory_values in daily_memory.items():
            trends[date] = np.mean(memory_values)

        return trends


# Global performance monitor instance
_global_monitor: Optional[PerformanceMonitor] = None


def get_performance_monitor() -> PerformanceMonitor:
    """Get the global performance monitor instance"""
    global _global_monitor
    if _global_monitor is None:
        _global_monitor = PerformanceMonitor()
    return _global_monitor


def monitor_performance(estimator_name: str):
    """Decorator for monitoring estimator performance"""

    def decorator(func):
        def wrapper(*args, **kwargs):
            monitor = get_performance_monitor()

            # Start monitoring
            session_id = monitor.start_monitoring(
                estimator_name=estimator_name,
                data_length=len(args[0]) if args else 0,
                parameters={k: str(v) for k, v in kwargs.items()},
            )

            try:
                result = func(*args, **kwargs)
                return result
            finally:
                # Stop monitoring
                monitor.stop_monitoring(session_id)

        return wrapper

    return decorator
