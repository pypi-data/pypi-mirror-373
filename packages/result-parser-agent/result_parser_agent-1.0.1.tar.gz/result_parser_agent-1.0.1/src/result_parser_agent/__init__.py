"""Results Parser Agent - A deep agent for extracting metrics from result files."""

from .agent.parser_agent import ResultsParserAgent
from .config.settings import settings

__version__ = "0.2.1"
__author__ = "Your Name"
__email__ = "your.email@example.com"

__all__ = [
    "ResultsParserAgent",
    "settings",
]
