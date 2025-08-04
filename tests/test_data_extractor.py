"""
Comprehensive test suite for the data_extractor module.
Tests stage extraction, suggestion extraction, and data processing functionality.
"""

import unittest
import sys
import os
import json
import tempfile
import shutil
from unittest.mock import Mock, patch, mock_open
from typing import Dict, List

# Using absolute imports, no path modification needed

from refactored_counseling_system.utils.data_extractor import (
    DataExtractor,
    StageExtractor,
    SuggestionExtractor,
    extract_stages_from_folder,
    extract_suggestions_from_folder,
    process_counseling_data_folder
)


class TestStageExtractor(unittest.TestCase):
    """Test cases for StageExtractor class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.extractor = StageExtractor()
        self.temp_dir = tempfile.mkdtemp()
        
        # Create test JSON files
        self.test_data = {
            "test1.json": [
                ['{"所处阶段":"设置议程","其他信息":"测试"}'],
                ['{"所处阶段":"情绪检查","其他信息":"测试"}']
            ],
            "test2.json": [
                ['{"所处阶段":"获取信息","其他信息":"测试"}'],
                ['{"所处阶段":"问题识别","其他信息":"测试"}'],
                ['{"所处阶段":"认知模型","其他信息":"测试"}']
            ],
            "invalid.json": "not a list"
        }
        
        for filename, data in self.test_data.items():
            with open(os.path.join(self.temp_dir, filename), 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
    
    def tearDown(self):
        """Clean up test fixtures"""
        shutil.rmtree(self.temp_dir)
    
    def test_extract_stages_from_directory_success(self):
        """Test successful stage extraction"""
        stages_data, errors = self.extractor.extract_stages_from_directory(self.temp_dir)
        
        self.assertIsNotNone(stages_data)
        self.assertIn("test1.json", stages_data)
        self.assertIn("test2.json", stages_data)
        
        # Check extracted stages
        self.assertEqual(stages_data["test1.json"], ["设置议程", "情绪检查"])
        self.assertEqual(stages_data["test2.json"], ["获取信息", "问题识别", "认知模型"])
        
        # Check error files
        self.assertIn("invalid.json", errors)
    
    def test_extract_stages_from_nonexistent_directory(self):
        """Test extraction from non-existent directory"""
        stages_data, errors = self.extractor.extract_stages_from_directory("/non/existent/path")
        
        self.assertIsNone(stages_data)
        self.assertIsNone(errors)
    
    def test_save_extracted_stages(self):
        """Test saving extracted stages to files"""
        test_data = {
            "test.json": ["设置议程", "情绪检查", None]
        }
        
        json_file = os.path.join(self.temp_dir, "test_stages.json")
        txt_file = os.path.join(self.temp_dir, "test_stages.txt")
        
        self.extractor.save_extracted_stages(test_data, json_file, txt_file)
        
        # Check JSON file
        self.assertTrue(os.path.exists(json_file))
        with open(json_file, 'r', encoding='utf-8') as f:
            saved_data = json.load(f)
        self.assertEqual(saved_data, test_data)
        
        # Check text file
        self.assertTrue(os.path.exists(txt_file))
        with open(txt_file, 'r', encoding='utf-8') as f:
            content = f.read()
        self.assertIn("设置议程", content)
        self.assertIn("[阶段未找到]", content)


class TestSuggestionExtractor(unittest.TestCase):
    """Test cases for SuggestionExtractor class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.extractor = SuggestionExtractor()
        self.temp_dir = tempfile.mkdtemp()
        self.output_dir = os.path.join(self.temp_dir, "output")
        
        # Create test JSON files
        self.test_data = {
            "test1.json": [
                ['{"改进意见":"需要更多共情","其他信息":"测试"}'],
                ['{"改进意见":"语言需要更自然","其他信息":"测试"}']
            ],
            "test2.json": [
                ['{"改进意见":"回应过于正式","其他信息":"测试"}'],
                ['{"改进意见":"建议使用开放式问题","其他信息":"测试"}'],
                ['{"改进意见":"需要更多支持性语言","其他信息":"测试"}']
            ]
        }
        
        for filename, data in self.test_data.items():
            with open(os.path.join(self.temp_dir, filename), 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
    
    def tearDown(self):
        """Clean up test fixtures"""
        shutil.rmtree(self.temp_dir)
    
    def test_extract_suggestions_structured_success(self):
        """Test successful suggestion extraction"""
        failed_files = self.extractor.extract_suggestions_structured(self.temp_dir, self.output_dir)
        
        self.assertEqual(len(failed_files), 0)
        
        # Check output files
        test1_output = os.path.join(self.output_dir, "test1.json")
        test2_output = os.path.join(self.output_dir, "test2.json")
        
        self.assertTrue(os.path.exists(test1_output))
        self.assertTrue(os.path.exists(test2_output))
        
        # Check extracted content
        with open(test1_output, 'r', encoding='utf-8') as f:
            extracted_data = json.load(f)
        
        self.assertEqual(len(extracted_data), 2)
        self.assertEqual(extracted_data[0], ["需要更多共情"])
        self.assertEqual(extracted_data[1], ["语言需要更自然"])
    
    def test_extract_suggestions_from_nonexistent_folder(self):
        """Test extraction from non-existent folder"""
        failed_files = self.extractor.extract_suggestions_structured("/non/existent/path", self.output_dir)
        
        self.assertEqual(len(failed_files), 0)


class TestDataExtractor(unittest.TestCase):
    """Test cases for DataExtractor class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.extractor = DataExtractor()
        self.temp_dir = tempfile.mkdtemp()
        
        # Create comprehensive test data
        self.test_data = {
            "counseling1.json": [
                ['{"所处阶段":"设置议程","改进意见":"需要更多共情","其他信息":"测试"}'],
                ['{"所处阶段":"情绪检查","改进意见":"语言需要更自然","其他信息":"测试"}']
            ],
            "counseling2.json": [
                ['{"所处阶段":"获取信息","改进意见":"回应过于正式","其他信息":"测试"}'],
                ['{"所处阶段":"问题识别","改进意见":"建议使用开放式问题","其他信息":"测试"}'],
                ['{"所处阶段":"认知模型","改进意见":"需要更多支持性语言","其他信息":"测试"}']
            ]
        }
        
        for filename, data in self.test_data.items():
            with open(os.path.join(self.temp_dir, filename), 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
    
    def tearDown(self):
        """Clean up test fixtures"""
        shutil.rmtree(self.temp_dir)
    
    def test_extract_stages_from_directory(self):
        """Test stage extraction through DataExtractor"""
        stages_data, errors = self.extractor.extract_stages_from_directory(
            self.temp_dir,
            os.path.join(self.temp_dir, "stages.json"),
            os.path.join(self.temp_dir, "stages.txt")
        )
        
        self.assertIsNotNone(stages_data)
        self.assertEqual(len(stages_data), 2)
        self.assertIn("counseling1.json", stages_data)
        self.assertIn("counseling2.json", stages_data)
        
        # Check files were created
        self.assertTrue(os.path.exists(os.path.join(self.temp_dir, "stages.json")))
        self.assertTrue(os.path.exists(os.path.join(self.temp_dir, "stages.txt")))
    
    def test_extract_suggestions_from_directory(self):
        """Test suggestion extraction through DataExtractor"""
        output_dir = os.path.join(self.temp_dir, "suggestions")
        failed_files = self.extractor.extract_suggestions_from_directory(self.temp_dir, output_dir)
        
        self.assertEqual(len(failed_files), 0)
        
        # Check output directory was created
        self.assertTrue(os.path.exists(output_dir))
        
        # Check output files
        self.assertTrue(os.path.exists(os.path.join(output_dir, "counseling1.json")))
        self.assertTrue(os.path.exists(os.path.join(output_dir, "counseling2.json")))
    
    def test_process_counseling_data(self):
        """Test comprehensive counseling data processing"""
        results = self.extractor.process_counseling_data(self.temp_dir)
        
        self.assertIn('stages', results)
        self.assertIn('suggestions', results)
        
        # Check stages results
        self.assertEqual(results['stages']['success'], 2)
        self.assertEqual(len(results['stages']['errors']), 0)
        
        # Check suggestions results
        self.assertEqual(results['suggestions']['success'], 2)
        self.assertEqual(len(results['suggestions']['failed_validation']), 0)


class TestUtilityFunctions(unittest.TestCase):
    """Test cases for utility functions"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        
        # Create test data
        test_data = [
            ['{"所处阶段":"设置议程","改进意见":"需要更多共情"}'],
            ['{"所处阶段":"情绪检查","改进意见":"语言需要更自然"}']
        ]
        
        with open(os.path.join(self.temp_dir, "test.json"), 'w', encoding='utf-8') as f:
            json.dump(test_data, f, ensure_ascii=False, indent=2)
    
    def tearDown(self):
        """Clean up test fixtures"""
        shutil.rmtree(self.temp_dir)
    
    def test_extract_stages_from_folder(self):
        """Test extract_stages_from_folder utility function"""
        stages_data, errors = extract_stages_from_folder(self.temp_dir, "test_stages")
        
        self.assertIsNotNone(stages_data)
        self.assertIn("test.json", stages_data)
        self.assertEqual(stages_data["test.json"], ["设置议程", "情绪检查"])
    
    def test_extract_suggestions_from_folder(self):
        """Test extract_suggestions_from_folder utility function"""
        output_dir = os.path.join(self.temp_dir, "suggestions")
        failed_files = extract_suggestions_from_folder(self.temp_dir, output_dir)
        
        self.assertEqual(len(failed_files), 0)
        self.assertTrue(os.path.exists(output_dir))
    
    def test_process_counseling_data_folder(self):
        """Test process_counseling_data_folder utility function"""
        results = process_counseling_data_folder(self.temp_dir)
        
        self.assertIn('stages', results)
        self.assertIn('suggestions', results)
        self.assertEqual(results['stages']['success'], 1)
        self.assertEqual(results['suggestions']['success'], 1)


class TestEdgeCases(unittest.TestCase):
    """Test edge cases and error conditions"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        
        # Create edge case test data
        edge_cases = {
            "empty_list.json": [],
            "malformed_stage.json": [
                ['{"所处阶段_wrong":"设置议程","其他信息":"测试"}']
            ],
            "no_stage.json": [
                ['{"其他信息":"测试，没有阶段"}']
            ],
            "complex_nesting.json": [
                ['{"所处阶段":"设置议程","改进意见":"复杂的\\"嵌套\\"引号"}']
            ]
        }
        
        for filename, data in edge_cases.items():
            with open(os.path.join(self.temp_dir, filename), 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
    
    def tearDown(self):
        """Clean up test fixtures"""
        shutil.rmtree(self.temp_dir)
    
    def test_handle_empty_files(self):
        """Test handling of empty files"""
        extractor = DataExtractor()
        stages_data, errors = extractor.extract_stages_from_directory(self.temp_dir)
        
        self.assertIsNotNone(stages_data)
        self.assertIn("empty_list.json", stages_data)
        self.assertEqual(stages_data["empty_list.json"], [])
    
    def test_handle_malformed_data(self):
        """Test handling of malformed stage data"""
        extractor = DataExtractor()
        stages_data, errors = extractor.extract_stages_from_directory(self.temp_dir)
        
        self.assertIsNotNone(stages_data)
        self.assertIn("malformed_stage.json", stages_data)
        self.assertEqual(stages_data["malformed_stage.json"], [None])
    
    def test_handle_missing_stages(self):
        """Test handling of missing stage information"""
        extractor = DataExtractor()
        stages_data, errors = extractor.extract_stages_from_directory(self.temp_dir)
        
        self.assertIsNotNone(stages_data)
        self.assertIn("no_stage.json", stages_data)
        self.assertEqual(stages_data["no_stage.json"], [None])
    
    def test_handle_complex_nesting(self):
        """Test handling of complex nested quotes"""
        extractor = DataExtractor()
        stages_data, errors = extractor.extract_stages_from_directory(self.temp_dir)
        
        self.assertIsNotNone(stages_data)
        self.assertIn("complex_nesting.json", stages_data)
        self.assertEqual(stages_data["complex_nesting.json"], ["设置议程"])


def run_all_tests():
    """Run all tests with detailed output"""
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test classes
    test_classes = [
        TestStageExtractor,
        TestSuggestionExtractor,
        TestDataExtractor,
        TestUtilityFunctions,
        TestEdgeCases
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Print summary
    print(f"\n{'='*60}")
    print(f"Data Extractor Test Summary:")
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
    print(f"{'='*60}")
    
    return result.wasSuccessful()


if __name__ == '__main__':
    # Run all tests
    success = run_all_tests()
    
    # Exit with appropriate code
    exit(0 if success else 1) 