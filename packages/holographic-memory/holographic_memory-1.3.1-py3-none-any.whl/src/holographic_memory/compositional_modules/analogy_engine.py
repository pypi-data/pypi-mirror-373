"""
Analogy Engine for Compositional Structures

Implements Plate (1995) Section VI "Analogies" (pages 633-636).
Addresses FIXME #3: Missing analogy and similarity operations with structural
analogy detection and compositional reasoning capabilities.

Research-Accurate Implementation of:
- "A is to B as C is to D" analogical reasoning with HRRs
- Structural analogy detection between different composition types
- Similarity metrics that consider compositional relationships
- Analogical completion for partial structures

Based on: Plate (1995) Section VI, page 633; Equation (15) analogy formula
"""

import numpy as np
from typing import Dict, Any, List, Optional, Tuple, Union
from dataclasses import dataclass
import logging

from .structure_types import StructureType

logger = logging.getLogger(__name__)


@dataclass 
class AnalogyResult:
    """Result of analogical reasoning operation"""
    result_vector: np.ndarray
    confidence: float
    analogy_type: str
    transformation_vector: np.ndarray
    metadata: Dict[str, Any]


@dataclass
class StructuralSimilarity:
    """Structural similarity between two compositions"""
    overall_similarity: float
    component_similarities: List[float]
    structural_alignment: float
    role_filler_consistency: float
    metadata: Dict[str, Any]


class AnalogyEngine:
    """
    Research-Accurate Analogy Engine for Compositional HRR
    
    Implements Plate (1995) Section VI analogical reasoning:
    "A is to B as C is to D" using Equation (15): D ≈ C ⊛ (B ⊛ A⁻¹)
    
    Key Research Contributions:
    1. Compositional analogy using circular correlation for transformation
    2. Structural similarity metrics for role-filler relationships
    3. Analogical completion for partial compositional structures
    4. Multi-level analogy detection (surface, structural, relational)
    """
    
    def __init__(self, 
                 vector_dim: int = 512,
                 similarity_threshold: float = 0.3,
                 analogy_confidence_threshold: float = 0.5):
        """
        Initialize Analogy Engine
        
        Args:
            vector_dim: Dimensionality of vectors
            similarity_threshold: Minimum similarity for meaningful comparison
            analogy_confidence_threshold: Minimum confidence for valid analogy
        """
        self.vector_dim = vector_dim
        self.similarity_threshold = similarity_threshold
        self.analogy_confidence_threshold = analogy_confidence_threshold
        
        # Analogy operation cache for efficiency
        self.transformation_cache = {}
        
        # Statistics
        self.analogy_stats = {
            "total_analogies": 0,
            "successful_analogies": 0,
            "cache_hits": 0,
            "analogy_types": {}
        }
    
    def compute_analogy(self, 
                       A: np.ndarray, 
                       B: np.ndarray, 
                       C: np.ndarray,
                       analogy_type: str = "standard") -> AnalogyResult:
        """
        Research-Accurate Analogical Reasoning
        
        Implements Plate (1995) Equation (15): A:B :: C:? → ? = C ⊛ (B ⊛ A⁻¹)
        
        The analogy "A is to B as C is to D" is computed by:
        1. Computing transformation T = B ⊛ A⁻¹ (what changes A into B)
        2. Applying transformation to C: D = C ⊛ T
        
        Args:
            A: Source vector in analogy
            B: Target vector in analogy  
            C: Query vector for analogy completion
            analogy_type: Type of analogy ("standard", "structural", "relational")
            
        Returns:
            AnalogyResult with computed D vector and metadata
        """
        self.analogy_stats["total_analogies"] += 1
        self.analogy_stats["analogy_types"][analogy_type] = \
            self.analogy_stats["analogy_types"].get(analogy_type, 0) + 1
        
        # Normalize inputs
        A_norm = A / (np.linalg.norm(A) + 1e-10)
        B_norm = B / (np.linalg.norm(B) + 1e-10)
        C_norm = C / (np.linalg.norm(C) + 1e-10)
        
        # Step 1: Compute A⁻¹ using circular correlation (approximate inverse)
        A_inverse = self._circular_correlation(A_norm)
        
        # Step 2: Compute transformation T = B ⊛ A⁻¹
        transformation = self._circular_convolution(B_norm, A_inverse)
        
        # Step 3: Apply transformation to C: D = C ⊛ T
        result_vector = self._circular_convolution(C_norm, transformation)
        
        # Step 4: Assess confidence of analogy
        confidence = self._assess_analogy_confidence(A_norm, B_norm, C_norm, result_vector)
        
        # Step 5: Apply type-specific refinements
        if analogy_type == "structural":
            result_vector, confidence = self._refine_structural_analogy(
                A_norm, B_norm, C_norm, result_vector, confidence
            )
        elif analogy_type == "relational":
            result_vector, confidence = self._refine_relational_analogy(
                A_norm, B_norm, C_norm, result_vector, confidence
            )
        
        # Update success statistics
        if confidence >= self.analogy_confidence_threshold:
            self.analogy_stats["successful_analogies"] += 1
        
        logger.debug(f"Analogy computed: type={analogy_type}, confidence={confidence:.3f}")
        
        return AnalogyResult(
            result_vector=result_vector,
            confidence=confidence,
            analogy_type=analogy_type,
            transformation_vector=transformation,
            metadata={
                "A_norm": np.linalg.norm(A),
                "B_norm": np.linalg.norm(B),
                "C_norm": np.linalg.norm(C),
                "transformation_magnitude": np.linalg.norm(transformation)
            }
        )
    
    def _circular_convolution(self, x: np.ndarray, y: np.ndarray) -> np.ndarray:
        """
        Circular convolution operation for HRR binding
        
        Implements the ⊛ operator using FFT for efficiency
        """
        # Use FFT for efficient circular convolution
        X = np.fft.fft(x)
        Y = np.fft.fft(y) 
        result = np.fft.ifft(X * Y).real
        
        # Normalize result
        return result / (np.linalg.norm(result) + 1e-10)
    
    def _circular_correlation(self, x: np.ndarray) -> np.ndarray:
        """
        Circular correlation (approximate inverse) operation
        
        Implements the approximate inverse x⁻¹ for HRR unbinding
        """
        # Circular correlation is convolution with time-reversed signal
        # For complex frequency domain: conjugate
        X = np.fft.fft(x)
        X_conj = np.conj(X)
        result = np.fft.ifft(X_conj).real
        
        # Normalize result  
        return result / (np.linalg.norm(result) + 1e-10)
    
    def _assess_analogy_confidence(self, 
                                  A: np.ndarray, 
                                  B: np.ndarray, 
                                  C: np.ndarray, 
                                  D: np.ndarray) -> float:
        """
        Assess confidence in analogical reasoning result
        
        Uses multiple consistency checks to evaluate analogy quality
        """
        confidence_factors = []
        
        # Factor 1: Transformation consistency
        # Check if applying the same transformation to A gives B
        A_inverse = self._circular_correlation(A)
        transformation = self._circular_convolution(B, A_inverse)
        reconstructed_B = self._circular_convolution(A, transformation)
        
        b_consistency = max(0, np.dot(B, reconstructed_B))
        confidence_factors.append(("transformation_consistency", b_consistency))
        
        # Factor 2: Reverse transformation consistency  
        # Check if we can recover C from D using inverse transformation
        T_inverse = self._circular_correlation(transformation)
        reconstructed_C = self._circular_convolution(D, T_inverse)
        
        c_consistency = max(0, np.dot(C, reconstructed_C))
        confidence_factors.append(("reverse_consistency", c_consistency))
        
        # Factor 3: Magnitude preservation
        # HRR operations should approximately preserve magnitude relationships
        AB_ratio = np.linalg.norm(B) / (np.linalg.norm(A) + 1e-10)
        CD_ratio = np.linalg.norm(D) / (np.linalg.norm(C) + 1e-10)
        
        magnitude_consistency = 1.0 - min(1.0, abs(AB_ratio - CD_ratio))
        confidence_factors.append(("magnitude_consistency", magnitude_consistency))
        
        # Factor 4: Statistical properties consistency
        # Check if result has reasonable HRR vector properties
        d_mean = abs(np.mean(D))
        d_std = np.std(D)
        expected_std = 1.0 / np.sqrt(len(D))
        
        stats_consistency = 1.0 - min(1.0, d_mean + abs(d_std - expected_std))
        confidence_factors.append(("stats_consistency", stats_consistency))
        
        # Combine confidence factors with weights
        weights = [0.4, 0.3, 0.2, 0.1]  # Emphasize transformation consistency
        overall_confidence = sum(w * factor[1] for w, factor in zip(weights, confidence_factors))
        
        logger.debug(f"Confidence factors: {confidence_factors}")
        
        return max(0.0, min(1.0, overall_confidence))
    
    def _refine_structural_analogy(self, 
                                  A: np.ndarray, 
                                  B: np.ndarray, 
                                  C: np.ndarray, 
                                  D: np.ndarray, 
                                  base_confidence: float) -> Tuple[np.ndarray, float]:
        """
        Refine analogy for structural consistency
        
        Applies structure-aware refinements to improve analogical reasoning
        for compositional structures.
        """
        # For structural analogies, check if the transformation preserves
        # compositional structure types
        
        # Approach 1: Iterative refinement
        refined_D = D.copy()
        
        # Apply mild cleanup to ensure proper HRR properties
        refined_D = refined_D - np.mean(refined_D)  # Zero mean
        refined_D = refined_D / (np.linalg.norm(refined_D) + 1e-10)  # Unit norm
        
        # Approach 2: Structural pattern matching
        # (Would require access to structure type information)
        # For now, apply general compositional refinements
        
        # Boost confidence for well-formed results
        d_properties_score = self._assess_vector_properties(refined_D)
        refined_confidence = base_confidence * (0.5 + 0.5 * d_properties_score)
        
        return refined_D, refined_confidence
    
    def _refine_relational_analogy(self, 
                                  A: np.ndarray, 
                                  B: np.ndarray, 
                                  C: np.ndarray, 
                                  D: np.ndarray, 
                                  base_confidence: float) -> Tuple[np.ndarray, float]:
        """
        Refine analogy for relational consistency
        
        Focuses on preserving relational structures in analogical reasoning
        """
        # For relational analogies, ensure that relationships between
        # components are preserved
        
        refined_D = D.copy()
        
        # Check relationship preservation
        # A-B relationship should be similar to C-D relationship
        AB_relationship = self._circular_convolution(
            self._circular_correlation(A), B
        )
        CD_relationship = self._circular_convolution(
            self._circular_correlation(C), refined_D
        )
        
        relationship_similarity = max(0, np.dot(AB_relationship, CD_relationship))
        
        # Adjust confidence based on relationship preservation
        refined_confidence = base_confidence * (0.3 + 0.7 * relationship_similarity)
        
        return refined_D, refined_confidence
    
    def _assess_vector_properties(self, vector: np.ndarray) -> float:
        """Assess how well a vector satisfies HRR properties"""
        # Check mean (should be ~0)
        mean_score = max(0, 1.0 - 5 * abs(np.mean(vector)))
        
        # Check standard deviation (should be ~1/sqrt(n))
        expected_std = 1.0 / np.sqrt(len(vector))
        std_score = max(0, 1.0 - abs(np.std(vector) - expected_std) / expected_std)
        
        # Check normalization (should be ~1)
        norm_score = max(0, 1.0 - abs(np.linalg.norm(vector) - 1.0))
        
        return (mean_score + std_score + norm_score) / 3.0
    
    def compute_structural_similarity(self, 
                                    structure1: np.ndarray,
                                    structure2: np.ndarray, 
                                    structure_type1: Optional[StructureType] = None,
                                    structure_type2: Optional[StructureType] = None) -> StructuralSimilarity:
        """
        Compute structural similarity between compositional structures
        
        Goes beyond simple cosine similarity to consider compositional
        relationships and role-filler bindings.
        
        Args:
            structure1: First compositional structure
            structure2: Second compositional structure
            structure_type1: Type hint for first structure
            structure_type2: Type hint for second structure
            
        Returns:
            StructuralSimilarity with detailed similarity analysis
        """
        # Normalize inputs
        s1_norm = structure1 / (np.linalg.norm(structure1) + 1e-10)
        s2_norm = structure2 / (np.linalg.norm(structure2) + 1e-10)
        
        # Component 1: Overall similarity (cosine similarity)
        overall_similarity = max(0, np.dot(s1_norm, s2_norm))
        
        # Component 2: Component similarities (analyze sub-patterns)
        component_similarities = self._compute_component_similarities(s1_norm, s2_norm)
        
        # Component 3: Structural alignment (role-structure preservation)
        structural_alignment = self._compute_structural_alignment(
            s1_norm, s2_norm, structure_type1, structure_type2
        )
        
        # Component 4: Role-filler consistency
        role_filler_consistency = self._compute_role_filler_consistency(s1_norm, s2_norm)
        
        logger.debug(f"Structural similarity: overall={overall_similarity:.3f}, "
                    f"alignment={structural_alignment:.3f}, "
                    f"role_filler={role_filler_consistency:.3f}")
        
        return StructuralSimilarity(
            overall_similarity=overall_similarity,
            component_similarities=component_similarities,
            structural_alignment=structural_alignment,
            role_filler_consistency=role_filler_consistency,
            metadata={
                "structure_type1": structure_type1.value if structure_type1 else None,
                "structure_type2": structure_type2.value if structure_type2 else None,
                "vector_norms": [np.linalg.norm(structure1), np.linalg.norm(structure2)]
            }
        )
    
    def _compute_component_similarities(self, 
                                       s1: np.ndarray, 
                                       s2: np.ndarray) -> List[float]:
        """Compute similarities between vector components/segments"""
        # Divide vectors into segments and compare
        n_segments = min(8, len(s1) // 16)  # Reasonable number of segments
        
        if n_segments < 2:
            return [np.dot(s1, s2)]
        
        segment_size = len(s1) // n_segments
        similarities = []
        
        for i in range(n_segments):
            start_idx = i * segment_size
            end_idx = (i + 1) * segment_size if i < n_segments - 1 else len(s1)
            
            seg1 = s1[start_idx:end_idx]
            seg2 = s2[start_idx:end_idx]
            
            # Normalize segments
            seg1_norm = seg1 / (np.linalg.norm(seg1) + 1e-10)
            seg2_norm = seg2 / (np.linalg.norm(seg2) + 1e-10)
            
            similarity = max(0, np.dot(seg1_norm, seg2_norm))
            similarities.append(similarity)
        
        return similarities
    
    def _compute_structural_alignment(self, 
                                     s1: np.ndarray, 
                                     s2: np.ndarray,
                                     type1: Optional[StructureType],
                                     type2: Optional[StructureType]) -> float:
        """Compute structural alignment between compositions"""
        # Basic alignment based on distribution properties
        
        # If types are different, reduce alignment score
        type_bonus = 1.0 if (type1 == type2 or type1 is None or type2 is None) else 0.7
        
        # Statistical alignment - similar distributions suggest similar structure
        s1_sorted = np.sort(np.abs(s1))[::-1]  # Sort by magnitude, descending
        s2_sorted = np.sort(np.abs(s2))[::-1]
        
        # Compare sorted magnitude profiles
        profile_similarity = max(0, np.corrcoef(s1_sorted[:20], s2_sorted[:20])[0, 1])
        if np.isnan(profile_similarity):
            profile_similarity = 0.0
        
        return type_bonus * profile_similarity
    
    def _compute_role_filler_consistency(self, s1: np.ndarray, s2: np.ndarray) -> float:
        """Compute role-filler consistency between structures"""
        # This is a simplified version - full implementation would require
        # knowledge of the actual role-filler decomposition
        
        # Use cross-correlation to detect similar binding patterns
        cross_correlation = np.correlate(s1, s2, mode='full')
        max_correlation = np.max(np.abs(cross_correlation))
        
        # Normalize by vector lengths
        normalized_correlation = max_correlation / (np.linalg.norm(s1) * np.linalg.norm(s2) + 1e-10)
        
        return max(0, min(1, normalized_correlation))
    
    def find_analogical_completions(self, 
                                   analogies: List[Tuple[np.ndarray, np.ndarray]], 
                                   query: np.ndarray,
                                   top_k: int = 5) -> List[AnalogyResult]:
        """
        Find analogical completions for a query using multiple analogy pairs
        
        Given multiple A:B analogies and a query C, find the best analogical
        completions C:D using each analogy pattern.
        
        Args:
            analogies: List of (A, B) analogy pairs
            query: Query vector C for completion
            top_k: Number of top results to return
            
        Returns:
            List of AnalogyResults sorted by confidence
        """
        results = []
        
        for i, (A, B) in enumerate(analogies):
            # Compute analogy: A:B :: query:?
            result = self.compute_analogy(A, B, query, analogy_type="standard")
            result.metadata["analogy_pair_index"] = i
            results.append(result)
        
        # Sort by confidence and return top-k
        results.sort(key=lambda r: r.confidence, reverse=True)
        
        logger.debug(f"Found {len(results)} analogical completions, "
                    f"top confidence: {results[0].confidence:.3f}")
        
        return results[:top_k]
    
    def get_analogy_statistics(self) -> Dict[str, Any]:
        """Get comprehensive analogy engine statistics"""
        stats = self.analogy_stats.copy()
        
        if stats["total_analogies"] > 0:
            stats["success_rate"] = stats["successful_analogies"] / stats["total_analogies"]
        else:
            stats["success_rate"] = 0.0
        
        return stats