import unittest
import json
import os
from datetime import datetime
from ..lib.spark_stage_analyzer import SparkStageAnalyzer, StorageFormat, StageType
from unittest.mock import Mock, patch

class TestSparkStageAnalyzer(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        test_data_path = os.path.join(os.path.dirname(current_dir), 'resources', 'test_data', 'stage_analyzer_test_data.json')
        
        with open(test_data_path, 'r') as f:
            cls.test_data = json.load(f)
            
        cls.mock_api_client = Mock()
        cls.analyzer = SparkStageAnalyzer(cls.mock_api_client)

    def setUp(self):
        self.mock_api_client.reset_mock()

    def test_format_stage_with_null_values(self):
        """Test handling of null values in stage data"""
        stage = self.test_data['stage_with_null_values']
        app_id = "test_app"
        executor_metrics = self.test_data['executor_metrics']
        
        self.mock_api_client.get_stage_details_with_tasks.return_value = self.test_data['stage_details_with_null']
        
        result = self.analyzer.format_stage_for_proto(stage, app_id, executor_metrics)
        
        self.assertIsNotNone(result)
        self.assertEqual(result['stage_id'], 2)
        self.assertEqual(result['stage_name'], "")  
        self.assertEqual(result['stage_description'], "")
        self.assertEqual(result['stage_details'], "")  
        self.assertEqual(result['executor_run_time_ms'], 0)
        self.assertEqual(result['stage_duration_ms'], 0) 

    def test_format_stage_with_missing_fields(self):
        """Test handling of missing fields in stage data"""
        stage = self.test_data['stage_missing_fields']
        app_id = "test_app"
        executor_metrics = self.test_data['executor_metrics']
        
        self.mock_api_client.get_stage_details_with_tasks.return_value = self.test_data['stage_details']
        
        result = self.analyzer.format_stage_for_proto(stage, app_id, executor_metrics)
        
        self.assertIsNotNone(result)
        self.assertEqual(result['stage_id'], 3)
        self.assertEqual(result['stage_name'], "") 
        self.assertEqual(result['stage_description'], "")
        self.assertEqual(result['stage_details'], "")

    def test_get_active_executors_with_null_values(self):
        """Test handling of null values in executor metrics"""
        stage_submission_time = "2024-03-20T10:00:00.000GMT"
        stage_completion_time = "2024-03-20T10:01:00.000GMT"
        executor_metrics = self.test_data['executor_metrics']
        task_executor_ids = {"executor1", "executor2", "executor3"}
        
        active_executors, active_executor_ids, cores_used, total_cores = self.analyzer._get_active_executors_during_stage(
            stage_submission_time,
            stage_completion_time,
            executor_metrics,
            task_executor_ids
        )
        
        self.assertEqual(len(active_executors), 2)
        self.assertEqual(len(active_executor_ids), 2)
        self.assertIn("executor1", active_executor_ids)
        self.assertIn("executor2", active_executor_ids)
        self.assertNotIn("executor3", active_executor_ids)  
        self.assertEqual(cores_used, 6)  
        self.assertEqual(total_cores, 6) 

    def test_get_executors_for_stage_with_null_values(self):
        stage_details = self.test_data['stage_details_with_null']
        executor_metrics = self.test_data['executor_metrics']
        
        executors, cores, task_executor_ids = self.analyzer._get_executors_for_stage(
            stage_details,
            executor_metrics,
            total_executors=3
        )
        
        self.assertEqual(len(executors), 0)
        self.assertEqual(cores, 0)
        self.assertEqual(len(task_executor_ids), 0)

    def test_determine_storage_format_with_null_values(self):
        """Test handling of null values in storage format determination"""
        storage_format = self.analyzer._determine_storage_format(None, None, None)
        self.assertEqual(storage_format, StorageFormat.UNKNOWN)
        
        storage_format = self.analyzer._determine_storage_format("", "", "")
        self.assertEqual(storage_format, StorageFormat.UNKNOWN)
        
        storage_format = self.analyzer._determine_storage_format("test", None, "")
        self.assertEqual(storage_format, StorageFormat.UNKNOWN)

    def test_determine_stage_type_with_null_values(self):
        """Test handling of null values in stage type determination"""
        stage_type = self.analyzer._determine_stage_type(
            StorageFormat.UNKNOWN,
            None,
            None,
            None
        )
        self.assertEqual(stage_type, StageType.UNKNOWN)
        
        stage_type = self.analyzer._determine_stage_type(
            StorageFormat.UNKNOWN,
            "",
            "",
            ""
        )
        self.assertEqual(stage_type, StageType.UNKNOWN)
        
        stage_type = self.analyzer._determine_stage_type(
            StorageFormat.UNKNOWN,
            "test",
            None,
            ""
        )
        self.assertEqual(stage_type, StageType.UNKNOWN)

if __name__ == '__main__':
    unittest.main() 