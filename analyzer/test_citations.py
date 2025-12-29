#!/usr/bin/env python3
"""Tests for CitationCountMetric in analyzer/src/metrics/dynamic/."""

import sys
import os
from unittest.mock import Mock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from analyzer.src.metrics.dynamic.citation_count import UpdateCitationCount
from analyzer.src.metrics.base import Benchmark


class MockBenchmark(Benchmark):
    """Concrete benchmark for testing."""
    def __init__(self, paper_url=None):
        super().__init__('test_benchmark', paper_url=paper_url)

    def refresh(self):
        pass


def test_parse_paper_id():
    """Test Semantic Scholar URL parsing."""
    metric = UpdateCitationCount()

    # Valid S2 URL
    url = 'https://www.semanticscholar.org/paper/BERT-Devlin-Chang/abc123def456'
    assert metric._parse_paper_id(url) == 'abc123def456'

    # Invalid URL
    assert metric._parse_paper_id('https://example.com/random') is None

    print("URL parsing tests passed!")


def test_compute_returns_zero_on_missing_url():
    """Test that missing paper_url returns 0."""
    metric = UpdateCitationCount()
    benchmark = MockBenchmark(paper_url=None)
    assert metric._compute_current(benchmark) == 0
    print("No URL test passed!")


def test_compute_returns_zero_on_invalid_url():
    """Test that invalid paper_url returns 0."""
    metric = UpdateCitationCount()
    benchmark = MockBenchmark(paper_url='https://example.com/not-a-paper')
    assert metric._compute_current(benchmark) == 0
    print("Invalid URL test passed!")


def test_compute_returns_citation_count():
    """Test successful citation fetch."""
    metric = UpdateCitationCount()

    mock_paper = Mock()
    mock_paper.citationCount = 150
    mock_client = Mock()
    mock_client.get_paper.return_value = mock_paper
    metric._client = mock_client

    benchmark = MockBenchmark(paper_url='https://www.semanticscholar.org/paper/Title/abc123def')
    result = metric._compute_current(benchmark)

    assert result == 150
    mock_client.get_paper.assert_called_once_with('abc123def')
    print("Success test passed!")


def test_compute_returns_zero_on_api_error():
    """Test that API errors return 0."""
    metric = UpdateCitationCount()

    mock_client = Mock()
    mock_client.get_paper.side_effect = Exception('API Error')
    metric._client = mock_client

    benchmark = MockBenchmark(paper_url='https://www.semanticscholar.org/paper/Title/abc123def')
    result = metric._compute_current(benchmark)

    assert result == 0
    print("API error test passed!")


if __name__ == '__main__':
    test_parse_paper_id()
    test_compute_returns_zero_on_missing_url()
    test_compute_returns_zero_on_invalid_url()
    test_compute_returns_citation_count()
    test_compute_returns_zero_on_api_error()
    print("\nAll tests passed!")
