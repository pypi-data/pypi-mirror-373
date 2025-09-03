"""
PRISM - AI-Powered Image Intelligence Engine
"""

__version__ = "0.1.0"
__author__ = "Olaoluwasubomi"
__email__ = "i@olaoluwasubomi.com"

from .core.analyzer import analyze, AnalysisResult

# Make the main function available at package level
__all__ = ['analyze', 'AnalysisResult', '__version__']
