"""
xSystem Performance Management Package.

This package provides generic performance management functionality that can be
used by any library in the xComBot framework.
"""

from .manager import GenericPerformanceManager, HealthStatus, PerformanceRecommendation

__all__ = ["GenericPerformanceManager", "PerformanceRecommendation", "HealthStatus"]
