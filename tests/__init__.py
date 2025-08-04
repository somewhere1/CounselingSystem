"""
Test package for the counseling system.
Contains comprehensive test suites for all system components.
"""

# Test utilities can be imported here if needed
from .test_sentence_rewriter import run_all_tests as run_sentence_rewriter_tests
from .test_data_extractor import run_all_tests as run_data_extractor_tests

__all__ = ["run_sentence_rewriter_tests", "run_data_extractor_tests"] 