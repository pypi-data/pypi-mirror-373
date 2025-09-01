"""
Verskyt: A library for Tversky Neural Networks.

Psychologically plausible deep learning with differentiable Tversky similarity.
"""

__version__ = "0.1.0"

from verskyt.benchmarks import (
    XORBenchmark,
    run_fast_xor_benchmark,
    run_full_xor_replication,
)
from verskyt.core import tversky_similarity
from verskyt.interventions import (
    ConceptGrounding,
    ConceptLibrary,
    CounterfactualAnalyzer,
    FeatureGrounder,
    ImpactAssessment,
    InterventionManager,
)
from verskyt.layers import TverskyProjectionLayer, TverskySimilarityLayer

__all__ = [
    "tversky_similarity",
    "TverskyProjectionLayer",
    "TverskySimilarityLayer",
    "run_fast_xor_benchmark",
    "run_full_xor_replication",
    "XORBenchmark",
    "InterventionManager",
    "CounterfactualAnalyzer",
    "ImpactAssessment",
    "FeatureGrounder",
    "ConceptGrounding",
    "ConceptLibrary",
]
