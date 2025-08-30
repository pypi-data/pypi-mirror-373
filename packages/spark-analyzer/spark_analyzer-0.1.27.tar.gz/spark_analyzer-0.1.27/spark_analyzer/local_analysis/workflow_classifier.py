from dataclasses import dataclass
from typing import Dict, List
from enum import Enum
from collections import defaultdict

from data_models import (
    WorkflowType, ExtractType, TransformType, LoadType, HudiMetadataType,
    WorkflowInfo, SparkStage
)


@dataclass
class SubTypeMetrics:
    count: int
    duration: float
    used_core_ms: float
    total_core_ms: float
    idle_core_ms: float

    @classmethod
    def empty(cls) -> 'SubTypeMetrics':
        return cls(0, 0.0, 0.0, 0.0, 0.0)


class CostEstimatorWorkflowClassifier:
    def __init__(self):
        self.stage_counts: Dict[WorkflowType, int] = defaultdict(int)
        self.stage_durations: Dict[WorkflowType, float] = defaultdict(float)
        self.work_ms: Dict[WorkflowType, float] = defaultdict(float)
        self.total_core_ms: Dict[WorkflowType, float] = defaultdict(float)
        self.used_core_ms: Dict[WorkflowType, float] = defaultdict(float)
        self.idle_core_ms: Dict[WorkflowType, float] = defaultdict(float)
        self.total_duration: float = 0.0

        self.extract_metrics: Dict[ExtractType, SubTypeMetrics] = defaultdict(SubTypeMetrics.empty)
        self.transform_metrics: Dict[TransformType, SubTypeMetrics] = defaultdict(SubTypeMetrics.empty)
        self.load_metrics: Dict[LoadType, SubTypeMetrics] = defaultdict(SubTypeMetrics.empty)
        self.hudi_metadata_metrics: Dict[HudiMetadataType, SubTypeMetrics] = defaultdict(SubTypeMetrics.empty)

    def analyze_stages(self, stages: List[SparkStage]) -> 'CostEstimatorWorkflowClassifier':
        self._reset_metrics()

        for stage in stages:
            if not stage.workflow_info:
                continue

            workflow_info = stage.workflow_info
            workflow_type = workflow_info.type

            self.stage_counts[workflow_type] += 1

            stage_duration = stage.stage_duration_ms
            self.stage_durations[workflow_type] += stage_duration
            self.total_duration += stage_duration

            cores_used = stage.cores_used_by_stage
            stage_work_ms = cores_used * stage_duration
            self.work_ms[workflow_type] += stage_work_ms

            stage_total_core_ms = stage.total_cores_available * stage_duration
            stage_used_core_ms = cores_used * stage_duration
            stage_idle_core_ms = max(0, stage.total_cores_available - cores_used) * stage_duration

            self.total_core_ms[workflow_type] += stage_total_core_ms
            self.used_core_ms[workflow_type] += stage_used_core_ms
            self.idle_core_ms[workflow_type] += stage_idle_core_ms

            self._analyze_sub_types(
                workflow_info, stage_duration, stage_used_core_ms,
                stage_total_core_ms, stage_idle_core_ms
            )

        return self

    def _analyze_sub_types(
        self,
        workflow_info: WorkflowInfo,
        stage_duration: float,
        stage_used_core_ms: float,
        stage_total_core_ms: float,
        stage_idle_core_ms: float
    ):
        workflow_type = workflow_info.type

        if workflow_type == WorkflowType.WORKFLOW_TYPE_EXTRACT:
            if workflow_info.extract_type:
                self._update_sub_type_metrics(
                    self.extract_metrics,
                    workflow_info.extract_type,
                    stage_duration,
                    stage_used_core_ms,
                    stage_total_core_ms,
                    stage_idle_core_ms
                )

        elif workflow_type == WorkflowType.WORKFLOW_TYPE_TRANSFORM:
            if workflow_info.transform_type:
                self._update_sub_type_metrics(
                    self.transform_metrics,
                    workflow_info.transform_type,
                    stage_duration,
                    stage_used_core_ms,
                    stage_total_core_ms,
                    stage_idle_core_ms
                )

        elif workflow_type == WorkflowType.WORKFLOW_TYPE_LOAD:
            if workflow_info.load_type:
                self._update_sub_type_metrics(
                    self.load_metrics,
                    workflow_info.load_type,
                    stage_duration,
                    stage_used_core_ms,
                    stage_total_core_ms,
                    stage_idle_core_ms
                )

        elif workflow_type == WorkflowType.WORKFLOW_TYPE_HUDI_METADATA:
            if workflow_info.metadata_type:
                self._update_sub_type_metrics(
                    self.hudi_metadata_metrics,
                    workflow_info.metadata_type,
                    stage_duration,
                    stage_used_core_ms,
                    stage_total_core_ms,
                    stage_idle_core_ms
                )

    def _update_sub_type_metrics(
        self,
        metrics_map: Dict[Enum, SubTypeMetrics],
        sub_type: Enum,
        stage_duration: float,
        stage_used_core_ms: float,
        stage_total_core_ms: float,
        stage_idle_core_ms: float
    ):
        current_metrics = metrics_map.get(sub_type, SubTypeMetrics.empty())

        updated_metrics = SubTypeMetrics(
            count=current_metrics.count + 1,
            duration=current_metrics.duration + stage_duration,
            used_core_ms=current_metrics.used_core_ms + stage_used_core_ms,
            total_core_ms=current_metrics.total_core_ms + stage_total_core_ms,
            idle_core_ms=current_metrics.idle_core_ms + stage_idle_core_ms
        )

        metrics_map[sub_type] = updated_metrics

    def get_percentage(self, workflow_type: WorkflowType) -> float:
        type_duration = self.stage_durations.get(workflow_type, 0.0)
        return (type_duration / self.total_duration * 100.0) if self.total_duration > 0 else 0.0

    def get_stage_count(self, workflow_type: WorkflowType) -> int:
        return self.stage_counts.get(workflow_type, 0)

    def get_duration(self, workflow_type: WorkflowType) -> float:
        return self.stage_durations.get(workflow_type, 0.0)

    def get_work_ms(self, workflow_type: WorkflowType) -> float:
        return self.work_ms.get(workflow_type, 0.0)

    def get_total_core_ms(self, workflow_type: WorkflowType) -> float:
        return self.total_core_ms.get(workflow_type, 0.0)

    def get_used_core_ms(self, workflow_type: WorkflowType) -> float:
        return self.used_core_ms.get(workflow_type, 0.0)

    def get_idle_core_ms(self, workflow_type: WorkflowType) -> float:
        return self.idle_core_ms.get(workflow_type, 0.0)

    def get_sub_type_metrics(self, workflow_type: WorkflowType, sub_type: Enum) -> SubTypeMetrics:
        if workflow_type == WorkflowType.WORKFLOW_TYPE_EXTRACT:
            return self.extract_metrics.get(sub_type, SubTypeMetrics.empty())
        elif workflow_type == WorkflowType.WORKFLOW_TYPE_TRANSFORM:
            return self.transform_metrics.get(sub_type, SubTypeMetrics.empty())
        elif workflow_type == WorkflowType.WORKFLOW_TYPE_LOAD:
            return self.load_metrics.get(sub_type, SubTypeMetrics.empty())
        elif workflow_type == WorkflowType.WORKFLOW_TYPE_HUDI_METADATA:
            return self.hudi_metadata_metrics.get(sub_type, SubTypeMetrics.empty())
        else:
            return SubTypeMetrics.empty()

    def get_sub_type_percentage(self, workflow_type: WorkflowType, sub_type: Enum) -> float:
        metrics = self.get_sub_type_metrics(workflow_type, sub_type)
        total_workflow_duration = self.stage_durations.get(workflow_type, 0.0)
        return (metrics.duration / total_workflow_duration * 100.0) if total_workflow_duration > 0 else 0.0

    def _reset_metrics(self):
        self.stage_counts.clear()
        self.stage_durations.clear()
        self.work_ms.clear()
        self.total_core_ms.clear()
        self.used_core_ms.clear()
        self.idle_core_ms.clear()
        self.total_duration = 0.0

        self.extract_metrics.clear()
        self.transform_metrics.clear()
        self.load_metrics.clear()
        self.hudi_metadata_metrics.clear() 