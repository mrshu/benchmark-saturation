import os
import re
from typing import Optional

from analyzer.src.metrics.dynamic.base import UpdatableMetric
from analyzer.src.metrics.base import Benchmark


class UpdateCitationCount(UpdatableMetric):
    """
    Dynamic metric that fetches citation count from Semantic Scholar API.

    Expects benchmark.paper_url to be a Semantic Scholar URL.
    Returns 0 if paper cannot be found or on API errors.
    """

    def __init__(self, update_frequency_days: int = 7):
        super().__init__(
            name='citation_count',
            description='Number of citations from Semantic Scholar',
            update_frequency_days=update_frequency_days
        )
        self._client = None

    @property
    def client(self):
        """Lazy-load Semantic Scholar client."""
        if self._client is None:
            from semanticscholar import SemanticScholar
            api_key = os.environ.get('SEMANTIC_SCHOLAR_API_KEY')
            self._client = SemanticScholar(api_key=api_key) if api_key else SemanticScholar()
        return self._client

    def _compute_current(self, benchmark: Benchmark) -> float:
        """Fetch current citation count for the benchmark's paper."""
        if not benchmark.paper_url:
            return 0

        paper_id = self._parse_paper_id(benchmark.paper_url)
        if not paper_id:
            return 0

        try:
            paper = self.client.get_paper(paper_id)
            return paper.citationCount or 0
        except Exception:
            return 0

    def _parse_paper_id(self, url: str) -> Optional[str]:
        """Extract paper ID from Semantic Scholar URL."""
        # https://www.semanticscholar.org/paper/Title-Here/abc123def456
        match = re.search(r'semanticscholar\.org/paper/[^/]+/([a-f0-9]+)', url, re.IGNORECASE)
        if match:
            return match.group(1)
        return None

    def _get_benchmark_id(self, benchmark: Benchmark) -> str:
        """Use dataset name as benchmark identifier."""
        return benchmark.dataset_name or str(id(benchmark))
