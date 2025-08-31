"""
Mediation analysis for CausalEM.

This module provides functionality for mediation analysis using plug-in 
G-computation with optional stochastic matching. Supports both binary and 
continuous mediators and outcomes, with bootstrap confidence intervals.
"""

from ._experimental import estimate_mediation

__all__ = ["estimate_mediation"]