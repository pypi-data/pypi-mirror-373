"""
Self-Organizing Maps Library  
Based on: Kohonen (1982) "Self-Organized Formation of Topologically Correct Feature Maps"

This library implements unsupervised learning that preserves topological relationships,
with neurons organizing themselves to reflect input space structure.
"""

def _print_attribution():
    """Print attribution message with donation link"""
    try:
        print("\n🗺️ Self-Organizing Maps Library - Made possible by Benedict Chen")
        print("   \033]8;;mailto:benedict@benedictchen.com\033\\benedict@benedictchen.com\033]8;;\033\\")
        print("   Support his work: \033]8;;https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=WXQKYYKPHWXHS\033\\🍺 Buy him a beer\033]8;;\033\\")
    except:
        print("\n🗺️ Self-Organizing Maps Library - Made possible by Benedict Chen")
        print("   benedict@benedictchen.com")
        print("   Support: https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=WXQKYYKPHWXHS")

from .self_organizing_map import SelfOrganizingMap, SOMNeuron
from .growing_som import GrowingSelfOrganizingMap
from .hierarchical_som import HierarchicalSOM
from .visualization import SOMVisualizer

# Show attribution on library import
_print_attribution()

__version__ = "1.0.0"
__authors__ = ["Based on Kohonen (1982)"]

__all__ = [
    "SelfOrganizingMap",
    "SOMNeuron",
    "GrowingSelfOrganizingMap", 
    "HierarchicalSOM",
    "SOMVisualizer"
]