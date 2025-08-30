from typing import Dict, List
from enum import Enum
from dataclasses import dataclass

from data_models import (
    WorkflowType, ExtractType, TransformType, LoadType, HudiMetadataType,
    SparkDiagnosticsPayload, SparkStage, WorkflowInfo, StageAcceleration,
    StageMetrics, WorkflowStats, AccelerationSummary, TotalMetrics,
    WorkflowDistribution, ExtractDistribution, TransformDistribution,
    LoadDistribution, HudiMetadataDistribution, AccelerationAnalysis,
    WorkflowBreakdown, ExtractBreakdown, TransformBreakdown, LoadBreakdown,
    HudiMetadataBreakdown
)
from workflow_classifier import CostEstimatorWorkflowClassifier, SubTypeMetrics


@dataclass
class ProductConfig:
    # Reduction ranges for different workflow types (HUDI)
    unknown_range: str = "33% - 50%"
    extract_scan_range: str = "40% - 60%"
    transform_operation_range: str = "40% - 50%"
    transform_join_range: str = "50% - 75%"
    load_upsert_range: str = "50% - 75%"
    load_insert_range: str = "50% - 90%"
    load_overwrite_range: str = "0% - 0%"  # No reduction
    load_indexing_range: str = "40% - 50%"
    metadata_operation_range: str = "0% - 0%"  # No reduction 


class CostEstimatorMetricsAnalyzer:
    MIN_PERCENTAGE = 0.0
    MAX_PERCENTAGE = 100.0
    FULL_RATIO = 1.0
    ZERO_VALUE = 0.0

    def __init__(self, metrics_data: SparkDiagnosticsPayload, product_config: ProductConfig = None):
        self.metrics_data = metrics_data
        self.product_config = product_config or ProductConfig()
        self.workflow_classifier = CostEstimatorWorkflowClassifier().analyze_stages(metrics_data.stages)

    @staticmethod
    def safe_division(numerator: float, denominator: float, default_value: float) -> float:
        return numerator / denominator if denominator > 0 else default_value

    @staticmethod
    def factor_to_range(factor: float) -> str:
        lower = max(0.6, factor - 0.4) 
        upper = factor + 0.4
        return f"{lower:.1f}x - {upper:.1f}x"

    @staticmethod
    def parse_reduction_range(reduction_range: str) -> tuple[float, float]:
        try:
            parts = reduction_range.replace('%', '').split(' - ')
            if len(parts) == 2:
                min_percentage = float(parts[0].strip()) / 100.0
                max_percentage = float(parts[1].strip()) / 100.0
                min_factor = 1.0 / (1.0 - min_percentage) if min_percentage < 1.0 else 1.0
                max_factor = 1.0 / (1.0 - max_percentage) if max_percentage < 1.0 else 1.0
                return min_factor, max_factor
        except (ValueError, AttributeError):
            pass
        return 1.0, 1.0

    @staticmethod
    def calculate_projected_range(used_core_ms: int, reduction_range: str) -> str:
        if used_core_ms <= 0:
            return "0 - 0 ms"
        
        try:
            parts = reduction_range.replace('%', '').split(' - ')
            if len(parts) == 2:
                min_percentage = float(parts[0].strip()) / 100.0
                max_percentage = float(parts[1].strip()) / 100.0
                
                if max_percentage >= 1.0:
                    min_projected = 0 
                else:
                    max_factor = 1.0 / (1.0 - max_percentage)
                    min_projected = int(used_core_ms / max_factor)
                
                if min_percentage >= 1.0:
                    max_projected = 0  
                else:
                    min_factor = 1.0 / (1.0 - min_percentage)
                    max_projected = int(used_core_ms / min_factor) 
                
                return f"{min_projected} - {max_projected} ms"
            
            return "0 - 0 ms"
        except (ValueError, AttributeError):
            return "0 - 0 ms"

    def calculate_stage_reduction(self, stage: SparkStage) -> StageAcceleration:
        if not stage.workflow_info:
            reduction_range = "0% - 0%"
            return StageAcceleration(
                factor=1.0, 
                projected_work_ms_with_acceleration=self.calculate_projected_range(0, reduction_range),
                acceleration_range=reduction_range
            )

        workflow_type = stage.workflow_info.type
        reduction_range = self._get_base_reduction_range(workflow_type)
        used_core_ms = self._calculate_used_core_ms(stage)
        reduction_factor = self._get_base_reduction_factor(workflow_type)

        return StageAcceleration(
            factor=reduction_factor,
            projected_work_ms_with_acceleration=self.calculate_projected_range(used_core_ms, reduction_range),
            acceleration_range=reduction_range
        )

    def _calculate_used_core_ms(self, stage: SparkStage) -> float:
        if stage.total_cores_available <= 0:
            return self.ZERO_VALUE
        return stage.cores_used_by_stage * stage.stage_duration_ms

    def _get_base_reduction_range(self, workflow_type: WorkflowType) -> str:
        if workflow_type == WorkflowType.WORKFLOW_TYPE_EXTRACT:
            return self.product_config.extract_scan_range
        elif workflow_type == WorkflowType.WORKFLOW_TYPE_TRANSFORM:
            return self.product_config.transform_operation_range
        elif workflow_type == WorkflowType.WORKFLOW_TYPE_LOAD:
            return self.product_config.load_upsert_range
        elif workflow_type == WorkflowType.WORKFLOW_TYPE_HUDI_METADATA:
            return self.product_config.metadata_operation_range
        else:
            return self.product_config.unknown_range

    def _get_base_reduction_factor(self, workflow_type: WorkflowType) -> float:
        reduction_range = self._get_base_reduction_range(workflow_type)
        min_factor, max_factor = self.parse_reduction_range(reduction_range)
        return (min_factor + max_factor) / 2.0

    def build_stage_metrics(self, stage: SparkStage, acceleration: StageAcceleration) -> StageMetrics:
        stage_duration_ms = stage.stage_duration_ms
        total_core_ms = stage.total_cores_available * stage_duration_ms
        used_core_ms = self._calculate_used_core_ms(stage)
        idle_core_ms = max(0, total_core_ms - used_core_ms)
        utilization_percentage = self.safe_division(
            stage.cores_used_by_stage, stage.total_cores_available, self.ZERO_VALUE
        ) * self.MAX_PERCENTAGE

        return StageMetrics(
            stage_id=stage.stage_id,
            workflow_info=stage.workflow_info or WorkflowInfo(type=WorkflowType.WORKFLOW_TYPE_UNKNOWN),
            duration_ms=int(stage_duration_ms),
            used_core_ms=int(used_core_ms),
            total_cores_available=stage.total_cores_available,
            cores_used=stage.cores_used_by_stage,
            total_core_ms=int(total_core_ms),
            idle_core_ms=int(idle_core_ms),
            acceleration=acceleration,
            utilization_percentage=utilization_percentage
        )

    def calculate_total_duration_ms(self) -> int:
        if (self.metrics_data.application_start_time_ms > 0 and 
            self.metrics_data.application_end_time_ms > 0 and
            self.metrics_data.application_end_time_ms > self.metrics_data.application_start_time_ms):
            return int(self.metrics_data.application_end_time_ms - self.metrics_data.application_start_time_ms)
        else:
            # Fallback: Use the latest stage completion time as application end time
            return self._calculate_duration_from_stage_times()
    
    def _calculate_duration_from_stage_times(self) -> int:
        if not self.metrics_data.stages:
            return 0
        
        import datetime
        
        earliest_submission = None
        latest_completion = None
        
        for stage in self.metrics_data.stages:
            # Parse submission time
            if stage.submission_time:
                try:
                    # Handle different time formats
                    if 'GMT' in stage.submission_time:
                        submission_time = datetime.datetime.strptime(
                            stage.submission_time, "%Y-%m-%dT%H:%M:%S.%fGMT"
                        )
                    elif 'Z' in stage.submission_time:
                        submission_time = datetime.datetime.strptime(
                            stage.submission_time.replace('Z', '+0000'), 
                            "%Y-%m-%dT%H:%M:%S.%f%z"
                        )
                    else:
                        submission_time = datetime.datetime.fromisoformat(stage.submission_time.replace('Z', '+00:00'))
                    
                    if earliest_submission is None or submission_time < earliest_submission:
                        earliest_submission = submission_time
                except (ValueError, AttributeError):
                    continue
            
            # Parse completion time
            if stage.completion_time:
                try:
                    # Handle different time formats
                    if 'GMT' in stage.completion_time:
                        completion_time = datetime.datetime.strptime(
                            stage.completion_time, "%Y-%m-%dT%H:%M:%S.%fGMT"
                        )
                    elif 'Z' in stage.completion_time:
                        completion_time = datetime.datetime.strptime(
                            stage.completion_time.replace('Z', '+0000'), 
                            "%Y-%m-%dT%H:%M:%S.%f%z"
                        )
                    else:
                        completion_time = datetime.datetime.fromisoformat(stage.completion_time.replace('Z', '+00:00'))
                    
                    if latest_completion is None or completion_time > latest_completion:
                        latest_completion = completion_time
                except (ValueError, AttributeError):
                    continue
        
        # Calculate duration if we have both times
        if earliest_submission and latest_completion:
            duration = latest_completion - earliest_submission
            return int(duration.total_seconds() * 1000)  # Convert to milliseconds
        
        # Final fallback: sum of stage durations
        return int(sum(stage.stage_duration_ms for stage in self.metrics_data.stages))

    def calculate_total_core_ms(self) -> float:
        return sum(
            stage.total_cores_available * stage.stage_duration_ms
            for stage in self.metrics_data.stages
        )

    def calculate_idle_core_ms(self) -> float:
        return sum(
            max(0, stage.total_cores_available - stage.cores_used_by_stage) * stage.stage_duration_ms
            for stage in self.metrics_data.stages
        )

    def build_workflow_stats(
        self, workflow_type: WorkflowType, workflow_utilizations: Dict[WorkflowType, List[float]]
    ) -> WorkflowStats:
        total_duration = self.workflow_classifier.get_duration(workflow_type)
        used_core_ms = self.workflow_classifier.get_used_core_ms(workflow_type)
        acceleration_range = self._get_base_reduction_range(workflow_type)

        projected_work_ms_with_acceleration = self.calculate_projected_range(used_core_ms, acceleration_range)

        average_utilization = self.ZERO_VALUE
        utilizations = workflow_utilizations.get(workflow_type, [])
        if utilizations:
            average_utilization = sum(utilizations) / len(utilizations)

        return WorkflowStats(
            total_stages=self.workflow_classifier.get_stage_count(workflow_type),
            total_duration_ms=int(total_duration),
            used_core_ms=int(used_core_ms),
            total_core_ms=int(self.workflow_classifier.get_total_core_ms(workflow_type)),
            idle_core_ms=int(self.workflow_classifier.get_idle_core_ms(workflow_type)),
            projected_work_ms_with_acceleration=projected_work_ms_with_acceleration,
            acceleration_range=acceleration_range,
            average_utilization_percentage=average_utilization
        )

    def calculate_overall_acceleration_range(self, stage_metrics_list: List[StageMetrics]) -> str:
        if not stage_metrics_list:
            return "0% - 0%"
        
        total_used_core_ms = sum(stage.used_core_ms for stage in stage_metrics_list)
        if total_used_core_ms == 0:
            return "0% - 0%"
        
        weighted_min_sum = 0.0
        weighted_max_sum = 0.0
        
        for stage in stage_metrics_list:
            weight = stage.used_core_ms / total_used_core_ms
            try:
                parts = stage.acceleration.acceleration_range.replace('%', '').split(' - ')
                if len(parts) == 2:
                    min_percentage = float(parts[0].strip())
                    max_percentage = float(parts[1].strip())
                    weighted_min_sum += min_percentage * weight
                    weighted_max_sum += max_percentage * weight
            except (ValueError, AttributeError):
                continue
        
        return f"{weighted_min_sum:.0f}% - {weighted_max_sum:.0f}%"

    def calculate_overall_projected_range(self, stage_metrics_list: List[StageMetrics]) -> str:
        if not stage_metrics_list:
            return "0 - 0 ms"
        
        total_min_projected = 0
        total_max_projected = 0
        
        for stage in stage_metrics_list:
            projected_range = stage.acceleration.projected_work_ms_with_acceleration
            try:
                parts = projected_range.replace(' ms', '').split(' - ')
                if len(parts) == 2:
                    min_projected = int(parts[0].strip())
                    max_projected = int(parts[1].strip())
                    total_min_projected += min_projected
                    total_max_projected += max_projected
            except (ValueError, AttributeError):
                total_min_projected += stage.used_core_ms
                total_max_projected += stage.used_core_ms
        
        return f"{total_min_projected} - {total_max_projected} ms"

    def generate_acceleration_analysis(self) -> AccelerationAnalysis:
        if not self.metrics_data.stages:
            raise ValueError("No stages available for analysis")

        total_duration_ms = self.calculate_total_duration_ms()
        
        total_used_core_ms = 0.0

        workflow_utilizations: Dict[WorkflowType, List[float]] = {
            workflow_type: [] for workflow_type in WorkflowType
        }

        stage_metrics_list = []
        for stage in self.metrics_data.stages:
            acceleration = self.calculate_stage_reduction(stage)
            stage_metrics = self.build_stage_metrics(stage, acceleration)
            stage_metrics_list.append(stage_metrics)

            if stage.workflow_info:
                workflow_type = stage.workflow_info.type
                workflow_utilizations[workflow_type].append(stage_metrics.utilization_percentage)

        total_used_core_ms = (
            self.workflow_classifier.get_used_core_ms(WorkflowType.WORKFLOW_TYPE_EXTRACT) +
            self.workflow_classifier.get_used_core_ms(WorkflowType.WORKFLOW_TYPE_TRANSFORM) +
            self.workflow_classifier.get_used_core_ms(WorkflowType.WORKFLOW_TYPE_LOAD) +
            self.workflow_classifier.get_used_core_ms(WorkflowType.WORKFLOW_TYPE_HUDI_METADATA) +
            self.workflow_classifier.get_used_core_ms(WorkflowType.WORKFLOW_TYPE_UNKNOWN)
        )

        workflow_distribution = WorkflowDistribution(
            unknown_percentage=self.workflow_classifier.get_percentage(WorkflowType.WORKFLOW_TYPE_UNKNOWN),
            extract_percentage=self.workflow_classifier.get_percentage(WorkflowType.WORKFLOW_TYPE_EXTRACT),
            transform_percentage=self.workflow_classifier.get_percentage(WorkflowType.WORKFLOW_TYPE_TRANSFORM),
            load_percentage=self.workflow_classifier.get_percentage(WorkflowType.WORKFLOW_TYPE_LOAD),
            metadata_percentage=self.workflow_classifier.get_percentage(WorkflowType.WORKFLOW_TYPE_HUDI_METADATA),
            extract_distribution=ExtractDistribution(
                scan_percentage=self.workflow_classifier.get_sub_type_percentage(
                    WorkflowType.WORKFLOW_TYPE_EXTRACT, ExtractType.EXTRACT_TYPE_SCAN
                )
            ),
            transform_distribution=TransformDistribution(
                operation_percentage=self.workflow_classifier.get_sub_type_percentage(
                    WorkflowType.WORKFLOW_TYPE_TRANSFORM, TransformType.TRANSFORM_TYPE_OPERATION
                ),
                join_percentage=self.workflow_classifier.get_sub_type_percentage(
                    WorkflowType.WORKFLOW_TYPE_TRANSFORM, TransformType.TRANSFORM_TYPE_JOIN
                )
            ),
            load_distribution=LoadDistribution(
                upsert_percentage=self.workflow_classifier.get_sub_type_percentage(
                    WorkflowType.WORKFLOW_TYPE_LOAD, LoadType.LOAD_TYPE_UPSERT
                ),
                insert_percentage=self.workflow_classifier.get_sub_type_percentage(
                    WorkflowType.WORKFLOW_TYPE_LOAD, LoadType.LOAD_TYPE_INSERT
                ),
                overwrite_percentage=self.workflow_classifier.get_sub_type_percentage(
                    WorkflowType.WORKFLOW_TYPE_LOAD, LoadType.LOAD_TYPE_OVERWRITE
                ),
                indexing_percentage=self.workflow_classifier.get_sub_type_percentage(
                    WorkflowType.WORKFLOW_TYPE_LOAD, LoadType.LOAD_TYPE_INDEXING
                )
            ),
            metadata_distribution=HudiMetadataDistribution(
                operation_percentage=self.workflow_classifier.get_sub_type_percentage(
                    WorkflowType.WORKFLOW_TYPE_HUDI_METADATA, HudiMetadataType.HUDI_METADATA_TYPE_OPERATION
                )
            )
        )

        total_metrics = TotalMetrics(
            total_duration_ms=total_duration_ms,
            used_core_ms=int(total_used_core_ms),
            total_core_ms=int(self.calculate_total_core_ms()),
            idle_core_ms=int(self.calculate_idle_core_ms()),
            workflow_distribution=workflow_distribution
        )

        overall_acceleration_range = self.calculate_overall_acceleration_range(stage_metrics_list)
        overall_projected_range = self.calculate_overall_projected_range(stage_metrics_list)

        acceleration_summary = AccelerationSummary(
            projected_work_ms_with_acceleration=overall_projected_range,
            acceleration_range=overall_acceleration_range,
            projected_duration_ms=overall_projected_range
        )

        workflow_breakdown = WorkflowBreakdown(
            unknown=self.build_workflow_stats(WorkflowType.WORKFLOW_TYPE_UNKNOWN, workflow_utilizations),
            extract=self.build_workflow_stats(WorkflowType.WORKFLOW_TYPE_EXTRACT, workflow_utilizations),
            transform=self.build_workflow_stats(WorkflowType.WORKFLOW_TYPE_TRANSFORM, workflow_utilizations),
            load=self.build_workflow_stats(WorkflowType.WORKFLOW_TYPE_LOAD, workflow_utilizations),
            metadata=self.build_workflow_stats(WorkflowType.WORKFLOW_TYPE_HUDI_METADATA, workflow_utilizations),
            extract_breakdown=ExtractBreakdown(
                scan=self.build_sub_type_workflow_stats(WorkflowType.WORKFLOW_TYPE_EXTRACT, ExtractType.EXTRACT_TYPE_SCAN)
            ),
            transform_breakdown=TransformBreakdown(
                operation=self.build_sub_type_workflow_stats(WorkflowType.WORKFLOW_TYPE_TRANSFORM, TransformType.TRANSFORM_TYPE_OPERATION),
                join=self.build_sub_type_workflow_stats(WorkflowType.WORKFLOW_TYPE_TRANSFORM, TransformType.TRANSFORM_TYPE_JOIN)
            ),
            load_breakdown=LoadBreakdown(
                upsert=self.build_sub_type_workflow_stats(WorkflowType.WORKFLOW_TYPE_LOAD, LoadType.LOAD_TYPE_UPSERT),
                insert=self.build_sub_type_workflow_stats(WorkflowType.WORKFLOW_TYPE_LOAD, LoadType.LOAD_TYPE_INSERT),
                overwrite=self.build_sub_type_workflow_stats(WorkflowType.WORKFLOW_TYPE_LOAD, LoadType.LOAD_TYPE_OVERWRITE),
                indexing=self.build_sub_type_workflow_stats(WorkflowType.WORKFLOW_TYPE_LOAD, LoadType.LOAD_TYPE_INDEXING)
            ),
            metadata_breakdown=HudiMetadataBreakdown(
                operation=self.build_sub_type_workflow_stats(WorkflowType.WORKFLOW_TYPE_HUDI_METADATA, HudiMetadataType.HUDI_METADATA_TYPE_OPERATION)
            )
        )

        return AccelerationAnalysis(
            application_id=self.metrics_data.application_id,
            total_metrics=total_metrics,
            acceleration_summary=acceleration_summary,
            workflow_breakdown=workflow_breakdown,
            stages=stage_metrics_list
        )

    def build_sub_type_workflow_stats(
        self, workflow_type: WorkflowType, sub_type: Enum
    ) -> WorkflowStats:
        metrics = self.workflow_classifier.get_sub_type_metrics(workflow_type, sub_type)
        acceleration_range = self._get_base_reduction_range(workflow_type)

        projected_work_ms_with_acceleration = self.calculate_projected_range(metrics.used_core_ms, acceleration_range)

        average_utilization_percentage = self.ZERO_VALUE
        if metrics.total_core_ms > 0:
            average_utilization_percentage = (metrics.used_core_ms / metrics.total_core_ms) * self.MAX_PERCENTAGE

        return WorkflowStats(
            total_stages=metrics.count,
            total_duration_ms=int(metrics.duration),
            used_core_ms=int(metrics.used_core_ms),
            total_core_ms=int(metrics.total_core_ms),
            idle_core_ms=int(metrics.idle_core_ms),
            projected_work_ms_with_acceleration=projected_work_ms_with_acceleration,
            acceleration_range=acceleration_range,
            average_utilization_percentage=average_utilization_percentage
        ) 