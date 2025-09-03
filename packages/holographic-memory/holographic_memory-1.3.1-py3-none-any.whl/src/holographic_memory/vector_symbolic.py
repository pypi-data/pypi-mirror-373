"""
Vector Symbolic Architecture (VSA) for Holographic Memory
Based on: Plate (1995) "Holographic Reduced Representations" and
         Gayler (1998) "Multiplicative Binding, Representation Operators & Analogy"

Implements Vector Symbolic Architectures using circular convolution binding
for cognitive modeling and symbolic reasoning with distributed representations.
"""

import numpy as np
from typing import Dict, Any, List, Optional, Union, Tuple, Set, Callable
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
import logging
from enum import Enum

from .core.holographic_memory import HolographicMemory
from .configuration import HolographicMemoryConfig

class VSAOperation(Enum):
    """Types of VSA operations"""
    BIND = "bind"           # Circular convolution (⊛)
    UNBIND = "unbind"       # Circular correlation (⊕)
    SUPERPOSE = "superpose" # Vector addition (+)
    PERMUTE = "permute"     # Permutation transformation
    POWER = "power"         # Self-binding (x⊛x⊛...⊛x)
    NORMALIZE = "normalize" # Vector normalization

@dataclass
class VSASymbol:
    """Represents a symbol in Vector Symbolic Architecture"""
    name: str
    vector: np.ndarray
    symbol_type: str = "atomic"  # atomic, composite, role, filler
    metadata: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

@dataclass
class VSAExpression:
    """Represents a symbolic expression using VSA operations"""
    operation: VSAOperation
    operands: List[Union[VSASymbol, 'VSAExpression']]
    result_vector: Optional[np.ndarray] = None
    expression_string: Optional[str] = None

class VectorSymbolicArchitecture:
    """
    Vector Symbolic Architecture implementation using Holographic Reduced Representations
    
    Features:
    - Circular convolution binding for compositional structures
    - Symbol vocabulary management
    - Expression evaluation and manipulation
    - Analogical reasoning capabilities
    - Memory retrieval and pattern completion
    """
    
    def __init__(self,
                 vector_dim: int = 512,
                 normalize_vectors: bool = True,
                 noise_level: float = 0.0,
                 random_seed: Optional[int] = None
                 # FIXME: Critical Issues in VectorSymbolicArchitecture __init__
                 #
                 # 1. INCORRECT DEFAULT VECTOR DIMENSION (512 vs research-accurate)
                 #    - Plate (1995) used dimensions 256-1024 for different experiments
                 #    - 512 may be suboptimal for many cognitive modeling tasks
                 #    - Different applications need different dimension trade-offs
                 #    - Solutions:
                 #      a) Use dimension based on application: vector_dim = "auto"
                 #      b) Add dimension selection guidance based on symbol count
                 #      c) Implement adaptive dimensionality based on binding capacity
                 #    - Research basis: Capacity scales with dimension but computational cost increases
                 #    - Example:
                 #      ```python
                 #      # Auto-select dimension based on expected symbols
                 #      if vector_dim == "auto":
                 #          expected_symbols = metadata.get('symbol_count', 100)
                 #          vector_dim = max(256, int(expected_symbols * 2.5))  # Capacity rule-of-thumb
                 #      ```
                 #
                 # 2. MISSING CRITICAL HRR PARAMETERS
                 #    - No control over vector distribution (should be i.i.d. normal or uniform)
                 #    - Missing binding capacity parameters
                 #    - No cleanup memory configuration
                 #    - Solutions:
                 #      a) Add: vector_distribution: str = 'normal'  # 'normal', 'uniform', 'bernoulli'
                 #      b) Add: cleanup_threshold: float = 0.3  # Similarity threshold for cleanup
                 #      c) Add: max_binding_depth: int = 10  # Prevent infinite recursion
                 #    - Example:
                 #      ```python
                 #      # HRR-specific parameters from Plate (1995)
                 #      self.vector_distribution = vector_distribution  
                 #      self.cleanup_threshold = cleanup_threshold
                 #      self.max_binding_depth = max_binding_depth
                 #      ```
                 #
                 # 3. INCORRECT NOISE MODEL (Gaussian vs structured noise)
                 #    - Simple noise_level doesn't model realistic neural noise
                 #    - Missing structured noise patterns from neural implementation
                 #    - Should include correlated noise, dropout, and quantization
                 #    - Solutions:
                 #      a) Add noise types: 'gaussian', 'salt_pepper', 'dropout', 'quantization'
                 #      b) Implement correlated noise: noise_correlation: float = 0.1
                 #      c) Add temporal noise dynamics for memory decay
                 #    - Research basis: Neural systems have structured, not purely random noise
                 #
                 # 4. MISSING FUNDAMENTAL VSA PARAMETERS
                 #    - No fractal binding parameter for hierarchical structures
                 #    - Missing permutation operation parameters
                 #    - No frequency domain optimization flags
                 #    - Solutions:
                 #      a) Add: fractal_binding: bool = True  # Enable hierarchical structures
                 #      b) Add: permutation_seed: int = None  # Deterministic permutation generation
                 #      c) Add: frequency_domain: bool = True  # Use FFT optimization
                 #    - Critical for advanced VSA applications like analogical reasoning
                 ):
        """
        Initialize Vector Symbolic Architecture
        
        Args:
            vector_dim: Dimensionality of vectors
            normalize_vectors: Whether to normalize vectors
            noise_level: Noise level for robustness testing
            random_seed: Random seed for reproducibility
        """
        self.vector_dim = vector_dim
        self.normalize_vectors = normalize_vectors
        self.noise_level = noise_level
        
        if random_seed is not None:
            np.random.seed(random_seed)
        
        # Initialize holographic memory for underlying operations
        self.hrr_memory = HolographicMemory(
            vector_size=vector_dim,
            normalize_vectors=normalize_vectors,
            noise_level=noise_level
        )
        
        # Symbol vocabulary
        self.symbols = {}  # name -> VSASymbol
        self.expressions = {}  # name -> VSAExpression
        
        # Operation history for debugging
        self.operation_history = []
        
        # Initialize fundamental symbols
        self._initialize_fundamental_symbols()
    
    def _initialize_fundamental_symbols(self):
        """Initialize fundamental VSA symbols"""
        # Identity element for binding (approximately)
        identity = np.zeros(self.vector_dim)
        identity[0] = 1.0  # Impulse at zero frequency
        self.add_symbol("IDENTITY", identity, "fundamental")
        
        # Null/empty symbol
        null = np.zeros(self.vector_dim)
        self.add_symbol("NULL", null, "fundamental")
        
        # Random symbols for common roles
        common_roles = ["AGENT", "OBJECT", "LOCATION", "TIME", "MANNER", "CAUSE"]
        for role in common_roles:
            self.create_random_symbol(role, "role")
    
    def create_random_symbol(self, name: str, symbol_type: str = "atomic") -> VSASymbol:
        """
        Create a random symbol vector
        
        Args:
            name: Symbol name
            symbol_type: Type of symbol
            
        Returns:
            Created VSASymbol
        """
        # Generate random vector (typically from normal distribution)
        vector = np.random.normal(0, 1/np.sqrt(self.vector_dim), self.vector_dim)
        
        if self.normalize_vectors:
            vector = vector / (np.linalg.norm(vector) + 1e-8)
        
        return self.add_symbol(name, vector, symbol_type)
    
    def add_symbol(self, name: str, vector: np.ndarray, symbol_type: str = "atomic",
                   metadata: Optional[Dict[str, Any]] = None) -> VSASymbol:
        """
        Add a symbol to the vocabulary
        
        Args:
            name: Symbol name
            vector: Vector representation
            symbol_type: Type of symbol
            metadata: Additional metadata
            
        Returns:
            Created VSASymbol
        """
        if len(vector) != self.vector_dim:
            raise ValueError(f"Vector dimension {len(vector)} doesn't match architecture dimension {self.vector_dim}")
        
        symbol = VSASymbol(
            name=name,
            vector=vector.copy(),
            symbol_type=symbol_type,
            metadata=metadata or {}
        )
        
        self.symbols[name] = symbol
        return symbol
    
    def bind(self, symbol1: Union[str, VSASymbol, np.ndarray], 
             symbol2: Union[str, VSASymbol, np.ndarray]) -> np.ndarray:
        """
        Bind two symbols using circular convolution
        
        Args:
            symbol1: First symbol (name, VSASymbol, or vector)
            symbol2: Second symbol (name, VSASymbol, or vector)
            
        Returns:
            Bound vector
        """
        vec1 = self._resolve_to_vector(symbol1)
        vec2 = self._resolve_to_vector(symbol2)
        
        # Use HRR memory's bind method
        result_hrr = self.hrr_memory.bind(vec1, vec2)
        result = result_hrr.data
        
        # Record operation
        self.operation_history.append({
            "operation": VSAOperation.BIND,
            "operands": [self._get_symbol_name(symbol1), self._get_symbol_name(symbol2)],
            "result_norm": np.linalg.norm(result)
        })
        
        return result
    
    def unbind(self, bound_vector: Union[str, VSASymbol, np.ndarray],
              symbol: Union[str, VSASymbol, np.ndarray]) -> np.ndarray:
        """
        Unbind a symbol from a bound vector using circular correlation
        
        Args:
            bound_vector: Vector containing bound information
            symbol: Symbol to unbind
            
        Returns:
            Unbound vector
        """
        bound_vec = self._resolve_to_vector(bound_vector)
        symbol_vec = self._resolve_to_vector(symbol)
        
        # Use HRR memory's circular correlation
        result = self.hrr_memory._circular_correlation(bound_vec, symbol_vec)
        
        # Record operation
        self.operation_history.append({
            "operation": VSAOperation.UNBIND,
            "operands": [self._get_symbol_name(bound_vector), self._get_symbol_name(symbol)],
            "result_norm": np.linalg.norm(result)
        })
        
        return result
    
    def superpose(self, *symbols: Union[str, VSASymbol, np.ndarray]) -> np.ndarray:
        """
        Superpose multiple symbols using vector addition
        
        Args:
            symbols: Symbols to superpose
            
        Returns:
            Superposed vector
        """
        if len(symbols) == 0:
            return np.zeros(self.vector_dim)
        
        result = np.zeros(self.vector_dim)
        symbol_names = []
        
        for symbol in symbols:
            vec = self._resolve_to_vector(symbol)
            result += vec
            symbol_names.append(self._get_symbol_name(symbol))
        
        if self.normalize_vectors:
            result = result / (np.linalg.norm(result) + 1e-8)
        
        # Record operation
        self.operation_history.append({
            "operation": VSAOperation.SUPERPOSE,
            "operands": symbol_names,
            "result_norm": np.linalg.norm(result)
        })
        
        return result
    
    def permute(self, symbol: Union[str, VSASymbol, np.ndarray], 
                permutation: Optional[np.ndarray] = None) -> np.ndarray:
        """
        Apply permutation to a symbol vector
        
        Args:
            symbol: Symbol to permute
            permutation: Permutation array (default: random cyclic shift)
            
        Returns:
            Permuted vector
        """
        vec = self._resolve_to_vector(symbol)
        
        if permutation is None:
            # Default: random cyclic shift
            shift = np.random.randint(1, self.vector_dim)
            result = np.roll(vec, shift)
        else:
            if len(permutation) != self.vector_dim:
                raise ValueError("Permutation must have same dimension as vectors")
            result = vec[permutation]
        
        # Record operation
        self.operation_history.append({
            "operation": VSAOperation.PERMUTE,
            "operands": [self._get_symbol_name(symbol)],
            "result_norm": np.linalg.norm(result)
        })
        
        return result
    
    def power(self, symbol: Union[str, VSASymbol, np.ndarray], n: int) -> np.ndarray:
        """
        Compute the n-th power of a symbol (n-fold self-binding)
        
        Args:
            symbol: Symbol to raise to power
            n: Power (number of self-bindings)
            
        Returns:
            Power vector
        """
        if n <= 0:
            return self.symbols["IDENTITY"].vector.copy()
        
        vec = self._resolve_to_vector(symbol)
        result = vec.copy()
        
        for i in range(n - 1):
            result_hrr = self.hrr_memory.bind(result, vec)
            result = result_hrr.data
        
        # Record operation
        self.operation_history.append({
            "operation": VSAOperation.POWER,
            "operands": [self._get_symbol_name(symbol)],
            "power": n,
            "result_norm": np.linalg.norm(result)
        })
        
        return result
    
    def similarity(self, symbol1: Union[str, VSASymbol, np.ndarray],
                  symbol2: Union[str, VSASymbol, np.ndarray]) -> float:
        """
        Compute cosine similarity between two symbols
        
        Args:
            symbol1: First symbol
            symbol2: Second symbol
            
        Returns:
            Similarity score [-1, 1]
        """
        vec1 = self._resolve_to_vector(symbol1)
        vec2 = self._resolve_to_vector(symbol2)
        
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return dot_product / (norm1 * norm2)
    
    def find_best_match(self, query_vector: np.ndarray, 
                       candidates: Optional[List[str]] = None,
                       threshold: float = 0.1) -> Tuple[Optional[str], float]:
        """
        Find the best matching symbol for a query vector
        
        Args:
            query_vector: Vector to match against
            candidates: List of candidate symbol names (all symbols if None)
            threshold: Minimum similarity threshold
            
        Returns:
            Tuple of (best_match_name, similarity_score)
        """
        if candidates is None:
            candidates = list(self.symbols.keys())
        
        best_match = None
        best_similarity = -1.0
        
        for candidate_name in candidates:
            if candidate_name not in self.symbols:
                continue
                
            similarity = self.similarity(query_vector, self.symbols[candidate_name].vector)
            
            if similarity > best_similarity and similarity > threshold:
                best_similarity = similarity
                best_match = candidate_name
        
        return best_match, best_similarity
    
    def create_expression(self, name: str, operation: VSAOperation,
                         operands: List[Union[str, VSASymbol, 'VSAExpression']]) -> VSAExpression:
        """
        Create a symbolic expression
        
        Args:
            name: Expression name
            operation: VSA operation
            operands: List of operands
            
        Returns:
            Created VSAExpression
        """
        expression = VSAExpression(
            operation=operation,
            operands=operands.copy()
        )
        
        # Generate expression string
        expression.expression_string = self._generate_expression_string(expression)
        
        self.expressions[name] = expression
        return expression
    
    def evaluate_expression(self, expression: Union[str, VSAExpression]) -> np.ndarray:
        """
        Evaluate a symbolic expression
        
        Args:
            expression: Expression to evaluate (name or VSAExpression)
            
        Returns:
            Result vector
        """
        if isinstance(expression, str):
            if expression not in self.expressions:
                raise ValueError(f"Expression {expression} not found")
            expr = self.expressions[expression]
        else:
            expr = expression
        
        # Recursively evaluate operands
        operand_vectors = []
        for operand in expr.operands:
            if isinstance(operand, str):
                # Symbol name
                operand_vectors.append(self._resolve_to_vector(operand))
            elif isinstance(operand, VSASymbol):
                # Direct symbol
                operand_vectors.append(operand.vector)
            elif isinstance(operand, VSAExpression):
                # Nested expression
                operand_vectors.append(self.evaluate_expression(operand))
            else:
                # Direct vector
                operand_vectors.append(operand)
        
        # Apply operation
        if expr.operation == VSAOperation.BIND:
            if len(operand_vectors) != 2:
                raise ValueError("BIND operation requires exactly 2 operands")
            result_hrr = self.hrr_memory.bind(operand_vectors[0], operand_vectors[1])
            result = result_hrr.data
            
        elif expr.operation == VSAOperation.UNBIND:
            if len(operand_vectors) != 2:
                raise ValueError("UNBIND operation requires exactly 2 operands")
            result_hrr = self.hrr_memory.unbind(operand_vectors[0], operand_vectors[1])
            result = result_hrr.data
            
        elif expr.operation == VSAOperation.SUPERPOSE:
            result = np.sum(operand_vectors, axis=0)
            if self.normalize_vectors:
                result = result / (np.linalg.norm(result) + 1e-8)
                
        elif expr.operation == VSAOperation.PERMUTE:
            if len(operand_vectors) != 1:
                raise ValueError("PERMUTE operation requires exactly 1 operand")
            result = self.permute(operand_vectors[0])
            
        else:
            raise ValueError(f"Unsupported operation: {expr.operation}")
        
        # Cache result
        expr.result_vector = result
        return result
    
    def analogy(self, a: Union[str, VSASymbol], b: Union[str, VSASymbol],
               c: Union[str, VSASymbol]) -> np.ndarray:
        """
        Perform analogical reasoning: a:b::c:?
        
        Computes the vector that completes the analogy using the relation binding approach
        
        Args:
            a: First term of source pair
            b: Second term of source pair  
            c: First term of target pair
            
        Returns:
            Vector representing the analogical completion (d such that a:b::c:d)
        """
        vec_a = self._resolve_to_vector(a)
        vec_b = self._resolve_to_vector(b)
        vec_c = self._resolve_to_vector(c)
        
        # Extract relation: R = b ⊕ a (unbind a from b)
        relation_hrr = self.hrr_memory.unbind(vec_b, vec_a)
        relation = relation_hrr.data
        
        # Apply relation to c: d = c ⊛ R (bind c with relation)
        result_hrr = self.hrr_memory.bind(vec_c, relation)
        result = result_hrr.data
        
        return result
    
    def cleanup(self, noisy_vector: np.ndarray, 
                candidates: Optional[List[str]] = None,
                cleanup_threshold: float = 0.3) -> Tuple[Optional[str], np.ndarray]:
        """
        Clean up a noisy vector by finding the best matching clean symbol
        
        Args:
            noisy_vector: Vector to clean up
            candidates: Candidate symbols for cleanup
            cleanup_threshold: Minimum similarity for successful cleanup
            
        Returns:
            Tuple of (cleaned_symbol_name, cleaned_vector)
        """
        best_match, similarity = self.find_best_match(
            noisy_vector, candidates, cleanup_threshold
        )
        
        if best_match is not None:
            cleaned_vector = self.symbols[best_match].vector
            return best_match, cleaned_vector
        else:
            # No good match found, return normalized input
            normalized = noisy_vector / (np.linalg.norm(noisy_vector) + 1e-8)
            return None, normalized
    
    def _resolve_to_vector(self, symbol: Union[str, VSASymbol, np.ndarray]) -> np.ndarray:
        """Convert symbol specification to vector"""
        if isinstance(symbol, str):
            if symbol not in self.symbols:
                raise ValueError(f"Symbol {symbol} not found in vocabulary")
            return self.symbols[symbol].vector
        elif isinstance(symbol, VSASymbol):
            return symbol.vector
        elif isinstance(symbol, np.ndarray):
            return symbol
        else:
            raise ValueError(f"Invalid symbol type: {type(symbol)}")
    
    def _get_symbol_name(self, symbol: Union[str, VSASymbol, np.ndarray]) -> str:
        """Get name for symbol (for logging)"""
        if isinstance(symbol, str):
            return symbol
        elif isinstance(symbol, VSASymbol):
            return symbol.name
        elif isinstance(symbol, np.ndarray):
            return f"vector[{len(symbol)}]"
        else:
            return "unknown"
    
    def _generate_expression_string(self, expression: VSAExpression) -> str:
        """Generate human-readable expression string"""
        op_symbols = {
            VSAOperation.BIND: "⊛",
            VSAOperation.UNBIND: "⊕", 
            VSAOperation.SUPERPOSE: "+",
            VSAOperation.PERMUTE: "π",
            VSAOperation.POWER: "^"
        }
        
        symbol = op_symbols.get(expression.operation, str(expression.operation))
        operand_names = [self._get_symbol_name(op) for op in expression.operands]
        
        if expression.operation in [VSAOperation.BIND, VSAOperation.UNBIND]:
            return f"({operand_names[0]} {symbol} {operand_names[1]})"
        elif expression.operation == VSAOperation.SUPERPOSE:
            return f"({' + '.join(operand_names)})"
        elif expression.operation == VSAOperation.PERMUTE:
            return f"π({operand_names[0]})"
        else:
            return f"{symbol}({', '.join(operand_names)})"
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get statistics about the VSA system"""
        symbol_types = {}
        for symbol in self.symbols.values():
            symbol_types[symbol.symbol_type] = symbol_types.get(symbol.symbol_type, 0) + 1
        
        return {
            "vector_dim": self.vector_dim,
            "n_symbols": len(self.symbols),
            "n_expressions": len(self.expressions),
            "symbol_types": symbol_types,
            "n_operations": len(self.operation_history),
            "normalize_vectors": self.normalize_vectors,
            "noise_level": self.noise_level
        }
    
    def clear_history(self):
        """Clear operation history"""
        self.operation_history.clear()
    
    def export_vocabulary(self) -> Dict[str, Dict[str, Any]]:
        """Export symbol vocabulary for serialization"""
        vocabulary = {}
        for name, symbol in self.symbols.items():
            vocabulary[name] = {
                "vector": symbol.vector.tolist(),
                "symbol_type": symbol.symbol_type,
                "metadata": symbol.metadata
            }
        return vocabulary
    
    def import_vocabulary(self, vocabulary: Dict[str, Dict[str, Any]]):
        """Import symbol vocabulary from serialized format"""
        for name, symbol_data in vocabulary.items():
            vector = np.array(symbol_data["vector"])
            self.add_symbol(
                name=name,
                vector=vector,
                symbol_type=symbol_data.get("symbol_type", "atomic"),
                metadata=symbol_data.get("metadata", {})
            )

# Utility functions for common VSA patterns
def create_semantic_pointer_architecture(vector_dim: int = 512) -> VectorSymbolicArchitecture:
    """
    Create a VSA configured for semantic pointer architectures
    
    Args:
        vector_dim: Vector dimensionality
        
    Returns:
        Configured VectorSymbolicArchitecture
    """
    vsa = VectorSymbolicArchitecture(
        vector_dim=vector_dim,
        normalize_vectors=True,
        noise_level=0.01
    )
    
    # Add common semantic roles
    semantic_roles = [
        "AGENT", "PATIENT", "INSTRUMENT", "LOCATION", "TIME",
        "MANNER", "CAUSE", "GOAL", "SOURCE", "THEME"
    ]
    
    for role in semantic_roles:
        vsa.create_random_symbol(role, "semantic_role")
    
    return vsa

def create_cognitive_architecture(vector_dim: int = 512) -> VectorSymbolicArchitecture:
    """
    Create a VSA configured for cognitive modeling
    
    Args:
        vector_dim: Vector dimensionality
        
    Returns:
        Configured VectorSymbolicArchitecture  
    """
    vsa = VectorSymbolicArchitecture(
        vector_dim=vector_dim,
        normalize_vectors=True,
        noise_level=0.05
    )
    
    # Add cognitive primitives
    cognitive_primitives = [
        "CONCEPT", "INSTANCE", "PROPERTY", "RELATION",
        "MEMORY", "GOAL", "ACTION", "STATE", "EVENT"
    ]
    
    for primitive in cognitive_primitives:
        vsa.create_random_symbol(primitive, "cognitive")
    
    return vsa