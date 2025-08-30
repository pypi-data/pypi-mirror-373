"""
AstroInsight - AI-powered research paper assistant with multi-agent collaboration

A comprehensive tool for research paper analysis, hypothesis generation,
and multi-agent collaborative optimization.
"""

from .api.paper_api import PaperAPI
from .core.astroinsight import AstroInsight
from .core.config import AstroInsightConfig
from .utils.generator import generate_paper

__version__ = "0.1.0"
__author__ = "AstroInsight Team"
__email__ = "contact@astroinsight.com"

__all__ = [
    "AstroInsight",
    "AstroInsightConfig",
    "PaperAPI",
    "generate_paper",
]
