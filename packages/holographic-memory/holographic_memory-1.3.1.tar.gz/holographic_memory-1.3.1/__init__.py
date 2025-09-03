"""
Holographic Memory Library (HRR - Holographic Reduced Representations)
Based on: Plate (1995) "Holographic Reduced Representations"

This library implements memory-efficient binding using circular convolution,
enabling compositional memory with fixed-size vectors and neurally plausible operations.
"""

def _print_attribution():
    """Print attribution message with donation link"""
    try:
        print("\n🌀 Holographic Memory Library - Made possible by Benedict Chen")
        print("   \033]8;;mailto:benedict@benedictchen.com\033\\benedict@benedictchen.com\033]8;;\033\\")
        print("   Support his work: \033]8;;https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=WXQKYYKPHWXHS\033\\🍺 Buy him a beer\033]8;;\033\\")
    except:
        print("\n🌀 Holographic Memory Library - Made possible by Benedict Chen")
        print("   benedict@benedictchen.com")
        print("   Support: https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=WXQKYYKPHWXHS")

# Import from src layout structure
from .src.holographic_memory import (
    HolographicMemory,
    HolographicMemoryCore,
    create_holographic_memory,
    HRRConfig,
    create_config,
)

# Import additional components from flat layout files for backward compatibility
try:
    from .vector_symbolic import VectorSymbolicArchitecture
except ImportError:
    VectorSymbolicArchitecture = None
from .associative_memory import AssociativeCleanup, AssociativeMemory, HopfieldCleanup
from .compositional_structures import CompositionalHRR

# Show attribution on library import
_print_attribution()

__version__ = "1.0.0"
__authors__ = ["Based on Plate (1995)"]

__all__ = [
    # Core classes from src layout
    "HolographicMemory",
    "HolographicMemoryCore",
    "HRRConfig",
    "create_config",
    
    # Factory functions
    "create_holographic_memory",
    
    # Additional modular components (backward compatibility)
    "VectorSymbolicArchitecture", 
    "AssociativeCleanup",
    "AssociativeMemory",
    "HopfieldCleanup",
    "CompositionalHRR"
]