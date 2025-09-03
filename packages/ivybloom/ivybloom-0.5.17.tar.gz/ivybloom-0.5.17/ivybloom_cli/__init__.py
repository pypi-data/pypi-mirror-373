"""
ivybloom CLI - Command-line interface for Ivy Biosciences Platform
Computational Biology & Drug Discovery
"""

__version__ = "0.5.17"
__author__ = "Ivy Biosciences"
__email__ = "support@ivybiosciences.com"
__description__ = "Command-line interface for computational biology and drug discovery"

from .client.api_client import IvyBloomAPIClient
from .utils.config import Config
from .utils.auth import AuthManager

__all__ = [
    "IvyBloomAPIClient",
    "Config", 
    "AuthManager",
    "__version__"
]
