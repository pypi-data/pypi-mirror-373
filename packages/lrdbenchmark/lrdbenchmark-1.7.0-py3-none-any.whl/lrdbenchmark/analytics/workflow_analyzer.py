"""
Workflow Analyzer for LRDBench

Analyzes user workflows and usage patterns:
- Workflow sequence analysis
- Common parameter combinations
- User behavior patterns
- Workflow optimization recommendations
- Feature usage analysis
"""

import json
from typing import Dict, List, Optional, Tuple, Set, Any
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from collections import defaultdict, Counter
import threading
from pathlib import Path
import networkx as nx


@dataclass
class WorkflowStep:
    """Represents a single step in a user workflow"""

    timestamp: str
    step_type: str  # 'estimator_usage', 'benchmark_run', 'data_generation', etc.
    estimator_name: Optional[str]
    parameters: Dict[str, str]
    data_length: int
    session_id: str
    user_id: Optional[str]


@dataclass
class Workflow:
    """Represents a complete user workflow"""

    workflow_id: str
    session_id: str
    user_id: Optional[str]
    steps: List[WorkflowStep]
    start_time: str
    end_time: str
    total_duration: float
    step_count: int


@dataclass
class WorkflowSummary:
    """Aggregated workflow statistics"""

    total_workflows: int
    unique_users: int
    avg_workflow_duration: float
    avg_steps_per_workflow: float
    common_workflow_patterns: List[Tuple[List[str], int]]
    popular_estimator_sequences: List[Tuple[List[str], int]]
    workflow_complexity_distribution: Dict[str, int]


class WorkflowAnalyzer:
    """
    Comprehensive workflow analysis system

    Features:
    - Workflow pattern recognition
    - Sequence analysis
    - User behavior modeling
    - Optimization recommendations
    - Feature usage analysis
    """

    def __init__(self, storage_path: str = "~/.lrdbench/analytics"):
        """Initialize the workflow analyzer"""
        self.storage_path = Path(storage_path).expanduser()
        self.storage_path.mkdir(parents=True, exist_ok=True)

        self._lock = threading.Lock()
        self._workflows: List[Workflow] = []
        self._current_sessions: Dict[str, List[WorkflowStep]] = defaultdict(list)

        # Load existing data
        self._load_existing_data()

    def _load_existing_data(self):
        """Load existing workflow data"""
        try:
            workflows_file = self.storage_path / "workflows.json"
            if workflows_file.exists():
                with open(workflows_file, "r") as f:
                    data = json.load(f)
                    for workflow_data in data:
                        # Reconstruct workflow from data
                        workflow = self._reconstruct_workflow(workflow_data)
                        if workflow:
                            self._workflows.append(workflow)
        except Exception as e:
            print(f"Warning: Could not load existing workflow data: {e}")

    def _reconstruct_workflow(self, workflow_data: Dict) -> Optional[Workflow]:
        """Reconstruct workflow object from stored data"""
        try:
            steps = []
            for step_data in workflow_data.get("steps", []):
                step = WorkflowStep(**step_data)
                steps.append(step)

            return Workflow(
                workflow_id=workflow_data["workflow_id"],
                session_id=workflow_data["session_id"],
                user_id=workflow_data.get("user_id"),
                steps=steps,
                start_time=workflow_data["start_time"],
                end_time=workflow_data["end_time"],
                total_duration=workflow_data["total_duration"],
                step_count=workflow_data["step_count"],
            )
        except Exception as e:
            print(f"Warning: Could not reconstruct workflow: {e}")
            return None

    def start_workflow_session(
        self, session_id: str, user_id: Optional[str] = None
    ) -> None:
        """Start tracking a new workflow session"""
        with self._lock:
            if session_id not in self._current_sessions:
                self._current_sessions[session_id] = []

    def add_workflow_step(
        self,
        session_id: str,
        step_type: str,
        estimator_name: Optional[str] = None,
        parameters: Optional[Dict[str, str]] = None,
        data_length: int = 0,
        user_id: Optional[str] = None,
    ) -> None:
        """
        Add a step to the current workflow session

        Args:
            session_id: Session identifier
            step_type: Type of workflow step
            estimator_name: Name of estimator used (if applicable)
            parameters: Parameters for the step
            data_length: Length of input data
            user_id: Optional user identifier
        """
        step = WorkflowStep(
            timestamp=datetime.now().isoformat(),
            step_type=step_type,
            estimator_name=estimator_name,
            parameters=parameters or {},
            data_length=data_length,
            session_id=session_id,
            user_id=user_id,
        )

        with self._lock:
            if session_id in self._current_sessions:
                self._current_sessions[session_id].append(step)

    def end_workflow_session(self, session_id: str) -> Optional[str]:
        """
        End a workflow session and create workflow record

        Args:
            session_id: Session identifier

        Returns:
            Workflow ID if successful, None otherwise
        """
        with self._lock:
            if session_id not in self._current_sessions:
                return None

            steps = self._current_sessions[session_id]
            if not steps:
                del self._current_sessions[session_id]
                return None

            # Create workflow
            workflow_id = f"workflow_{int(datetime.now().timestamp())}_{session_id}"
            start_time = steps[0].timestamp
            end_time = steps[-1].timestamp

            # Calculate duration
            start_dt = datetime.fromisoformat(start_time)
            end_dt = datetime.fromisoformat(end_time)
            total_duration = (end_dt - start_dt).total_seconds()

            workflow = Workflow(
                workflow_id=workflow_id,
                session_id=session_id,
                user_id=steps[0].user_id,
                steps=steps,
                start_time=start_time,
                end_time=end_time,
                total_duration=total_duration,
                step_count=len(steps),
            )

            # Store workflow
            self._workflows.append(workflow)

            # Clean up session
            del self._current_sessions[session_id]

            return workflow_id

    def get_workflow_summary(self, days: int = 30) -> WorkflowSummary:
        """
        Get workflow summary for the specified time period

        Args:
            days: Number of days to analyze

        Returns:
            WorkflowSummary object
        """
        cutoff_time = datetime.now() - timedelta(days=days)

        with self._lock:
            recent_workflows = [
                w
                for w in self._workflows
                if datetime.fromisoformat(w.start_time) > cutoff_time
            ]

        if not recent_workflows:
            return WorkflowSummary(
                total_workflows=0,
                unique_users=0,
                avg_workflow_duration=0.0,
                avg_steps_per_workflow=0.0,
                common_workflow_patterns=[],
                popular_estimator_sequences=[],
                workflow_complexity_distribution={},
            )

        # Calculate basic statistics
        total_workflows = len(recent_workflows)
        unique_users = len(set(w.user_id for w in recent_workflows if w.user_id))

        durations = [w.total_duration for w in recent_workflows]
        avg_workflow_duration = sum(durations) / len(durations)

        step_counts = [w.step_count for w in recent_workflows]
        avg_steps_per_workflow = sum(step_counts) / len(step_counts)

        # Analyze workflow patterns
        common_patterns = self._analyze_workflow_patterns(recent_workflows)
        popular_sequences = self._analyze_estimator_sequences(recent_workflows)
        complexity_distribution = self._analyze_workflow_complexity(recent_workflows)

        return WorkflowSummary(
            total_workflows=total_workflows,
            unique_users=unique_users,
            avg_workflow_duration=avg_workflow_duration,
            avg_steps_per_workflow=avg_steps_per_workflow,
            common_workflow_patterns=common_patterns,
            popular_estimator_sequences=popular_sequences,
            workflow_complexity_distribution=complexity_distribution,
        )

    def _analyze_workflow_patterns(
        self, workflows: List[Workflow]
    ) -> List[Tuple[List[str], int]]:
        """Analyze common workflow patterns"""
        patterns = Counter()

        for workflow in workflows:
            # Extract step types as pattern
            pattern = [step.step_type for step in workflow.steps]
            patterns[tuple(pattern)] += 1

        # Return top patterns
        return patterns.most_common(10)

    def _analyze_estimator_sequences(
        self, workflows: List[Workflow]
    ) -> List[Tuple[List[str], int]]:
        """Analyze popular estimator sequences"""
        sequences = Counter()

        for workflow in workflows:
            # Extract estimator names as sequence
            estimator_sequence = [
                step.estimator_name for step in workflow.steps if step.estimator_name
            ]
            if len(estimator_sequence) > 1:  # Only sequences with multiple estimators
                sequences[tuple(estimator_sequence)] += 1

        # Return top sequences
        return sequences.most_common(10)

    def _analyze_workflow_complexity(self, workflows: List[Workflow]) -> Dict[str, int]:
        """Analyze workflow complexity distribution"""
        complexity_distribution = {
            "simple": 0,  # 1-2 steps
            "moderate": 0,  # 3-5 steps
            "complex": 0,  # 6-10 steps
            "very_complex": 0,  # 10+ steps
        }

        for workflow in workflows:
            step_count = workflow.step_count
            if step_count <= 2:
                complexity_distribution["simple"] += 1
            elif step_count <= 5:
                complexity_distribution["moderate"] += 1
            elif step_count <= 10:
                complexity_distribution["complex"] += 1
            else:
                complexity_distribution["very_complex"] += 1

        return complexity_distribution

    def get_user_workflow_patterns(
        self, user_id: str, days: int = 30
    ) -> Dict[str, Any]:
        """Get workflow patterns for a specific user"""
        cutoff_time = datetime.now() - timedelta(days=days)

        with self._lock:
            user_workflows = [
                w
                for w in self._workflows
                if w.user_id == user_id
                and datetime.fromisoformat(w.start_time) > cutoff_time
            ]

        if not user_workflows:
            return {}

        # Analyze user-specific patterns
        avg_duration = sum(w.total_duration for w in user_workflows) / len(
            user_workflows
        )
        avg_steps = sum(w.step_count for w in user_workflows) / len(user_workflows)

        # Most common step types
        step_types = Counter()
        for workflow in user_workflows:
            for step in workflow.steps:
                step_types[step.step_type] += 1

        # Most common estimators
        estimators = Counter()
        for workflow in user_workflows:
            for step in workflow.steps:
                if step.estimator_name:
                    estimators[step.estimator_name] += 1

        return {
            "total_workflows": len(user_workflows),
            "avg_duration": avg_duration,
            "avg_steps": avg_steps,
            "favorite_step_types": step_types.most_common(5),
            "favorite_estimators": estimators.most_common(5),
        }

    def get_workflow_optimization_recommendations(self, days: int = 30) -> List[str]:
        """Get recommendations for workflow optimization"""
        summary = self.get_workflow_summary(days)
        recommendations = []

        # Analyze workflow duration
        if summary.avg_workflow_duration > 300:  # 5 minutes
            recommendations.append(
                "Workflows are taking a long time on average. Consider "
                "implementing parallel processing or caching."
            )

        # Analyze workflow complexity
        complex_workflows = summary.workflow_complexity_distribution.get(
            "complex", 0
        ) + summary.workflow_complexity_distribution.get("very_complex", 0)
        if complex_workflows > summary.total_workflows * 0.3:  # 30% are complex
            recommendations.append(
                "Many workflows are complex. Consider creating workflow templates "
                "or automated workflows for common tasks."
            )

        # Analyze step patterns
        if summary.common_workflow_patterns:
            most_common = summary.common_workflow_patterns[0]
            if (
                most_common[1] > summary.total_workflows * 0.5
            ):  # 50% follow same pattern
                recommendations.append(
                    f"Most workflows follow the same pattern: {most_common[0]}. "
                    "Consider creating a dedicated function for this workflow."
                )

        # Analyze estimator usage
        if summary.popular_estimator_sequences:
            most_popular = summary.popular_estimator_sequences[0]
            if most_popular[1] > summary.total_workflows * 0.4:  # 40% use same sequence
                recommendations.append(
                    f"Many users use the same estimator sequence: {most_popular[0]}. "
                    "Consider creating a combined estimator or pipeline."
                )

        if not recommendations:
            recommendations.append("No specific optimization opportunities detected.")

        return recommendations

    def export_workflows(self, output_path: str, days: int = 30) -> None:
        """Export workflow data to file"""
        cutoff_time = datetime.now() - timedelta(days=days)

        with self._lock:
            recent_workflows = [
                w
                for w in self._workflows
                if datetime.fromisoformat(w.start_time) > cutoff_time
            ]

        workflows_data = [asdict(w) for w in recent_workflows]

        with open(output_path, "w") as f:
            json.dump(workflows_data, f, indent=2)

    def get_feature_usage_analysis(self, days: int = 30) -> Dict[str, Any]:
        """Analyze feature usage patterns"""
        cutoff_time = datetime.now() - timedelta(days=days)

        with self._lock:
            recent_workflows = [
                w
                for w in self._workflows
                if datetime.fromisoformat(w.start_time) > cutoff_time
            ]

        # Analyze feature usage
        feature_usage = {
            "estimators": Counter(),
            "step_types": Counter(),
            "parameter_combinations": Counter(),
            "data_length_ranges": Counter(),
        }

        for workflow in recent_workflows:
            for step in workflow.steps:
                # Count step types
                feature_usage["step_types"][step.step_type] += 1

                # Count estimators
                if step.estimator_name:
                    feature_usage["estimators"][step.estimator_name] += 1

                # Count parameter combinations
                if step.parameters:
                    param_key = tuple(sorted(step.parameters.items()))
                    feature_usage["parameter_combinations"][param_key] += 1

                # Count data length ranges
                if step.data_length > 0:
                    length_range = self._get_length_range(step.data_length)
                    feature_usage["data_length_ranges"][length_range] += 1

        return {
            "total_workflows": len(recent_workflows),
            "feature_usage": feature_usage,
            "top_estimators": feature_usage["estimators"].most_common(10),
            "top_step_types": feature_usage["step_types"].most_common(10),
            "top_parameter_combinations": feature_usage[
                "parameter_combinations"
            ].most_common(10),
            "data_length_distribution": dict(feature_usage["data_length_ranges"]),
        }

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


# Global workflow analyzer instance
_global_workflow_analyzer: Optional[WorkflowAnalyzer] = None


def get_workflow_analyzer() -> WorkflowAnalyzer:
    """Get the global workflow analyzer instance"""
    global _global_workflow_analyzer
    if _global_workflow_analyzer is None:
        _global_workflow_analyzer = WorkflowAnalyzer()
    return _global_workflow_analyzer


def track_workflow(step_type: str):
    """Decorator for tracking workflow steps"""

    def decorator(func):
        def wrapper(*args, **kwargs):
            analyzer = get_workflow_analyzer()

            # Start workflow session if not already started
            session_id = f"session_{int(datetime.now().timestamp())}"
            analyzer.start_workflow_session(session_id)

            # Add workflow step
            analyzer.add_workflow_step(
                session_id=session_id,
                step_type=step_type,
                estimator_name=func.__name__ if hasattr(func, "__name__") else None,
                parameters={k: str(v) for k, v in kwargs.items()},
                data_length=len(args[0]) if args else 0,
            )

            try:
                result = func(*args, **kwargs)
                return result
            finally:
                # End workflow session
                analyzer.end_workflow_session(session_id)

        return wrapper

    return decorator
