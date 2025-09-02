# -*- coding: utf-8 -*-
"""
Data models for plugins.
"""

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

import numpy as np


@dataclass
class InferenceRequest:
    """Request for probabilistic inference"""

    model_code: str
    query_variables: List[str]
    evidence: Optional[Dict[str, Any]] = None
    num_samples: int = 1000
    inference_method: str = "mcmc"  # mcmc, svi, nuts


@dataclass
class InferenceResult:
    """Result of probabilistic inference"""

    posterior_samples: Dict[str, np.ndarray]
    summary_statistics: Dict[str, Dict[str, float]]
    credible_intervals: Dict[str, Tuple[float, float]]
    marginal_likelihoods: Dict[str, float]
    uncertainty_measures: Dict[str, float]
    confidence_score: float
    execution_time: float
    convergence_diagnostics: Dict[str, Any]
    errors: List[str] = None