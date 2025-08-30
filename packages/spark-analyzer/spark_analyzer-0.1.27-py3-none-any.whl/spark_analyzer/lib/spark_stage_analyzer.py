from .api_client import APIClient
import json
import logging
import requests
from typing import Optional, Dict, Any, List, Tuple, Set
from enum import Enum
import datetime
import traceback
import re

class StorageFormat(Enum):
    HUDI = "hudi"
    ICEBERG = "iceberg"
    DELTA = "delta"
    PARQUET = "parquet"
    UNKNOWN = "unknown"

class StageType(Enum):
    EXTRACT = "extract"
    TRANSFORM = "transform"
    LOAD = "load"
    UNKNOWN = "unknown"

class SparkStageAnalyzer:
    def __init__(self, api_client: APIClient):
        self.api_client = api_client
        self._load_storage_format_keywords()
        self._load_workflow_type_keywords()
        self.opt_out_fields = set()
        logging.debug("Initialized SparkStageAnalyzer")

    def _load_storage_format_keywords(self):
        """Load keywords for storage format detection"""
        try:
            import os
            import json
            
            # Get the directory of the current file
            current_dir = os.path.dirname(os.path.abspath(__file__))
            # Construct path to the resources directory
            resources_dir = os.path.join(os.path.dirname(current_dir), 'resources')
            keywords_file = os.path.join(resources_dir, 'storage_format_keywords.json')
            
            with open(keywords_file, 'r') as f:
                self.storage_format_keywords = json.load(f)
                
            for format_type, keywords in self.storage_format_keywords.items():
                logging.debug(f"Loaded {len(keywords)} keywords for storage format: {format_type}")
                
        except Exception as e:
            logging.error(f"Error loading storage format keywords: {str(e)}")
            self.storage_format_keywords = {}
            raise

    def _load_workflow_type_keywords(self):
        """Load keywords for workflow type detection"""
        try:
            import os
            import json
            
            # Get the directory of the current file
            current_dir = os.path.dirname(os.path.abspath(__file__))
            # Construct path to the resources directory
            resources_dir = os.path.join(os.path.dirname(current_dir), 'resources')
            keywords_file = os.path.join(resources_dir, 'workflow_type_keywords.json')
            
            with open(keywords_file, 'r') as f:
                self.workflow_type_keywords = json.load(f)
                
            for category, keywords in self.workflow_type_keywords.items():
                logging.debug(f"Loaded {len(keywords)} keywords for workflow category: {category}")
                
        except Exception as e:
            logging.error(f"Error loading workflow type keywords: {str(e)}")
            self.workflow_type_keywords = {}
            raise

    def set_opt_out_fields(self, fields: Set[str]):
        """Set which fields should be excluded from output (hashed or omitted)"""
        if not isinstance(fields, set):
            logging.warning(f"opt_out_fields should be a set, got {type(fields)}. Converting to set.")
            fields = set(fields)
            
        self.opt_out_fields = fields
        logging.debug(f"Set opt-out fields: {fields}")

    def _analyze_task_timeline(self, tasks: Dict[str, Any]) -> Dict[str, List[Tuple[datetime.datetime, datetime.datetime]]]:
        executor_tasks = {}
        
        logging.info(f"Analyzing task timeline for {len(tasks)} tasks")
        
        for task_id, task in tasks.items():
            executor_id = task.get("executorId")
            if not executor_id:
                logging.debug(f"Task {task_id} has no executor ID, skipping")
                continue
            
            start_time = task.get("launchTime")
            duration_ms = task.get("duration")
            
            if not start_time or duration_ms is None:
                logging.debug(f"Task {task_id} missing timing data: launchTime={start_time}, duration={duration_ms}")
                continue
            
            try:
                start_dt = datetime.datetime.strptime(start_time.split("GMT")[0], "%Y-%m-%dT%H:%M:%S.%f")
                # Calculate end time using start time + duration
                end_dt = start_dt + datetime.timedelta(milliseconds=duration_ms)
                
                if executor_id not in executor_tasks:
                    executor_tasks[executor_id] = []
                executor_tasks[executor_id].append((start_dt, end_dt))
                logging.debug(f"Successfully parsed task {task_id} timing: {start_dt} to {end_dt}")
                
            except (ValueError, TypeError) as e:
                logging.error(f"Error parsing task time for task {task_id}: {str(e)}")
                logging.error(f"Raw timing data - start: {start_time}, duration: {duration_ms}")
                continue
        
        logging.info(f"Found task intervals for {len(executor_tasks)} executors")
        for executor_id, intervals in executor_tasks.items():
            logging.debug(f"Executor {executor_id} has {len(intervals)} task intervals")
        
        return executor_tasks

    def _calculate_max_concurrent_tasks(self, task_intervals: List[Tuple[datetime.datetime, datetime.datetime]]) -> int:
        if not task_intervals:
            return 0
        
        events = []
        for start, end in task_intervals:
            events.append((start, 1))
            events.append((end, -1))
        
        events.sort()
        
        current_tasks = 0
        max_tasks = 0
        
        for _, delta in events:
            current_tasks += delta
            max_tasks = max(max_tasks, current_tasks)
        
        return max_tasks

    def _was_executor_active_during_stage(
        self, 
        executor: Dict[str, Any], 
        stage_start: datetime.datetime, 
        stage_end: datetime.datetime
    ) -> bool:
        add_time = executor.get("addTime")
        remove_time = executor.get("removeTime")
        
        if not add_time:
            return False
        
        try:
            add_dt = datetime.datetime.strptime(add_time.split("GMT")[0], "%Y-%m-%dT%H:%M:%S.%f")
            remove_dt = None
            if remove_time:
                remove_dt = datetime.datetime.strptime(remove_time.split("GMT")[0], "%Y-%m-%dT%H:%M:%S.%f")
            
            return add_dt <= stage_end and (remove_dt is None or remove_dt >= stage_start)
            
        except (ValueError, TypeError) as e:
            logging.debug(f"Error parsing executor time for executor {executor.get('id')}: {str(e)}")
            return False

    def _calculate_effective_cores_used(
        self,
        executor: Dict[str, Any],
        task_intervals: List[Tuple[datetime.datetime, datetime.datetime]],
        stage_duration_ms: int
    ) -> float:
        executor_id = executor.get("id", "unknown")
        logging.info(f"Calculating effective cores for executor {executor_id}")
        logging.info(f"Stage duration: {stage_duration_ms}ms")
        logging.info(f"Number of task intervals: {len(task_intervals)}")
        
        if not task_intervals:
            logging.warning(f"No task intervals for executor {executor_id}")
            return 0.0
        
        if stage_duration_ms <= 0:
            logging.warning(f"Invalid stage duration {stage_duration_ms}ms for executor {executor_id}")
            return 0.0
        
        total_task_time_ms = sum(
            (end - start).total_seconds() * 1000 
            for start, end in task_intervals
        )
        logging.info(f"Total task time for executor {executor_id}: {total_task_time_ms}ms")
        
        utilization_ratio = min(total_task_time_ms / stage_duration_ms, 1.0)
        logging.info(f"Utilization ratio for executor {executor_id}: {utilization_ratio}")
        
        max_concurrent = self._calculate_max_concurrent_tasks(task_intervals)
        logging.info(f"Max concurrent tasks for executor {executor_id}: {max_concurrent}")
        
        available_cores = executor.get("totalCores", 0)
        logging.info(f"Available cores for executor {executor_id}: {available_cores}")
        
        concurrent_cores = min(max_concurrent, available_cores)
        effective_cores = concurrent_cores * utilization_ratio
        final_cores = min(effective_cores, available_cores)
        
        logging.info(f"Final effective cores for executor {executor_id}: {final_cores}")
        return final_cores

    def _get_active_executors_during_stage(
        self, 
        stage_submission_time: str, 
        stage_completion_time: str, 
        executor_metrics: List[Dict[str, Any]], 
        task_executor_ids: Set[str],
        stage_attempt: Dict[str, Any]
    ) -> Tuple[List[Dict[str, Any]], List[str], float, int]:
        """Get executors that were active during a stage's execution and calculate core usage."""
        active_executors = []
        active_executor_ids = []
        effective_cores_used = 0.0
        total_cores_available = 0
        
        try:
            if not stage_submission_time or not stage_completion_time:
                logging.debug("Skipping active executor determination due to missing stage timestamps")
                return active_executors, active_executor_ids, effective_cores_used, total_cores_available

            submission_dt = datetime.datetime.strptime(stage_submission_time.split("GMT")[0], "%Y-%m-%dT%H:%M:%S.%f")
            completion_dt = datetime.datetime.strptime(stage_completion_time.split("GMT")[0], "%Y-%m-%dT%H:%M:%S.%f")
            stage_duration_ms = int((completion_dt - submission_dt).total_seconds() * 1000)
            logging.info(f"Stage duration: {stage_duration_ms}ms (from {submission_dt} to {completion_dt})")
            
            executor_task_timelines = {}
            if stage_attempt and "tasks" in stage_attempt:
                tasks = stage_attempt["tasks"]
                logging.info(f"Found {len(tasks)} tasks in stage details")
                for task_id, task in tasks.items():
                    logging.debug(f"Task {task_id}: executor={task.get('executorId')}, "
                                f"launchTime={task.get('launchTime')}, "
                                f"duration={task.get('duration')}")
                executor_task_timelines = self._analyze_task_timeline(tasks)
            else:
                logging.debug("No task details found in stage details")
            
            for executor in executor_metrics:
                if executor["id"] == "driver":
                    continue
                    
                if self._was_executor_active_during_stage(executor, submission_dt, completion_dt):
                    executor_cores = executor.get("totalCores", 0)
                    active_executors.append(executor)
                    active_executor_ids.append(executor["id"])
                    total_cores_available += executor_cores
                    logging.info(f"Executor {executor['id']} was active with {executor_cores} cores")
                    
                    if executor["id"] in task_executor_ids:
                        task_intervals = executor_task_timelines.get(executor["id"], [])
                        effective_cores = self._calculate_effective_cores_used(
                            executor,
                            task_intervals,
                            stage_duration_ms
                        )
                        effective_cores_used += effective_cores
                        logging.info(f"Added {effective_cores} effective cores for executor {executor['id']}")
                    else:
                        logging.info(f"Executor {executor['id']} was active but ran no tasks")
                else:
                    logging.debug(f"Executor {executor['id']} was not active during stage")
            
            logging.info(f"Final metrics - Active executors: {len(active_executors)}, "
                        f"Total cores available: {total_cores_available}, "
                        f"Effective cores used: {effective_cores_used}")
                    
        except Exception as e:
            logging.error(f"Error determining active executors: {str(e)}")
            logging.error(f"Exception traceback: {traceback.format_exc()}")
        
        return active_executors, active_executor_ids, effective_cores_used, total_cores_available

    def format_stage_for_proto(self, stage: Dict[str, Any], app_id: str, executor_metrics: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Format a stage's data according to the proto structure."""
        try:
            stage_id = stage.get("stageId")
            if stage_id is None:
                logging.debug("Found stage with missing stageId, skipping")
                return None
                
            logging.debug(f"Processing stage {stage_id} for application {app_id}")
                
            try:
                stage_details = self.api_client.get_stage_details_with_tasks(app_id, stage_id)
                if not stage_details:
                    logging.debug(f"No stage details found for stage {stage_id}")
                    return None
            except ValueError as e:
                error_msg = str(e)
                if "Databricks API returned non-JSON response" in error_msg:
                    logging.warning(f"Stage {stage_id}: Databricks API issue - {error_msg}")
                    return None
                elif "Server returned non-JSON response" in error_msg:
                    logging.warning(f"Stage {stage_id}: Server returned non-JSON response - {error_msg}")
                    return None
                else:
                    raise
            except Exception as e:
                if "404" in str(e) or "not found" in str(e).lower():
                    logging.info(f"Stage {stage_id} not found (likely removed), skipping")
                    return None
                else:
                    logging.error(f"Error fetching details for stage {stage_id}: {str(e)}")
                    raise ValueError(f"Failed to get stage details: {str(e)}")

            stage_attempt = stage_details[0] if isinstance(stage_details, list) else stage_details
            
            tasks = stage_attempt.get("tasks", {})
            num_tasks = len(tasks) if tasks else 0
            logging.debug(f"Stage {stage_id} has {num_tasks} tasks")
            
            try:
                total_executor_count = len([e for e in executor_metrics if e["id"] != "driver"])
                executors, cores, task_executor_ids = self._get_executors_for_stage(
                    stage_attempt, 
                    executor_metrics,
                    total_executors=total_executor_count
                )
                used_executor_ids = [executor["id"] for executor in executors]
                logging.debug(f"Found {len(used_executor_ids)} executors used for stage {stage_id}")
                
                if len(used_executor_ids) == 0 and len(task_executor_ids) > 0:
                    logging.info(f"Using {len(task_executor_ids)} task executor IDs for stage {stage_id} instead of metrics")
                    used_executor_ids = list(task_executor_ids)
            except Exception as e:
                logging.error(f"Error determining executors for stage {stage_id}: {str(e)}")
                logging.debug(f"Exception traceback: {traceback.format_exc()}")
                used_executor_ids = []
                task_executor_ids = set()
                
            name = str(stage.get("name", "")) if stage.get("name") is not None else ""
            description = str(stage.get("description", "")) if stage.get("description") is not None else ""
            details = str(stage.get("details", "")) if stage.get("details") is not None else ""

            try:
                workflow_info = self._get_workflow_info(name, description, stage_id, app_id, details)
                logging.debug(f"Stage {stage_id} workflow type: {workflow_info['type']}, storage format: {workflow_info['storage_format']}")
            except Exception as e:
                logging.error(f"Error determining workflow info for stage {stage_id}: {str(e)}")
                logging.debug(f"Exception traceback: {traceback.format_exc()}")
                workflow_info = {
                    "type": "WORKFLOW_TYPE_UNKNOWN",
                    "storage_format": "STORAGE_FORMAT_UNKNOWN",
                    "custom_info": ""
                }

            if "name" in self.opt_out_fields:
                logging.debug(f"Hashing stage name for privacy (stage {stage_id})")
                name = f"name_hash_{hash(name)}"
            if "description" in self.opt_out_fields:
                logging.debug(f"Hashing stage description for privacy (stage {stage_id})")
                description = f"description_hash_{hash(description)}"
            if "details" in self.opt_out_fields:
                logging.debug(f"Hashing stage details for privacy (stage {stage_id})")
                details = f"details_hash_{hash(details)}"

            submission_time = stage_attempt.get("submissionTime")
            completion_time = stage_attempt.get("completionTime")
            
            stage_duration_ms = 0
            if submission_time and completion_time:
                try:
                    submission_dt = datetime.datetime.strptime(submission_time.split("GMT")[0], "%Y-%m-%dT%H:%M:%S.%f")
                    completion_dt = datetime.datetime.strptime(completion_time.split("GMT")[0], "%Y-%m-%dT%H:%M:%S.%f")
                    stage_duration_ms = int((completion_dt - submission_dt).total_seconds() * 1000)
                    logging.debug(f"Stage {stage_id} duration: {stage_duration_ms} ms")
                except (ValueError, TypeError) as e:
                    logging.error(f"Error calculating duration for stage {stage_id}: {str(e)}")
                    logging.debug(f"Error details: {traceback.format_exc()}")
            else:
                logging.debug(f"Stage {stage_id} missing timestamps:")
                logging.debug(f"  submission_time is None: {submission_time is None}")
                logging.debug(f"  completion_time is None: {completion_time is None}")
                    
            executor_run_time_ms = stage_attempt.get("executorRunTime")
            if executor_run_time_ms is None:
                executor_run_time_ms = 0
            else:
                try:
                    executor_run_time_ms = int(executor_run_time_ms)
                except (ValueError, TypeError):
                    executor_run_time_ms = 0

            active_executors, active_executor_ids, effective_cores_used, total_cores_available = self._get_active_executors_during_stage(
                submission_time,
                completion_time,
                executor_metrics,
                task_executor_ids,
                stage_attempt
            )

            stage_data = {
                "stage_id": int(stage_id),
                "application_id": app_id,
                "stage_name": name,
                "stage_description": description,
                "stage_details": details,
                "num_tasks": num_tasks,
                "num_executors_used": len(used_executor_ids),
                "used_executor_ids": used_executor_ids,
                "total_active_executors": len(active_executor_ids),
                "active_executor_ids": active_executor_ids,
                "cores_used_by_stage": effective_cores_used,
                "total_cores_available": total_cores_available,
                "submission_time": submission_time,
                "completion_time": completion_time,
                "executor_run_time_ms": executor_run_time_ms,
                "stage_duration_ms": stage_duration_ms,
                "workflow_info": workflow_info
            }
            
            if workflow_info:
                workflow_info["type"] = workflow_info["type"]
                workflow_info["storage_format"] = workflow_info["storage_format"]
                workflow_info["custom_info"] = str(workflow_info["custom_info"])
            
            logging.debug(f"Successfully processed stage {stage_id}")
            return stage_data
            
        except Exception as e:
            stage_id = stage.get('stageId', 'unknown')
            logging.error(f"Error formatting stage {stage_id}: {str(e)}")
            logging.debug(f"Exception traceback: {traceback.format_exc()}")
            return None

    def _normalize_text(self, text: str) -> str:
        original_text = text
        text = text.lower()
        text = re.sub(r'[^a-z0-9\s]', ' ', text)
        text = re.sub(r'\s+', ' ', text).strip()
        return text

    def _matches_keyword(self, text: str, keyword: str) -> bool:
        escaped_keyword = re.escape(keyword.lower())
        pattern = r'\b' + escaped_keyword + r'\b'
        return bool(re.search(pattern, text))

    def _count_keyword_occurrences_in_text(self, text: str, keyword: str) -> int:
        escaped_keyword = re.escape(keyword.lower())
        pattern = r'\b' + escaped_keyword + r'\b'
        matches = re.findall(pattern, text)
        return len(matches)

    def _count_keyword_occurrences(self, text: str) -> Dict[str, int]:
        counts = {
            "WORKFLOW_TYPE_UNKNOWN": 0,
            "WORKFLOW_TYPE_EXTRACT": 0,
            "WORKFLOW_TYPE_TRANSFORM": 0,
            "WORKFLOW_TYPE_LOAD": 0,
            "WORKFLOW_TYPE_HUDI_METADATA": 0
        }
        
        # Get normalized text
        normalized_text = self._normalize_text(text)
        
        # Map workflow categories to their corresponding count keys
        category_to_count = {
            "extract": "WORKFLOW_TYPE_EXTRACT",
            "transform": "WORKFLOW_TYPE_TRANSFORM",
            "load": "WORKFLOW_TYPE_LOAD",
            "hudi_metadata": "WORKFLOW_TYPE_HUDI_METADATA"
        }
        
        for category, keywords in self.workflow_type_keywords.items():
            count_key = category_to_count.get(category)
            if count_key:
                for keyword in keywords:
                    if self._matches_keyword(normalized_text, keyword):
                        counts[count_key] += 1
                        logging.debug(f"Found word boundary match '{keyword}' for category {category}")
        
        return counts

    def _determine_workflow_type_and_subtype(self, text: str) -> Tuple[str, str, str]:
        normalized_text = self._normalize_text(text)
        type_counts = {
            "WORKFLOW_TYPE_EXTRACT": 0,
            "WORKFLOW_TYPE_TRANSFORM": 0,
            "WORKFLOW_TYPE_LOAD": 0,
            "WORKFLOW_TYPE_HUDI_METADATA": 0
        }
        
        subtype_counts = {
            "EXTRACT_TYPE_SCAN": 0,
            
            "TRANSFORM_TYPE_OPERATION": 0,
            "TRANSFORM_TYPE_JOIN": 0,
            
            "LOAD_TYPE_UPSERT": 0,
            "LOAD_TYPE_INSERT": 0,
            "LOAD_TYPE_OVERWRITE": 0,
            "LOAD_TYPE_INDEXING": 0,
            
            "HUDI_METADATA_TYPE_OPERATION": 0
        }
        
        category_mapping = {
            "extract": {
                "type": "WORKFLOW_TYPE_EXTRACT",
                "subtypes": {
                    "scan": "EXTRACT_TYPE_SCAN"
                }
            },
            "transform": {
                "type": "WORKFLOW_TYPE_TRANSFORM",
                "subtypes": {
                    "operation": "TRANSFORM_TYPE_OPERATION",
                    "join": "TRANSFORM_TYPE_JOIN"
                }
            },
            "load": {
                "type": "WORKFLOW_TYPE_LOAD",
                "subtypes": {
                    "upsert": "LOAD_TYPE_UPSERT",
                    "insert": "LOAD_TYPE_INSERT",
                    "overwrite": "LOAD_TYPE_OVERWRITE",
                    "indexing": "LOAD_TYPE_INDEXING"
                }
            },
            "hudi_metadata": {
                "type": "WORKFLOW_TYPE_HUDI_METADATA",
                "subtypes": {
                    "operation": "HUDI_METADATA_TYPE_OPERATION"
                }
            }
        }
        
        for category, category_info in self.workflow_type_keywords.items():
            if category not in category_mapping:
                continue
                
            main_type = category_mapping[category]["type"]
            
            for subtype, keywords in category_info.items():
                if subtype not in category_mapping[category]["subtypes"]:
                    continue
                    
                subtype_key = category_mapping[category]["subtypes"][subtype]
                
                for keyword in keywords:
                    if self._matches_keyword(normalized_text, keyword):
                        type_counts[main_type] += 1
                        subtype_counts[subtype_key] += 1
                        logging.debug(f"Found word boundary match '{keyword}' for {main_type} -> {subtype_key}")
        
        logging.debug("Type counts:")
        for type_name, count in type_counts.items():
            logging.debug(f"  {type_name}: {count}")
        logging.debug("Subtype counts:")
        for subtype, count in subtype_counts.items():
            logging.debug(f"  {subtype}: {count}")
        
        max_type_count = 0
        chosen_type = "WORKFLOW_TYPE_UNKNOWN"
        for type_name, count in type_counts.items():
            if count > max_type_count:
                max_type_count = count
                chosen_type = type_name
        
        if chosen_type == "WORKFLOW_TYPE_UNKNOWN":
            logging.debug("No type matches found, returning UNKNOWN")
            return "WORKFLOW_TYPE_UNKNOWN", None, ""
        
        max_subtype_count = 0
        chosen_subtype = None
        
        type_subtypes = {
            subtype for category_info in category_mapping.values()
            if category_info["type"] == chosen_type
            for subtype in category_info["subtypes"].values()
        }
        
        for subtype in type_subtypes:
            if subtype_counts[subtype] > max_subtype_count:
                max_subtype_count = subtype_counts[subtype]
                chosen_subtype = subtype
        
        logging.debug(f"Chosen type: {chosen_type} (count: {max_type_count})")
        if chosen_subtype:
            logging.debug(f"Chosen subtype: {chosen_subtype} (count: {max_subtype_count})")
        
        return chosen_type, chosen_subtype, ""

    def _determine_platform_from_url(self) -> str:
        """Determine the platform type based on the API client's base URL."""
        if not hasattr(self.api_client, 'base_url'):
            return "unknown"
        
        base_url = self.api_client.base_url.lower()
        
        # Check for Databricks (including Azure Databricks)
        if "databricks.com" in base_url or "azuredatabricks.net" in base_url:
            return "databricks"
        
        # Check for AWS EMR (common patterns)
        if any(pattern in base_url for pattern in [
            "emr", 
            "elasticmapreduce", 
            "amazonaws.com/emr",
            ".elasticmapreduce."
        ]):
            return "emr"
        
        # Check for local mode (localhost or 127.0.0.1)
        if any(pattern in base_url for pattern in [
            "localhost", 
            "127.0.0.1",
            "0.0.0.0"
        ]):
            return "local"
        
        # Check for other cloud providers
        if "azure" in base_url or "microsoft" in base_url:
            return "azure"
        
        if "gcp" in base_url or "google" in base_url or "cloud.google.com" in base_url:
            return "gcp"
        
        # Check for other common patterns
        if "aws" in base_url or "amazonaws.com" in base_url:
            return "aws"
        
        # Default to unknown if no pattern matches
        return "unknown"

    def _get_workflow_info(self, stage_name: str, stage_description: str, stage_id: str = None, app_id: str = None, stage_details: str = None) -> Dict[str, Any]:
        """Determine workflow type and storage format for a stage using frequency-based classification."""
        text = f"{stage_name} {stage_description} {stage_details or ''}".lower()
        storage_format = self._determine_storage_format(stage_name, stage_description, stage_details)
        
        main_type, subtype, _ = self._determine_workflow_type_and_subtype(text)  # Ignore custom_info
        
        # Determine platform type from URL
        platform = self._determine_platform_from_url()
        
        workflow_info = {
            "type": main_type,
            "storage_format": self._get_storage_format_proto(storage_format),
            "custom_info": platform
        }
        
        if subtype is not None:
            if main_type == "WORKFLOW_TYPE_EXTRACT":
                workflow_info["extract_type"] = subtype
            elif main_type == "WORKFLOW_TYPE_TRANSFORM":
                workflow_info["transform_type"] = subtype
            elif main_type == "WORKFLOW_TYPE_LOAD":
                workflow_info["load_type"] = subtype
            elif main_type == "WORKFLOW_TYPE_HUDI_METADATA":
                workflow_info["metadata_type"] = subtype
        
        return workflow_info
        
    def _get_storage_format_proto(self, storage_format: StorageFormat) -> str:
        storage_format_map = {
            StorageFormat.HUDI: "STORAGE_FORMAT_HUDI",
            StorageFormat.ICEBERG: "STORAGE_FORMAT_ICEBERG",
            StorageFormat.DELTA: "STORAGE_FORMAT_DELTA",
            StorageFormat.PARQUET: "STORAGE_FORMAT_PARQUET",
            StorageFormat.UNKNOWN: "STORAGE_FORMAT_UNKNOWN"
        }
        return storage_format_map.get(storage_format, "STORAGE_FORMAT_UNKNOWN")

    def _get_executors_for_stage(self, stage_details: Dict[str, Any], executor_metrics: List[Dict[str, Any]], total_executors: Optional[int] = None) -> Tuple[List[Dict[str, Any]], int, set]:
        """Get executors used for a specific stage."""
        stage_id = stage_details.get('stageId', 'unknown')
        task_data = stage_details.get("tasks", {})
        
        if not task_data:
            logging.debug(f"No task data found for stage {stage_id}. This is normal for stages that are queued, just starting, or already completed.")
            return [], 0, set()
        
        task_executor_ids = set()
        for task_id, task in task_data.items():
            executor_id = task.get("executorId")
            if executor_id:
                task_executor_ids.add(executor_id)
        
        if not task_executor_ids:
            logging.debug(f"No executor IDs found in tasks for stage {stage_id}. Tasks may be pending assignment to executors.")
            return [], 0, set()
            
        logging.debug(f"Found {len(task_executor_ids)} unique executor IDs in tasks for stage {stage_id}")
        
        found_executors = []
        total_cores = 0
        
        if not executor_metrics:
            logging.debug(f"No executor metrics available. Using task executor IDs only for stage {stage_id}.")
            return [], 0, task_executor_ids
        
        for executor in executor_metrics:
            executor_id = executor.get("id")
            if executor_id in task_executor_ids:
                found_executors.append(executor)
                total_cores += executor.get("totalCores", 0)
                
                if len(found_executors) == len(task_executor_ids):
                    logging.debug(f"Found all {len(task_executor_ids)} executors in metrics for stage {stage_id}")
                    break
                    
                if total_executors is not None and len(found_executors) == total_executors:
                    logging.debug(f"Found all {total_executors} total executors for stage {stage_id}")
                    break
        
        if task_executor_ids and found_executors:
            if len(found_executors) < len(task_executor_ids):
                logging.debug(f"Found only {len(found_executors)}/{len(task_executor_ids)} executors in metrics for stage {stage_id}. Some executors may have been reused or removed.")
        
        logging.debug(f"Found {len(found_executors)} executors with {total_cores} total cores for stage {stage_id}")
        
        return found_executors, total_cores, task_executor_ids

    def _determine_storage_format(self, stage_name: str, stage_description: str, stage_details: str = None) -> StorageFormat:
        """Determine the storage format for a stage using keyword counting-based detection."""
        normalized_text = self._normalize_text(f"{stage_name} {stage_description} {stage_details or ''}")
        
        format_counts = {
            "HUDI": 0,
            "ICEBERG": 0,
            "DELTA": 0,
            "PARQUET": 0
        }
        
        for format_type, keywords in self.storage_format_keywords.items():
            for keyword in keywords:
                count = self._count_keyword_occurrences_in_text(normalized_text, keyword)
                if count > 0:
                    format_counts[format_type] += count
                    logging.debug(f"Found {count} word boundary match(es) '{keyword}' for storage format {format_type} (total count now: {format_counts[format_type]})")
        
        logging.debug("Storage format counts:")
        for format_name, count in format_counts.items():
            logging.debug(f"  {format_name}: {count}")
        
        max_count = 0
        chosen_format = StorageFormat.UNKNOWN
        
        for format_name, count in format_counts.items():
            if count > max_count:
                max_count = count
                chosen_format = StorageFormat[format_name]
                logging.debug(f"DEBUG: New max count {max_count} for {format_name}")
        
        if chosen_format == StorageFormat.UNKNOWN:
            logging.debug("No storage format matches found, returning UNKNOWN")
        else:
            logging.debug(f"Chosen storage format: {chosen_format.value} (count: {max_count})")
        
        return chosen_format
    
    def _determine_stage_type(
        self,
        storage_format: StorageFormat,
        stage_name: str,
        stage_description: str,
        stage_details: str = None
    ) -> StageType:
        """Determine the type of stage (EXTRACT, TRANSFORM, LOAD) using workflow type keywords."""
        normalized_text = self._normalize_text(f"{stage_name} {stage_description} {stage_details or ''}")
        
        # Count keyword occurrences for each category
        counts = {
            "EXTRACT": 0,
            "TRANSFORM": 0,
            "LOAD": 0
        }
        
        # Map workflow categories to stage types
        category_to_stage_type = {
            "scan": "EXTRACT",
            "transform": "TRANSFORM",
            "merge_write": "LOAD",
            "insert_write": "LOAD"
        }
        
        # Count occurrences for each category
        for category, keywords in self.workflow_type_keywords.items():
            stage_type = category_to_stage_type.get(category)
            if stage_type:
                for keyword in keywords:
                    if self._matches_keyword(normalized_text, keyword):
                        counts[stage_type] += 1
                        logging.debug(f"Found word boundary match '{keyword}' for stage type {stage_type}")
        
        # Determine the stage type based on highest count
        max_count = 0
        stage_type = StageType.UNKNOWN
        
        for type_name, count in counts.items():
            if count > max_count:
                max_count = count
                stage_type = StageType[type_name]
        
        return stage_type 