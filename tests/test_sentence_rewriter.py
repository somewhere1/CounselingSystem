"""
Comprehensive test suite for the sentence_rewriter module.
Tests sentence rewriting functionality, integration with the counseling system, and performance.
"""

import unittest
import sys
import os
from unittest.mock import Mock, patch
import time
from typing import List, Dict

# Using absolute imports, no path modification needed

from refactored_counseling_system.utils.sentence_rewriter import (
    SentenceRewriter,
    CounselorResponseEnhancer,
    quick_rewrite,
    quick_enhance_counselor_response,
    integrate_with_counselor_agent
)


class TestSentenceRewriter(unittest.TestCase):
    """Test cases for SentenceRewriter class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.rewriter = SentenceRewriter()
        self.test_sentences = [
            "请您详细描述一下您的症状。",
            "我们需要对您的情况进行全面评估。",
            "根据您的描述，我认为您可能存在焦虑症状。",
            "建议您配合治疗并按时完成作业。",
            "今天我们可以先聊聊你现在的感受，看看是什么让你最近觉得迷茫。"
        ]
    
    @patch('refactored_counseling_system.utils.sentence_rewriter.get_llm_client')
    def test_rewrite_sentence_basic(self, mock_get_client):
        """Test basic sentence rewriting"""
        # Mock the LLM client
        mock_client = Mock()
        mock_client.generate_conversation_response.return_value = "你能跟我说说你的症状吗？"
        mock_get_client.return_value = mock_client
        
        # Test sentence rewriting
        original = "请您详细描述一下您的症状。"
        result = self.rewriter.rewrite_sentence(original)
        
        self.assertIsInstance(result, str)
        self.assertNotEqual(result, original)
        self.assertTrue(len(result) > 0)
    
    @patch('refactored_counseling_system.utils.sentence_rewriter.get_llm_client')
    def test_rewrite_with_context(self, mock_get_client):
        """Test context-aware sentence rewriting"""
        # Mock the LLM client
        mock_client = Mock()
        mock_client.generate_conversation_response.return_value = "你现在心情怎么样？"
        mock_get_client.return_value = mock_client
        
        # Test with context
        original = "请您描述一下您的情绪状态。"
        context = "CBT咨询的情绪检查阶段，需要温和地了解来访者的情绪状态"
        result = self.rewriter.rewrite_with_context(original, context)
        
        self.assertIsInstance(result, str)
        self.assertNotEqual(result, original)
        self.assertTrue(len(result) > 0)
    
    @patch('refactored_counseling_system.utils.sentence_rewriter.get_llm_client')
    def test_rewrite_multiple_sentences(self, mock_get_client):
        """Test batch sentence rewriting"""
        # Mock the LLM client
        mock_client = Mock()
        mock_client.generate_conversation_response.side_effect = [
            "你能跟我说说你的症状吗？",
            "我们来了解一下你的情况吧。",
            "从你说的情况来看，你可能有些焦虑。",
            "我们一起努力，按时做练习好吗？",
            "我们先聊聊你最近的感受，有什么特别困扰你的吗？"
        ]
        mock_get_client.return_value = mock_client
        
        # Test batch rewriting
        results = self.rewriter.rewrite_multiple_sentences(self.test_sentences)
        
        self.assertEqual(len(results), len(self.test_sentences))
        for i, result in enumerate(results):
            self.assertIn('original', result)
            self.assertIn('rewritten', result)
            self.assertEqual(result['original'], self.test_sentences[i])
            self.assertNotEqual(result['rewritten'], self.test_sentences[i])
    
    @patch('refactored_counseling_system.utils.sentence_rewriter.get_llm_client')
    def test_rewrite_cbt_stage_sentences(self, mock_get_client):
        """Test CBT stage-specific sentence rewriting"""
        # Mock the LLM client
        mock_client = Mock()
        mock_client.generate_conversation_response.return_value = "你现在心情怎么样？"
        mock_get_client.return_value = mock_client
        
        # Test CBT stage rewriting
        sentences = ["请您描述一下您的情绪状态。", "您感觉如何？"]
        results = self.rewriter.rewrite_cbt_stage_sentences(sentences, "情绪检查")
        
        self.assertEqual(len(results), 2)
        for result in results:
            self.assertIn('original', result)
            self.assertIn('rewritten', result)
            self.assertIn('context', result)
            self.assertIn('情绪检查', result['context'])
    
    @patch('refactored_counseling_system.utils.sentence_rewriter.get_llm_client')
    def test_enhance_counselor_response(self, mock_get_client):
        """Test counselor response enhancement"""
        # Mock the LLM client
        mock_client = Mock()
        mock_client.generate_conversation_response.return_value = "我们来谈谈你的感受吧。"
        mock_get_client.return_value = mock_client
        
        # Test response enhancement
        original = "我们需要讨论您的情感问题。"
        result = self.rewriter.enhance_counselor_response(original, "情绪检查")
        
        self.assertIsInstance(result, str)
        self.assertNotEqual(result, original)
        self.assertTrue(len(result) > 0)
    
    @patch('refactored_counseling_system.utils.sentence_rewriter.get_llm_client')
    def test_error_handling(self, mock_get_client):
        """Test error handling in sentence rewriting"""
        # Mock the LLM client to raise an exception
        mock_client = Mock()
        mock_client.generate_conversation_response.side_effect = Exception("API Error")
        mock_get_client.return_value = mock_client
        
        # Test error handling
        original = "请您详细描述一下您的症状。"
        result = self.rewriter.rewrite_sentence(original)
        
        # Should return original sentence on error
        self.assertEqual(result, original)


class TestCounselorResponseEnhancer(unittest.TestCase):
    """Test cases for CounselorResponseEnhancer class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.enhancer = CounselorResponseEnhancer()
    
    @patch('refactored_counseling_system.utils.sentence_rewriter.get_llm_client')
    def test_enhance_response(self, mock_get_client):
        """Test response enhancement with context"""
        # Mock the LLM client
        mock_client = Mock()
        mock_client.generate_conversation_response.return_value = "你现在感觉怎么样？"
        mock_get_client.return_value = mock_client
        
        # Test response enhancement
        original = "请描述您的情绪状态。"
        context = {
            'current_stage': '情绪检查',
            'patient_emotion': '焦虑',
            'session_type': '首次会话'
        }
        result = self.enhancer.enhance_response(original, context)
        
        self.assertIsInstance(result, str)
        self.assertNotEqual(result, original)
        self.assertTrue(len(result) > 0)
    
    @patch('refactored_counseling_system.utils.sentence_rewriter.get_llm_client')
    def test_enhance_multiple_responses(self, mock_get_client):
        """Test batch response enhancement"""
        # Mock the LLM client
        mock_client = Mock()
        mock_client.generate_conversation_response.side_effect = [
            "你现在感觉怎么样？",
            "我们来聊聊你的情况吧。"
        ]
        mock_get_client.return_value = mock_client
        
        # Test batch enhancement
        responses = ["请描述您的情绪状态。", "我们需要了解您的情况。"]
        context = {'current_stage': '情绪检查'}
        results = self.enhancer.enhance_multiple_responses(responses, context)
        
        self.assertEqual(len(results), 2)
        for result in results:
            self.assertIsInstance(result, str)
            self.assertTrue(len(result) > 0)


class TestUtilityFunctions(unittest.TestCase):
    """Test cases for utility functions"""
    
    @patch('refactored_counseling_system.utils.sentence_rewriter.get_llm_client')
    def test_quick_rewrite(self, mock_get_client):
        """Test quick_rewrite function"""
        # Mock the LLM client
        mock_client = Mock()
        mock_client.generate_conversation_response.return_value = "你能跟我说说吗？"
        mock_get_client.return_value = mock_client
        
        # Test quick rewrite
        original = "请您详细描述一下。"
        result = quick_rewrite(original)
        
        self.assertIsInstance(result, str)
        self.assertNotEqual(result, original)
    
    @patch('refactored_counseling_system.utils.sentence_rewriter.get_llm_client')
    def test_quick_enhance_counselor_response(self, mock_get_client):
        """Test quick_enhance_counselor_response function"""
        # Mock the LLM client
        mock_client = Mock()
        mock_client.generate_conversation_response.return_value = "我们来谈谈吧。"
        mock_get_client.return_value = mock_client
        
        # Test quick enhancement
        original = "我们需要讨论您的情况。"
        result = quick_enhance_counselor_response(original, "对话")
        
        self.assertIsInstance(result, str)
        self.assertNotEqual(result, original)
    
    @patch('refactored_counseling_system.utils.sentence_rewriter.get_llm_client')
    def test_integrate_with_counselor_agent(self, mock_get_client):
        """Test integration with counselor agent"""
        # Mock the LLM client
        mock_client = Mock()
        mock_client.generate_conversation_response.return_value = "你现在感觉怎么样？"
        mock_get_client.return_value = mock_client
        
        # Test integration
        original = "请描述您的情绪状态。"
        result = integrate_with_counselor_agent(
            original, 
            "情绪检查", 
            "焦虑", 
            "首次会话"
        )
        
        self.assertIsInstance(result, str)
        self.assertNotEqual(result, original)


class TestPerformance(unittest.TestCase):
    """Performance tests for sentence rewriter"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.rewriter = SentenceRewriter()
        self.large_sentence_list = [
            f"这是第{i}个测试句子，用于测试批量处理性能。" for i in range(100)
        ]
    
    @patch('refactored_counseling_system.utils.sentence_rewriter.get_llm_client')
    def test_batch_processing_performance(self, mock_get_client):
        """Test performance of batch processing"""
        # Mock the LLM client
        mock_client = Mock()
        mock_client.generate_conversation_response.side_effect = [
            f"这是第{i}个改写句子。" for i in range(100)
        ]
        mock_get_client.return_value = mock_client
        
        # Time the batch processing
        start_time = time.time()
        results = self.rewriter.rewrite_multiple_sentences(self.large_sentence_list[:10])  # Test with 10 sentences
        end_time = time.time()
        
        # Check results
        self.assertEqual(len(results), 10)
        processing_time = end_time - start_time
        
        # Should complete in reasonable time (adjust threshold as needed)
        self.assertLess(processing_time, 30.0)  # 30 seconds threshold
        
        print(f"Batch processing of 10 sentences took {processing_time:.2f} seconds")


class TestIntegration(unittest.TestCase):
    """Integration tests with the counseling system"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.rewriter = SentenceRewriter()
        self.enhancer = CounselorResponseEnhancer()
    
    @patch('refactored_counseling_system.utils.sentence_rewriter.get_llm_client')
    def test_integration_with_cbt_stages(self, mock_get_client):
        """Test integration with CBT stages"""
        # Mock the LLM client
        mock_client = Mock()
        mock_client.generate_conversation_response.return_value = "你现在心情怎么样？"
        mock_get_client.return_value = mock_client
        
        # Test different CBT stages
        stages = ["设置议程", "情绪检查", "获取信息", "讨论诊断", "问题识别", "认知模型", "行为激活", "总结作业"]
        test_sentence = "我们需要进行下一步的工作。"
        
        for stage in stages:
            result = self.rewriter.rewrite_cbt_stage_sentences([test_sentence], stage)
            self.assertEqual(len(result), 1)
            self.assertIn(stage, result[0]['context'])
    
    @patch('refactored_counseling_system.utils.sentence_rewriter.get_llm_client')
    def test_integration_with_dialogue_context(self, mock_get_client):
        """Test integration with dialogue context"""
        # Mock the LLM client
        mock_client = Mock()
        mock_client.generate_conversation_response.return_value = "你现在感觉怎么样？"
        mock_get_client.return_value = mock_client
        
        # Test with various dialogue contexts
        contexts = [
            {'current_stage': '情绪检查', 'patient_emotion': '焦虑', 'session_type': '首次会话'},
            {'current_stage': '问题识别', 'patient_emotion': '抑郁', 'session_type': '后续会话'},
            {'current_stage': '认知模型', 'patient_emotion': '平静', 'session_type': '首次会话'},
        ]
        
        original = "请描述您的情况。"
        
        for context in contexts:
            result = self.enhancer.enhance_response(original, context)
            self.assertIsInstance(result, str)
            self.assertNotEqual(result, original)


class TestEdgeCases(unittest.TestCase):
    """Test edge cases and error conditions"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.rewriter = SentenceRewriter()
    
    def test_empty_string_input(self):
        """Test handling of empty string input"""
        result = self.rewriter.rewrite_sentence("")
        self.assertEqual(result, "")
    
    def test_very_long_sentence(self):
        """Test handling of very long sentences"""
        long_sentence = "这是一个很长的句子，" * 100
        result = self.rewriter.rewrite_sentence(long_sentence)
        self.assertIsInstance(result, str)
    
    def test_special_characters(self):
        """Test handling of special characters"""
        special_sentence = "测试特殊字符：@#￥%…&*()！？"
        result = self.rewriter.rewrite_sentence(special_sentence)
        self.assertIsInstance(result, str)
    
    def test_unicode_characters(self):
        """Test handling of unicode characters"""
        unicode_sentence = "测试unicode字符：😊👍🎉"
        result = self.rewriter.rewrite_sentence(unicode_sentence)
        self.assertIsInstance(result, str)


def run_all_tests():
    """Run all tests with detailed output"""
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test classes
    test_classes = [
        TestSentenceRewriter,
        TestCounselorResponseEnhancer,
        TestUtilityFunctions,
        TestPerformance,
        TestIntegration,
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
    print(f"Test Summary:")
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