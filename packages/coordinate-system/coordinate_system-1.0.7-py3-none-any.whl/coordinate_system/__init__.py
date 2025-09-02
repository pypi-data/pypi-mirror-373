# coordinate_system/__init__.py

from .coordinate_system import vec3
from .coordinate_system import quat
from .coordinate_system import coord3

__all__ = ['vec3', 'quat', 'coord3', 'lerp']

def lerp(a: vec3, b: vec3, t: float) -> vec3:
    """
    Linear interpolation function that returns the interpolated point between two points

    Args:
        a: Starting point
        b: End point
        t: Interpolation ratio (0-1)
        
    Returns:
        The interpolated point
    """
    return a + (b - a) * t