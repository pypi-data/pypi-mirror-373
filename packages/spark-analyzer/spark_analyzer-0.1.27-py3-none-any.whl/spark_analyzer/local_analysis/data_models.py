from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional, Dict, Any


class WorkflowType(Enum):
    WORKFLOW_TYPE_INVALID = 0
    WORKFLOW_TYPE_UNKNOWN = 1
    WORKFLOW_TYPE_EXTRACT = 2
    WORKFLOW_TYPE_TRANSFORM = 3
    WORKFLOW_TYPE_LOAD = 4
    WORKFLOW_TYPE_HUDI_METADATA = 5


class ExtractType(Enum):
    EXTRACT_TYPE_INVALID = 0
    EXTRACT_TYPE_SCAN = 1


class TransformType(Enum):
    TRANSFORM_TYPE_INVALID = 0
    TRANSFORM_TYPE_OPERATION = 1
    TRANSFORM_TYPE_JOIN = 2


class LoadType(Enum):
    LOAD_TYPE_INVALID = 0
    LOAD_TYPE_UPSERT = 1
    LOAD_TYPE_INSERT = 2
    LOAD_TYPE_OVERWRITE = 3
    LOAD_TYPE_INDEXING = 4


class HudiMetadataType(Enum):
    HUDI_METADATA_TYPE_INVALID = 0
    HUDI_METADATA_TYPE_OPERATION = 1


class StorageFormat(Enum):
    STORAGE_FORMAT_INVALID = 0
    STORAGE_FORMAT_UNKNOWN = 1
    STORAGE_FORMAT_HUDI = 2
    STORAGE_FORMAT_ICEBERG = 3
    STORAGE_FORMAT_DELTA = 4
    STORAGE_FORMAT_PARQUET = 5


@dataclass
class WorkflowInfo:
    type: WorkflowType
    storage_format: StorageFormat = StorageFormat.STORAGE_FORMAT_UNKNOWN
    custom_info: str = ""
    extract_type: Optional[ExtractType] = None
    transform_type: Optional[TransformType] = None
    load_type: Optional[LoadType] = None
    metadata_type: Optional[HudiMetadataType] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'WorkflowInfo':
        workflow_type = WorkflowType[data.get('type', 'WORKFLOW_TYPE_UNKNOWN')]
        storage_format = StorageFormat[data.get('storage_format', 'STORAGE_FORMAT_UNKNOWN')]
        
        extract_type = None
        transform_type = None
        load_type = None
        metadata_type = None
        
        if 'extract_type' in data:
            extract_type = ExtractType[data['extract_type']]
        if 'transform_type' in data:
            transform_type = TransformType[data['transform_type']]
        if 'load_type' in data:
            load_type = LoadType[data['load_type']]
        if 'metadata_type' in data:
            metadata_type = HudiMetadataType[data['metadata_type']]
        
        return cls(
            type=workflow_type,
            storage_format=storage_format,
            custom_info=data.get('custom_info', ''),
            extract_type=extract_type,
            transform_type=transform_type,
            load_type=load_type,
            metadata_type=metadata_type
        )


@dataclass
class SparkExecutor:
    executor_id: str
    is_active: bool
    total_cores: int
    created_at: str = ""
    removed_at: str = ""

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SparkExecutor':
        return cls(
            executor_id=data['executor_id'],
            is_active=data.get('is_active', False),
            total_cores=data.get('total_cores', 0),
            created_at=data.get('add_time', ''),
            removed_at=data.get('remove_time', '')
        )


@dataclass
class SparkStage:
    stage_id: int
    application_id: str
    stage_name: str
    stage_description: str
    stage_details: str
    num_tasks: int
    num_executors_used: int
    used_executor_ids: List[str] = field(default_factory=list)
    total_active_executors: int = 0
    active_executor_ids: List[str] = field(default_factory=list)
    cores_used_by_stage: float = 0.0
    total_cores_available: int = 0
    submission_time: str = ""
    completion_time: str = ""
    executor_run_time_ms: int = 0
    stage_duration_ms: int = 0
    workflow_info: Optional[WorkflowInfo] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SparkStage':
        workflow_info = None
        if 'workflow_info' in data:
            workflow_info = WorkflowInfo.from_dict(data['workflow_info'])
        
        return cls(
            stage_id=data['stage_id'],
            application_id=data['application_id'],
            stage_name=data['stage_name'],
            stage_description=data.get('stage_description', ''),
            stage_details=data.get('stage_details', ''),
            num_tasks=data.get('num_tasks', 0),
            num_executors_used=data.get('num_executors_used', 0),
            used_executor_ids=data.get('used_executor_ids', []),
            total_active_executors=data.get('total_active_executors', 0),
            active_executor_ids=data.get('active_executor_ids', []),
            cores_used_by_stage=data.get('cores_used_by_stage', 0.0),
            total_cores_available=data.get('total_cores_available', 0),
            submission_time=data.get('submission_time', ''),
            completion_time=data.get('completion_time', ''),
            executor_run_time_ms=data.get('executor_run_time_ms', 0),
            stage_duration_ms=data.get('stage_duration_ms', 0),
            workflow_info=workflow_info
        )


@dataclass
class SparkDiagnosticsPayload:
    application_id: str
    total_executors: int
    total_cores: int
    application_start_time_ms: int
    application_end_time_ms: int
    executors: List[SparkExecutor] = field(default_factory=list)
    stages: List[SparkStage] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SparkDiagnosticsPayload':
        executors = [SparkExecutor.from_dict(exec_data) for exec_data in data.get('executors', [])]
        stages = [SparkStage.from_dict(stage_data) for stage_data in data.get('stages', [])]
        
        return cls(
            application_id=data['application_id'],
            total_executors=data.get('total_executors', 0),
            total_cores=data.get('total_cores', 0),
            application_start_time_ms=data.get('application_start_time_ms', 0),
            application_end_time_ms=data.get('application_end_time_ms', 0),
            executors=executors,
            stages=stages
        )


@dataclass
class StageAcceleration:
    factor: float
    projected_work_ms_with_acceleration: str
    acceleration_range: str


@dataclass
class StageMetrics:
    stage_id: int
    workflow_info: WorkflowInfo
    duration_ms: int
    used_core_ms: int
    total_cores_available: int
    cores_used: float
    total_core_ms: int
    idle_core_ms: int
    acceleration: StageAcceleration
    utilization_percentage: float


@dataclass
class WorkflowStats:
    total_stages: int
    total_duration_ms: int
    used_core_ms: int
    total_core_ms: int
    idle_core_ms: int
    projected_work_ms_with_acceleration: str
    acceleration_range: str
    average_utilization_percentage: float


@dataclass
class ExtractDistribution:
    scan_percentage: float = 0.0


@dataclass
class TransformDistribution:
    operation_percentage: float = 0.0
    join_percentage: float = 0.0


@dataclass
class LoadDistribution:
    upsert_percentage: float = 0.0
    insert_percentage: float = 0.0
    overwrite_percentage: float = 0.0
    indexing_percentage: float = 0.0


@dataclass
class HudiMetadataDistribution:
    operation_percentage: float = 0.0


@dataclass
class ExtractBreakdown:
    scan: WorkflowStats


@dataclass
class TransformBreakdown:
    operation: WorkflowStats
    join: WorkflowStats


@dataclass
class LoadBreakdown:
    upsert: WorkflowStats
    insert: WorkflowStats
    overwrite: WorkflowStats
    indexing: WorkflowStats


@dataclass
class HudiMetadataBreakdown:
    operation: WorkflowStats


@dataclass
class WorkflowBreakdown:
    unknown: WorkflowStats = field(default_factory=lambda: WorkflowStats(
        total_stages=0, total_duration_ms=0, used_core_ms=0, total_core_ms=0, 
        idle_core_ms=0, projected_work_ms_with_acceleration="0 - 0 ms", 
        acceleration_range="33% - 50%", average_utilization_percentage=0.0
    ))
    extract: WorkflowStats = field(default_factory=lambda: WorkflowStats(
        total_stages=0, total_duration_ms=0, used_core_ms=0, total_core_ms=0, 
        idle_core_ms=0, projected_work_ms_with_acceleration="0 - 0 ms", 
        acceleration_range="40% - 60%", average_utilization_percentage=0.0
    ))
    transform: WorkflowStats = field(default_factory=lambda: WorkflowStats(
        total_stages=0, total_duration_ms=0, used_core_ms=0, total_core_ms=0, 
        idle_core_ms=0, projected_work_ms_with_acceleration="0 - 0 ms", 
        acceleration_range="50% - 75%", average_utilization_percentage=0.0
    ))
    load: WorkflowStats = field(default_factory=lambda: WorkflowStats(
        total_stages=0, total_duration_ms=0, used_core_ms=0, total_core_ms=0, 
        idle_core_ms=0, projected_work_ms_with_acceleration="0 - 0 ms", 
        acceleration_range="50% - 75%", average_utilization_percentage=0.0
    ))
    metadata: WorkflowStats = field(default_factory=lambda: WorkflowStats(
        total_stages=0, total_duration_ms=0, used_core_ms=0, total_core_ms=0, 
        idle_core_ms=0, projected_work_ms_with_acceleration="0 - 0 ms", 
        acceleration_range="0% - 0%", average_utilization_percentage=0.0
    ))
    extract_breakdown: ExtractBreakdown = field(default_factory=lambda: ExtractBreakdown(
        scan=WorkflowStats(
            total_stages=0, total_duration_ms=0, used_core_ms=0, total_core_ms=0, 
            idle_core_ms=0, projected_work_ms_with_acceleration="0 - 0 ms", 
            acceleration_range="40% - 60%", average_utilization_percentage=0.0
        )
    ))
    transform_breakdown: TransformBreakdown = field(default_factory=lambda: TransformBreakdown(
        operation=WorkflowStats(
            total_stages=0, total_duration_ms=0, used_core_ms=0, total_core_ms=0, 
            idle_core_ms=0, projected_work_ms_with_acceleration="0 - 0 ms", 
            acceleration_range="40% - 50%", average_utilization_percentage=0.0
        ),
        join=WorkflowStats(
            total_stages=0, total_duration_ms=0, used_core_ms=0, total_core_ms=0, 
            idle_core_ms=0, projected_work_ms_with_acceleration="0 - 0 ms", 
            acceleration_range="50% - 75%", average_utilization_percentage=0.0
        )
    ))
    load_breakdown: LoadBreakdown = field(default_factory=lambda: LoadBreakdown(
        upsert=WorkflowStats(
            total_stages=0, total_duration_ms=0, used_core_ms=0, total_core_ms=0, 
            idle_core_ms=0, projected_work_ms_with_acceleration="0 - 0 ms", 
            acceleration_range="50% - 75%", average_utilization_percentage=0.0
        ),
        insert=WorkflowStats(
            total_stages=0, total_duration_ms=0, used_core_ms=0, total_core_ms=0, 
            idle_core_ms=0, projected_work_ms_with_acceleration="0 - 0 ms", 
            acceleration_range="50% - 90%", average_utilization_percentage=0.0
        ),
        overwrite=WorkflowStats(
            total_stages=0, total_duration_ms=0, used_core_ms=0, total_core_ms=0, 
            idle_core_ms=0, projected_work_ms_with_acceleration="0 - 0 ms", 
            acceleration_range="0% - 0%", average_utilization_percentage=0.0
        ),
        indexing=WorkflowStats(
            total_stages=0, total_duration_ms=0, used_core_ms=0, total_core_ms=0, 
            idle_core_ms=0, projected_work_ms_with_acceleration="0 - 0 ms", 
            acceleration_range="40% - 50%", average_utilization_percentage=0.0
        )
    ))
    metadata_breakdown: HudiMetadataBreakdown = field(default_factory=lambda: HudiMetadataBreakdown(
        operation=WorkflowStats(
            total_stages=0, total_duration_ms=0, used_core_ms=0, total_core_ms=0, 
            idle_core_ms=0, projected_work_ms_with_acceleration="0 - 0 ms", 
            acceleration_range="0% - 0%", average_utilization_percentage=0.0
        )
    ))


@dataclass
class WorkflowDistribution:
    unknown_percentage: float = 0.0
    extract_percentage: float = 0.0
    transform_percentage: float = 0.0
    load_percentage: float = 0.0
    metadata_percentage: float = 0.0
    extract_distribution: ExtractDistribution = field(default_factory=ExtractDistribution)
    transform_distribution: TransformDistribution = field(default_factory=TransformDistribution)
    load_distribution: LoadDistribution = field(default_factory=LoadDistribution)
    metadata_distribution: HudiMetadataDistribution = field(default_factory=HudiMetadataDistribution)
    workflow_breakdown: WorkflowBreakdown = field(default_factory=WorkflowBreakdown)


@dataclass
class AccelerationSummary:
    projected_work_ms_with_acceleration: str
    acceleration_range: str
    projected_duration_ms: str


@dataclass
class TotalMetrics:
    total_duration_ms: int
    used_core_ms: int
    total_core_ms: int
    idle_core_ms: int
    workflow_distribution: WorkflowDistribution


@dataclass
class AccelerationAnalysis:
    application_id: str
    total_metrics: TotalMetrics
    acceleration_summary: AccelerationSummary
    workflow_breakdown: WorkflowBreakdown
    stages: List[StageMetrics] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "application_id": self.application_id,
            "total_metrics": {
                "total_duration_ms": self.total_metrics.total_duration_ms,
                "used_core_ms": self.total_metrics.used_core_ms,
                "total_core_ms": self.total_metrics.total_core_ms,
                "idle_core_ms": self.total_metrics.idle_core_ms,
                "workflow_distribution": {
                    "unknown_percentage": self.total_metrics.workflow_distribution.unknown_percentage,
                    "extract_percentage": self.total_metrics.workflow_distribution.extract_percentage,
                    "transform_percentage": self.total_metrics.workflow_distribution.transform_percentage,
                    "load_percentage": self.total_metrics.workflow_distribution.load_percentage,
                    "metadata_percentage": self.total_metrics.workflow_distribution.metadata_percentage,
                    "extract_distribution": {
                        "scan_percentage": self.total_metrics.workflow_distribution.extract_distribution.scan_percentage
                    },
                    "transform_distribution": {
                        "operation_percentage": self.total_metrics.workflow_distribution.transform_distribution.operation_percentage,
                        "join_percentage": self.total_metrics.workflow_distribution.transform_distribution.join_percentage
                    },
                    "load_distribution": {
                        "upsert_percentage": self.total_metrics.workflow_distribution.load_distribution.upsert_percentage,
                        "insert_percentage": self.total_metrics.workflow_distribution.load_distribution.insert_percentage,
                        "overwrite_percentage": self.total_metrics.workflow_distribution.load_distribution.overwrite_percentage,
                        "indexing_percentage": self.total_metrics.workflow_distribution.load_distribution.indexing_percentage
                    },
                    "metadata_distribution": {
                        "operation_percentage": self.total_metrics.workflow_distribution.metadata_distribution.operation_percentage
                    }
                }
            },
            "acceleration_summary": {
                "projected_work_ms_with_acceleration": self.acceleration_summary.projected_work_ms_with_acceleration,
                "acceleration_range": self.acceleration_summary.acceleration_range,
                "projected_duration_ms": self.acceleration_summary.projected_duration_ms
            },
            "workflow_breakdown": {
                "unknown": {
                    "total_stages": self.workflow_breakdown.unknown.total_stages,
                    "total_duration_ms": self.workflow_breakdown.unknown.total_duration_ms,
                    "used_core_ms": self.workflow_breakdown.unknown.used_core_ms,
                    "total_core_ms": self.workflow_breakdown.unknown.total_core_ms,
                    "idle_core_ms": self.workflow_breakdown.unknown.idle_core_ms,
                    "projected_work_ms_with_acceleration": self.workflow_breakdown.unknown.projected_work_ms_with_acceleration,
                    "acceleration_range": self.workflow_breakdown.unknown.acceleration_range,
                    "average_utilization_percentage": self.workflow_breakdown.unknown.average_utilization_percentage
                },
                "extract": {
                    "total_stages": self.workflow_breakdown.extract.total_stages,
                    "total_duration_ms": self.workflow_breakdown.extract.total_duration_ms,
                    "used_core_ms": self.workflow_breakdown.extract.used_core_ms,
                    "total_core_ms": self.workflow_breakdown.extract.total_core_ms,
                    "idle_core_ms": self.workflow_breakdown.extract.idle_core_ms,
                    "projected_work_ms_with_acceleration": self.workflow_breakdown.extract.projected_work_ms_with_acceleration,
                    "acceleration_range": self.workflow_breakdown.extract.acceleration_range,
                    "average_utilization_percentage": self.workflow_breakdown.extract.average_utilization_percentage
                },
                "transform": {
                    "total_stages": self.workflow_breakdown.transform.total_stages,
                    "total_duration_ms": self.workflow_breakdown.transform.total_duration_ms,
                    "used_core_ms": self.workflow_breakdown.transform.used_core_ms,
                    "total_core_ms": self.workflow_breakdown.transform.total_core_ms,
                    "idle_core_ms": self.workflow_breakdown.transform.idle_core_ms,
                    "projected_work_ms_with_acceleration": self.workflow_breakdown.transform.projected_work_ms_with_acceleration,
                    "acceleration_range": self.workflow_breakdown.transform.acceleration_range,
                    "average_utilization_percentage": self.workflow_breakdown.transform.average_utilization_percentage
                },
                "load": {
                    "total_stages": self.workflow_breakdown.load.total_stages,
                    "total_duration_ms": self.workflow_breakdown.load.total_duration_ms,
                    "used_core_ms": self.workflow_breakdown.load.used_core_ms,
                    "total_core_ms": self.workflow_breakdown.load.total_core_ms,
                    "idle_core_ms": self.workflow_breakdown.load.idle_core_ms,
                    "projected_work_ms_with_acceleration": self.workflow_breakdown.load.projected_work_ms_with_acceleration,
                    "acceleration_range": self.workflow_breakdown.load.acceleration_range,
                    "average_utilization_percentage": self.workflow_breakdown.load.average_utilization_percentage
                },
                "metadata": {
                    "total_stages": self.workflow_breakdown.metadata.total_stages,
                    "total_duration_ms": self.workflow_breakdown.metadata.total_duration_ms,
                    "used_core_ms": self.workflow_breakdown.metadata.used_core_ms,
                    "total_core_ms": self.workflow_breakdown.metadata.total_core_ms,
                    "idle_core_ms": self.workflow_breakdown.metadata.idle_core_ms,
                    "projected_work_ms_with_acceleration": self.workflow_breakdown.metadata.projected_work_ms_with_acceleration,
                    "acceleration_range": self.workflow_breakdown.metadata.acceleration_range,
                    "average_utilization_percentage": self.workflow_breakdown.metadata.average_utilization_percentage
                },
                "extract_breakdown": {
                    "scan": {
                        "total_stages": self.workflow_breakdown.extract_breakdown.scan.total_stages,
                        "total_duration_ms": self.workflow_breakdown.extract_breakdown.scan.total_duration_ms,
                        "used_core_ms": self.workflow_breakdown.extract_breakdown.scan.used_core_ms,
                        "total_core_ms": self.workflow_breakdown.extract_breakdown.scan.total_core_ms,
                        "idle_core_ms": self.workflow_breakdown.extract_breakdown.scan.idle_core_ms,
                        "projected_work_ms_with_acceleration": self.workflow_breakdown.extract_breakdown.scan.projected_work_ms_with_acceleration,
                        "acceleration_range": self.workflow_breakdown.extract_breakdown.scan.acceleration_range,
                        "average_utilization_percentage": self.workflow_breakdown.extract_breakdown.scan.average_utilization_percentage
                    }
                },
                "transform_breakdown": {
                    "operation": {
                        "total_stages": self.workflow_breakdown.transform_breakdown.operation.total_stages,
                        "total_duration_ms": self.workflow_breakdown.transform_breakdown.operation.total_duration_ms,
                        "used_core_ms": self.workflow_breakdown.transform_breakdown.operation.used_core_ms,
                        "total_core_ms": self.workflow_breakdown.transform_breakdown.operation.total_core_ms,
                        "idle_core_ms": self.workflow_breakdown.transform_breakdown.operation.idle_core_ms,
                        "projected_work_ms_with_acceleration": self.workflow_breakdown.transform_breakdown.operation.projected_work_ms_with_acceleration,
                        "acceleration_range": self.workflow_breakdown.transform_breakdown.operation.acceleration_range,
                        "average_utilization_percentage": self.workflow_breakdown.transform_breakdown.operation.average_utilization_percentage
                    },
                    "join": {
                        "total_stages": self.workflow_breakdown.transform_breakdown.join.total_stages,
                        "total_duration_ms": self.workflow_breakdown.transform_breakdown.join.total_duration_ms,
                        "used_core_ms": self.workflow_breakdown.transform_breakdown.join.used_core_ms,
                        "total_core_ms": self.workflow_breakdown.transform_breakdown.join.total_core_ms,
                        "idle_core_ms": self.workflow_breakdown.transform_breakdown.join.idle_core_ms,
                        "projected_work_ms_with_acceleration": self.workflow_breakdown.transform_breakdown.join.projected_work_ms_with_acceleration,
                        "acceleration_range": self.workflow_breakdown.transform_breakdown.join.acceleration_range,
                        "average_utilization_percentage": self.workflow_breakdown.transform_breakdown.join.average_utilization_percentage
                    }
                },
                "load_breakdown": {
                    "upsert": {
                        "total_stages": self.workflow_breakdown.load_breakdown.upsert.total_stages,
                        "total_duration_ms": self.workflow_breakdown.load_breakdown.upsert.total_duration_ms,
                        "used_core_ms": self.workflow_breakdown.load_breakdown.upsert.used_core_ms,
                        "total_core_ms": self.workflow_breakdown.load_breakdown.upsert.total_core_ms,
                        "idle_core_ms": self.workflow_breakdown.load_breakdown.upsert.idle_core_ms,
                        "projected_work_ms_with_acceleration": self.workflow_breakdown.load_breakdown.upsert.projected_work_ms_with_acceleration,
                        "acceleration_range": self.workflow_breakdown.load_breakdown.upsert.acceleration_range,
                        "average_utilization_percentage": self.workflow_breakdown.load_breakdown.upsert.average_utilization_percentage
                    },
                    "insert": {
                        "total_stages": self.workflow_breakdown.load_breakdown.insert.total_stages,
                        "total_duration_ms": self.workflow_breakdown.load_breakdown.insert.total_duration_ms,
                        "used_core_ms": self.workflow_breakdown.load_breakdown.insert.used_core_ms,
                        "total_core_ms": self.workflow_breakdown.load_breakdown.insert.total_core_ms,
                        "idle_core_ms": self.workflow_breakdown.load_breakdown.insert.idle_core_ms,
                        "projected_work_ms_with_acceleration": self.workflow_breakdown.load_breakdown.insert.projected_work_ms_with_acceleration,
                        "acceleration_range": self.workflow_breakdown.load_breakdown.insert.acceleration_range,
                        "average_utilization_percentage": self.workflow_breakdown.load_breakdown.insert.average_utilization_percentage
                    },
                    "overwrite": {
                        "total_stages": self.workflow_breakdown.load_breakdown.overwrite.total_stages,
                        "total_duration_ms": self.workflow_breakdown.load_breakdown.overwrite.total_duration_ms,
                        "used_core_ms": self.workflow_breakdown.load_breakdown.overwrite.used_core_ms,
                        "total_core_ms": self.workflow_breakdown.load_breakdown.overwrite.total_core_ms,
                        "idle_core_ms": self.workflow_breakdown.load_breakdown.overwrite.idle_core_ms,
                        "projected_work_ms_with_acceleration": self.workflow_breakdown.load_breakdown.overwrite.projected_work_ms_with_acceleration,
                        "acceleration_range": self.workflow_breakdown.load_breakdown.overwrite.acceleration_range,
                        "average_utilization_percentage": self.workflow_breakdown.load_breakdown.overwrite.average_utilization_percentage
                    },
                    "indexing": {
                        "total_stages": self.workflow_breakdown.load_breakdown.indexing.total_stages,
                        "total_duration_ms": self.workflow_breakdown.load_breakdown.indexing.total_duration_ms,
                        "used_core_ms": self.workflow_breakdown.load_breakdown.indexing.used_core_ms,
                        "total_core_ms": self.workflow_breakdown.load_breakdown.indexing.total_core_ms,
                        "idle_core_ms": self.workflow_breakdown.load_breakdown.indexing.idle_core_ms,
                        "projected_work_ms_with_acceleration": self.workflow_breakdown.load_breakdown.indexing.projected_work_ms_with_acceleration,
                        "acceleration_range": self.workflow_breakdown.load_breakdown.indexing.acceleration_range,
                        "average_utilization_percentage": self.workflow_breakdown.load_breakdown.indexing.average_utilization_percentage
                    }
                },
                "metadata_breakdown": {
                    "operation": {
                        "total_stages": self.workflow_breakdown.metadata_breakdown.operation.total_stages,
                        "total_duration_ms": self.workflow_breakdown.metadata_breakdown.operation.total_duration_ms,
                        "used_core_ms": self.workflow_breakdown.metadata_breakdown.operation.used_core_ms,
                        "total_core_ms": self.workflow_breakdown.metadata_breakdown.operation.total_core_ms,
                        "idle_core_ms": self.workflow_breakdown.metadata_breakdown.operation.idle_core_ms,
                        "projected_work_ms_with_acceleration": self.workflow_breakdown.metadata_breakdown.operation.projected_work_ms_with_acceleration,
                        "acceleration_range": self.workflow_breakdown.metadata_breakdown.operation.acceleration_range,
                        "average_utilization_percentage": self.workflow_breakdown.metadata_breakdown.operation.average_utilization_percentage
                    }
                }
            },
            "stages": [
                {
                    "stage_id": stage.stage_id,
                    "workflow_info": {
                        "type": stage.workflow_info.type.name,
                        "storage_format": stage.workflow_info.storage_format.name,
                        "custom_info": stage.workflow_info.custom_info,
                        "load_type": stage.workflow_info.load_type.name if stage.workflow_info.load_type else None,
                        "extract_type": stage.workflow_info.extract_type.name if stage.workflow_info.extract_type else None,
                        "transform_type": stage.workflow_info.transform_type.name if stage.workflow_info.transform_type else None,
                        "metadata_type": stage.workflow_info.metadata_type.name if stage.workflow_info.metadata_type else None
                    },
                    "duration_ms": stage.duration_ms,
                    "used_core_ms": stage.used_core_ms,
                    "total_cores_available": stage.total_cores_available,
                    "cores_used": stage.cores_used,
                    "total_core_ms": stage.total_core_ms,
                    "idle_core_ms": stage.idle_core_ms,
                    "acceleration": {
                        "projected_work_ms_with_acceleration": stage.acceleration.projected_work_ms_with_acceleration,
                        "acceleration_range": stage.acceleration.acceleration_range
                    },
                    "utilization_percentage": stage.utilization_percentage
                }
                for stage in self.stages
            ]
        } 