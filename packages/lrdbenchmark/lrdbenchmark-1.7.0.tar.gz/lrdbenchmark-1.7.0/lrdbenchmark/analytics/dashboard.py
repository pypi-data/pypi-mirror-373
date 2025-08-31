"""
Analytics Dashboard for LRDBench

Provides a unified interface for accessing all analytics data:
- Usage statistics
- Performance metrics
- Error analysis
- Workflow insights
- Report generation
"""

import json
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from pathlib import Path
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np

from .usage_tracker import UsageTracker, get_usage_tracker
from .performance_monitor import PerformanceMonitor, get_performance_monitor
from .error_analyzer import ErrorAnalyzer, get_error_analyzer
from .workflow_analyzer import WorkflowAnalyzer, get_workflow_analyzer


class AnalyticsDashboard:
    """
    Comprehensive analytics dashboard for LRDBench

    Provides easy access to all analytics data and generates
    comprehensive reports and visualizations.
    """

    def __init__(self, storage_path: str = "~/.lrdbench/analytics"):
        """Initialize the analytics dashboard"""
        self.storage_path = Path(storage_path).expanduser()
        self.storage_path.mkdir(parents=True, exist_ok=True)

        # Initialize analytics components
        self.usage_tracker = get_usage_tracker()
        self.performance_monitor = get_performance_monitor()
        self.error_analyzer = get_error_analyzer()
        self.workflow_analyzer = get_workflow_analyzer()

        # Set plotting style
        plt.style.use("default")
        sns.set_palette("husl")

    def get_comprehensive_summary(self, days: int = 30) -> Dict[str, Any]:
        """
        Get comprehensive summary of all analytics data

        Args:
            days: Number of days to analyze

        Returns:
            Dictionary containing all analytics summaries
        """
        return {
            "usage_summary": self.usage_tracker.get_usage_summary(days),
            "performance_summary": self.performance_monitor.get_performance_summary(
                days
            ),
            "error_summary": self.error_analyzer.get_error_summary(days),
            "workflow_summary": self.workflow_analyzer.get_workflow_summary(days),
            "generated_at": datetime.now().isoformat(),
            "analysis_period_days": days,
        }

    def generate_usage_report(
        self, days: int = 30, output_path: Optional[str] = None
    ) -> str:
        """Generate comprehensive usage report"""
        summary = self.usage_tracker.get_usage_summary(days)

        report = f"""
# LRDBench Usage Report
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Analysis Period: {days} days

## Overview
- Total Events: {summary.total_events:,}
- Unique Users: {summary.unique_users:,}
- Success Rate: {summary.success_rate:.1%}
- Average Execution Time: {summary.avg_execution_time:.3f}s

## Most Popular Estimators
"""

        for estimator, count in summary.estimator_usage.items():
            report += f"- {estimator}: {count:,} uses\n"

        report += f"""
## Parameter Usage Patterns
"""

        for param, values in summary.parameter_frequency.items():
            report += f"\n### {param}\n"
            for value, count in list(values.items())[:5]:  # Top 5 values
                report += f"- {value}: {count:,} times\n"

        report += f"""
## Data Length Distribution
"""

        for length_range, count in summary.data_length_distribution.items():
            report += f"- {length_range}: {count:,} datasets\n"

        if summary.common_errors:
            report += f"""
## Common Errors
"""
            for error, count in summary.common_errors.items()[:5]:  # Top 5 errors
                report += f"- {error}: {count:,} occurrences\n"

        if output_path:
            with open(output_path, "w") as f:
                f.write(report)

        return report

    def generate_performance_report(
        self, days: int = 30, output_path: Optional[str] = None
    ) -> str:
        """Generate comprehensive performance report"""
        summary = self.performance_monitor.get_performance_summary(days)

        report = f"""
# LRDBench Performance Report
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Analysis Period: {days} days

## Performance Overview
- Total Executions: {summary.total_executions:,}
- Average Execution Time: {summary.avg_execution_time:.3f}s
- Execution Time Range: {summary.min_execution_time:.3f}s - {summary.max_execution_time:.3f}s
- Standard Deviation: {summary.std_execution_time:.3f}s
- Performance Trend: {summary.performance_trend}

## Memory Usage
- Average Memory Usage: {summary.avg_memory_usage:.2f} MB
- Memory Efficiency: {summary.memory_efficiency:.3f} MB/s

## Performance Bottlenecks
"""

        if summary.bottleneck_estimators:
            for estimator in summary.bottleneck_estimators:
                report += f"- {estimator}\n"
        else:
            report += "- No significant bottlenecks detected\n"

        if output_path:
            with open(output_path, "w") as f:
                f.write(report)

        return report

    def generate_reliability_report(
        self, days: int = 30, output_path: Optional[str] = None
    ) -> str:
        """Generate comprehensive reliability report"""
        error_summary = self.error_analyzer.get_error_summary(days)
        recommendations = self.error_analyzer.get_improvement_recommendations(days)

        report = f"""
# LRDBench Reliability Report
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Analysis Period: {days} days

## Error Overview
- Total Errors: {error_summary.total_errors:,}
- Unique Errors: {error_summary.unique_errors:,}
- Reliability Score: {error_summary.reliability_score:.1%}

## Error Distribution by Type
"""

        for error_type, count in error_summary.error_by_type.items():
            report += f"- {error_type}: {count:,} errors\n"

        report += f"""
## Error Distribution by Estimator
"""

        for estimator, count in error_summary.error_by_estimator.items():
            report += f"- {estimator}: {count:,} errors\n"

        if error_summary.error_trends:
            report += f"""
## Error Trends
"""
            for trend_key, trend_value in error_summary.error_trends.items():
                report += f"- {trend_key}: {trend_value}\n"

        if recommendations:
            report += f"""
## Improvement Recommendations
"""
            for i, recommendation in enumerate(recommendations, 1):
                report += f"{i}. {recommendation}\n"

        if output_path:
            with open(output_path, "w") as f:
                f.write(report)

        return report

    def generate_workflow_report(
        self, days: int = 30, output_path: Optional[str] = None
    ) -> str:
        """Generate comprehensive workflow report"""
        summary = self.workflow_analyzer.get_workflow_summary(days)
        recommendations = (
            self.workflow_analyzer.get_workflow_optimization_recommendations(days)
        )
        feature_usage = self.workflow_analyzer.get_feature_usage_analysis(days)

        report = f"""
# LRDBench Workflow Report
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Analysis Period: {days} days

## Workflow Overview
- Total Workflows: {summary.total_workflows:,}
- Unique Users: {summary.unique_users:,}
- Average Duration: {summary.avg_workflow_duration:.1f}s
- Average Steps: {summary.avg_steps_per_workflow:.1f}

## Workflow Complexity Distribution
"""

        for complexity, count in summary.workflow_complexity_distribution.items():
            percentage = (
                (count / summary.total_workflows * 100)
                if summary.total_workflows > 0
                else 0
            )
            report += f"- {complexity.replace('_', ' ').title()}: {count:,} ({percentage:.1f}%)\n"

        if summary.common_workflow_patterns:
            report += f"""
## Common Workflow Patterns
"""
            for i, (pattern, count) in enumerate(
                summary.common_workflow_patterns[:5], 1
            ):
                report += f"{i}. {pattern}: {count:,} workflows\n"

        if summary.popular_estimator_sequences:
            report += f"""
## Popular Estimator Sequences
"""
            for i, (sequence, count) in enumerate(
                summary.popular_estimator_sequences[:5], 1
            ):
                report += f"{i}. {' → '.join(sequence)}: {count:,} workflows\n"

        if feature_usage["top_estimators"]:
            report += f"""
## Top Estimators by Usage
"""
            for estimator, count in feature_usage["top_estimators"][:10]:
                report += f"- {estimator}: {count:,} uses\n"

        if recommendations:
            report += f"""
## Optimization Recommendations
"""
            for i, recommendation in enumerate(recommendations, 1):
                report += f"{i}. {recommendation}\n"

        if output_path:
            with open(output_path, "w") as f:
                f.write(report)

        return report

    def generate_comprehensive_report(
        self, days: int = 30, output_dir: Optional[str] = None
    ) -> str:
        """Generate comprehensive analytics report with all sections"""
        if output_dir is None:
            output_dir = self.storage_path / "reports"

        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Generate individual reports
        usage_report = self.generate_usage_report(
            days, output_path / f"usage_report_{timestamp}.md"
        )
        performance_report = self.generate_performance_report(
            days, output_path / f"performance_report_{timestamp}.md"
        )
        reliability_report = self.generate_reliability_report(
            days, output_path / f"reliability_report_{timestamp}.md"
        )
        workflow_report = self.generate_workflow_report(
            days, output_path / f"workflow_report_{timestamp}.md"
        )

        # Generate comprehensive report
        comprehensive_report = f"""
# LRDBench Comprehensive Analytics Report
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Analysis Period: {days} days

## Executive Summary
This report provides comprehensive insights into LRDBench usage, performance, reliability, and workflows.

## Quick Statistics
"""

        # Add quick stats from all summaries
        usage_summary = self.usage_tracker.get_usage_summary(days)
        performance_summary = self.performance_monitor.get_performance_summary(days)
        error_summary = self.error_analyzer.get_error_summary(days)
        workflow_summary = self.workflow_analyzer.get_workflow_summary(days)

        comprehensive_report += f"""
- **Total Usage Events**: {usage_summary.total_events:,}
- **Success Rate**: {usage_summary.success_rate:.1%}
- **Average Execution Time**: {performance_summary.avg_execution_time:.3f}s
- **Reliability Score**: {error_summary.reliability_score:.1%}
- **Total Workflows**: {workflow_summary.total_workflows:,}
- **Unique Users**: {usage_summary.unique_users:,}

## Report Sections
1. [Usage Analysis](usage_report_{timestamp}.md)
2. [Performance Analysis](performance_report_{timestamp}.md)
3. [Reliability Analysis](reliability_report_{timestamp}.md)
4. [Workflow Analysis](workflow_report_{timestamp}.md)

## Key Insights
"""

        # Add key insights
        if usage_summary.estimator_usage:
            top_estimator = max(
                usage_summary.estimator_usage.items(), key=lambda x: x[1]
            )
            comprehensive_report += f"- Most popular estimator: {top_estimator[0]} ({top_estimator[1]:,} uses)\n"

        if performance_summary.bottleneck_estimators:
            comprehensive_report += f"- Performance bottleneck: {performance_summary.bottleneck_estimators[0]}\n"

        if error_summary.error_by_type:
            top_error_type = max(
                error_summary.error_by_type.items(), key=lambda x: x[1]
            )
            comprehensive_report += f"- Most common error type: {top_error_type[0]} ({top_error_type[1]:,} errors)\n"

        if workflow_summary.common_workflow_patterns:
            top_pattern = workflow_summary.common_workflow_patterns[0]
            comprehensive_report += f"- Most common workflow pattern: {top_pattern[0]} ({top_pattern[1]:,} workflows)\n"

        comprehensive_report += f"""
## Recommendations
"""

        # Add recommendations from all analyzers
        usage_recommendations = []
        performance_recommendations = []
        error_recommendations = self.error_analyzer.get_improvement_recommendations(
            days
        )
        workflow_recommendations = (
            self.workflow_analyzer.get_workflow_optimization_recommendations(days)
        )

        all_recommendations = (
            usage_recommendations
            + performance_recommendations
            + error_recommendations
            + workflow_recommendations
        )

        if all_recommendations:
            for i, recommendation in enumerate(all_recommendations[:10], 1):  # Top 10
                comprehensive_report += f"{i}. {recommendation}\n"
        else:
            comprehensive_report += "- No specific recommendations at this time.\n"

        # Save comprehensive report
        comprehensive_path = output_path / f"comprehensive_report_{timestamp}.md"
        with open(comprehensive_path, "w") as f:
            f.write(comprehensive_report)

        return comprehensive_report

    def create_visualizations(
        self, days: int = 30, output_dir: Optional[str] = None
    ) -> Dict[str, str]:
        """Create visualizations for analytics data"""
        if output_dir is None:
            output_dir = self.storage_path / "visualizations"

        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        plots = {}

        # Usage visualization
        usage_summary = self.usage_tracker.get_usage_summary(days)
        if usage_summary.estimator_usage:
            plt.figure(figsize=(12, 6))
            estimators = list(usage_summary.estimator_usage.keys())
            counts = list(usage_summary.estimator_usage.values())

            plt.bar(range(len(estimators)), counts)
            plt.xlabel("Estimators")
            plt.ylabel("Usage Count")
            plt.title(f"Estimator Usage (Last {days} days)")
            plt.xticks(range(len(estimators)), estimators, rotation=45, ha="right")
            plt.tight_layout()

            usage_plot_path = output_path / f"estimator_usage_{timestamp}.png"
            plt.savefig(usage_plot_path, dpi=300, bbox_inches="tight")
            plt.close()
            plots["estimator_usage"] = str(usage_plot_path)

        # Performance visualization
        performance_summary = self.performance_monitor.get_performance_summary(days)
        if performance_summary.total_executions > 0:
            plt.figure(figsize=(10, 6))

            # Create performance metrics bar chart
            metrics = ["Avg Time", "Min Time", "Max Time"]
            values = [
                performance_summary.avg_execution_time,
                performance_summary.min_execution_time,
                performance_summary.max_execution_time,
            ]

            plt.bar(metrics, values, color=["skyblue", "lightgreen", "lightcoral"])
            plt.ylabel("Execution Time (seconds)")
            plt.title(f"Performance Metrics (Last {days} days)")
            plt.tight_layout()

            perf_plot_path = output_path / f"performance_metrics_{timestamp}.png"
            plt.savefig(perf_plot_path, dpi=300, bbox_inches="tight")
            plt.close()
            plots["performance_metrics"] = str(perf_plot_path)

        # Error visualization
        error_summary = self.error_analyzer.get_error_summary(days)
        if error_summary.error_by_type:
            plt.figure(figsize=(10, 6))
            error_types = list(error_summary.error_by_type.keys())
            error_counts = list(error_summary.error_by_type.values())

            plt.pie(error_counts, labels=error_types, autopct="%1.1f%%", startangle=90)
            plt.title(f"Error Distribution by Type (Last {days} days)")
            plt.axis("equal")
            plt.tight_layout()

            error_plot_path = output_path / f"error_distribution_{timestamp}.png"
            plt.savefig(error_plot_path, dpi=300, bbox_inches="tight")
            plt.close()
            plots["error_distribution"] = str(error_plot_path)

        # Workflow visualization
        workflow_summary = self.workflow_analyzer.get_workflow_summary(days)
        if workflow_summary.workflow_complexity_distribution:
            plt.figure(figsize=(10, 6))
            complexities = list(
                workflow_summary.workflow_complexity_distribution.keys()
            )
            counts = list(workflow_summary.workflow_complexity_distribution.values())

            # Clean up complexity labels
            clean_labels = [c.replace("_", " ").title() for c in complexities]

            plt.bar(clean_labels, counts, color="lightblue")
            plt.xlabel("Workflow Complexity")
            plt.ylabel("Number of Workflows")
            plt.title(f"Workflow Complexity Distribution (Last {days} days)")
            plt.xticks(rotation=45, ha="right")
            plt.tight_layout()

            workflow_plot_path = output_path / f"workflow_complexity_{timestamp}.png"
            plt.savefig(workflow_plot_path, dpi=300, bbox_inches="tight")
            plt.close()
            plots["workflow_complexity"] = str(workflow_plot_path)

        return plots

    def export_all_data(
        self, output_dir: Optional[str] = None, days: int = 30
    ) -> Dict[str, str]:
        """Export all analytics data to files"""
        if output_dir is None:
            output_dir = self.storage_path / "exports"

        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        exports = {}

        # Export usage data
        usage_path = output_path / f"usage_data_{timestamp}.json"
        self.usage_tracker.export_summary(str(usage_path), days)
        exports["usage_data"] = str(usage_path)

        # Export performance data
        perf_path = output_path / f"performance_data_{timestamp}.json"
        self.performance_monitor.export_metrics(str(perf_path), days)
        exports["performance_data"] = str(perf_path)

        # Export error data
        error_path = output_path / f"error_data_{timestamp}.json"
        self.error_analyzer.export_errors(str(error_path), days)
        exports["error_data"] = str(error_path)

        # Export workflow data
        workflow_path = output_path / f"workflow_data_{timestamp}.json"
        self.workflow_analyzer.export_workflows(str(workflow_path), days)
        exports["workflow_data"] = str(workflow_path)

        return exports


# Global dashboard instance
_global_dashboard: Optional[AnalyticsDashboard] = None


def get_analytics_dashboard() -> AnalyticsDashboard:
    """Get the global analytics dashboard instance"""
    global _global_dashboard
    if _global_dashboard is None:
        _global_dashboard = AnalyticsDashboard()
    return _global_dashboard


def quick_analytics_summary(days: int = 30) -> str:
    """Get a quick summary of analytics data"""
    dashboard = get_analytics_dashboard()
    summary = dashboard.get_comprehensive_summary(days)

    quick_summary = f"""
📊 LRDBench Analytics Summary (Last {days} days)

📈 Usage:
   • Total Events: {summary['usage_summary'].total_events:,}
   • Success Rate: {summary['usage_summary'].success_rate:.1%}
   • Unique Users: {summary['usage_summary'].unique_users:,}

⚡ Performance:
   • Avg Execution Time: {summary['performance_summary'].avg_execution_time:.3f}s
   • Total Executions: {summary['performance_summary'].total_executions:,}
   • Trend: {summary['performance_summary'].performance_trend}

🛡️ Reliability:
   • Reliability Score: {summary['error_summary'].reliability_score:.1%}
   • Total Errors: {summary['error_summary'].total_errors:,}

🔄 Workflows:
   • Total Workflows: {summary['workflow_summary'].total_workflows:,}
   • Avg Duration: {summary['workflow_summary'].avg_workflow_duration:.1f}s
   • Avg Steps: {summary['workflow_summary'].avg_steps_per_workflow:.1f}
"""

    return quick_summary
