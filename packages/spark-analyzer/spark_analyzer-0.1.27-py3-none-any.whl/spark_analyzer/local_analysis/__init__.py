"""
Local Analysis Package for Spark Acceleration Analysis

This package provides local analysis capabilities for Spark job performance
and acceleration potential analysis.
"""

from .report_generator import generate_report, process_input_file

from .data_models import SparkDiagnosticsPayload, AccelerationAnalysis
from .metrics_analyzer import CostEstimatorMetricsAnalyzer

__all__ = [
    "generate_report", 
    "process_input_file",
    "SparkDiagnosticsPayload",
    "AccelerationAnalysis"
]
