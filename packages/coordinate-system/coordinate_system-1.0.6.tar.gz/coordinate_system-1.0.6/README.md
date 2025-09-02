### `__init__.py`

```python
from coordinate_system import vec3, quat, coord3
```

# Coordinate System Package

"""
This package provides a mathematical framework for defining and manipulating three-dimensional coordinate systems in Python.
It includes the `vec3`, `quat`, and `coord3` classes, allowing users to work with vectors, rotations, and coordinate transformations efficiently.

## Installation

You can install the package using pip:

```bash
pip install coordinate-system
```

## Overview

The `coordinate_system` package is based on group theory and defines a coordinate system in three-dimensional space. 
It includes an origin, three directional axes, and scaling components that correspond to transformations like translation, rotation, and scaling. 
This package provides methods to construct coordinate systems from various parameters and perform operations to convert between different coordinate systems.

### System Compatibility

**Note:** This package currently only supports Windows operating systems.

### Coordinate System Type

This package utilizes a left-handed coordinate system for all vector and quaternion operations.

## Classes

### `vec3`

Represents a three-dimensional vector.

- **Constructors:**
  - `vec3()` - Initializes a zero vector.
  - `vec3(float x, float y, float z)` - Initializes with specified components.

- **Properties:**
  - `x`: Component along the x-axis.
  - `y`: Component along the y-axis.
  - `z`: Component along the z-axis.

- **Methods:**
  - `__repr__()`: Returns a string representation of the vector.
  - `__add__(vec3 other)`: Computes the sum of two vectors.
  - `__sub__(vec3 other)`: Computes the difference between two vectors.
  - `__mul__(float scalar)`: Multiplies the vector by a scalar (both left and right).
  - `__truediv__(float scalar)`: Divides the vector by a scalar.
  - `dot(vec3 other)`: Computes the dot product with another vector.
  - `cross(vec3 other)`: Computes the cross product with another vector.
  - `length()`: Returns the length (magnitude) of the vector.
  - `normalize()`: Normalizes the vector to unit length.
  - `isINF()`: Checks if any component is infinite.
  - `flipX()`, `flipY()`, `flipZ()`: Flips the respective component.
  - `serialise()`: Serializes the vector to a string.
  - `len()`, `lenxy()`, `sqrlen()`, `abslen()`: Various length-related calculations.
  - `norm()`, `normcopy()`, `normalized()`: Normalization methods.
  - Static methods like `min3(vec3 a, vec3 b, vec3 c)`, `max3(vec3 a, vec3 b, vec3 c)`, `rnd()`, `lerp(vec3 a, vec3 b, float t)`, and `angle(vec3 a, vec3 b)` for various vector operations.

### `quat`

Represents a quaternion for 3D rotations.

- **Constructors:**
  - `quat()` - Initializes to the identity quaternion.
  - `quat(float w, float x, float y, float z)` - Initializes with specified components.
  - `quat(float angle, const vec3& axis)` - Creates a quaternion from an angle and an axis.
  - `quat(const vec3& v1, const vec3& v2)` - Creates a quaternion from two vectors.

- **Properties:**
  - `w`: Scalar component of the quaternion.
  - `x`, `y`, `z`: Vector components of the quaternion.

- **Methods:**
  - `__repr__()`: Returns a string representation of the quaternion.
  - `__add__(quat other)`: Computes the sum of two quaternions.
  - `__mul__(quat other)`: Multiplies two quaternions.
  - `__mul__(vec3 vector)`: Rotates a vector using the quaternion.
  - `__truediv__(quat other)`: Divides one quaternion by another.
  - `normalize()`: Normalizes the quaternion.
  - `normalized()`: Returns a normalized copy of the quaternion.
  - `conj()`: Returns the conjugate of the quaternion.
  - `length()`: Returns the length of the quaternion.
  - `dot(quat other)`: Computes the dot product with another quaternion.
  - `angle_to(quat other)`: Computes the angle to another quaternion.
  - Methods for conversion and construction from Euler angles and vectors: `from_eulers(float pitch, float yaw, float roll)` and `fromvectors(vec3 v1, vec3 v2)`.
  - `exp()`: Computes the exponential of the quaternion.
  - `log()`: Computes the logarithm of the quaternion.
  - `spherical_cubic_interpolate()`: Performs spherical cubic interpolation.

### `coord3`

Represents a 3D coordinate system.

- **Constructors:**
  - `coord3()` - Default constructor.
  - `coord3(real x, real y, real z)` - Initializes with specified coordinates.
  - `coord3(real x, real y, real z, real pitch, real yaw, real roll)` - Initializes with position and rotation.
  - `coord3(real x, real y, real z, real qw, real qx, real qy, real qz)` - Initializes with position and quaternion.
  - `coord3(const vec3& position)` - Initializes from a position vector.
  - `coord3(const vec3& ux, const vec3& uy, const vec3& uz)` - Initializes from three axis vectors.
  - `coord3(real angle, const vec3& axis)` - Initializes from an angle and axis.
  - `coord3(const quaternion& q)` - Initializes from a quaternion.
  - `coord3(const vec3& position, const quaternion& q, const vec3& scale)` - Initializes from position, quaternion, and scale.

- **Properties:**
  - `o`: Origin vector.
  - `ux`, `uy`, `uz`: Directional axes.
  - `s`: Scale vector.

- **Methods:**
  - `__add__(coord3 other)`: Computes the sum of two coordinate systems.
  - `__sub__(coord3 other)`: Computes the difference between two coordinate systems.
  - `__mul__(coord3 other)`: Multiplies two coordinate systems or transforms a vector using the coordinate system.
  - `__truediv__(coord3 other)`: Divides one coordinate system by another.
  - `__eq__(coord3 other)`: Checks for equality between two coordinate systems.
  - `pos()`: Returns the position vector.
  - `tovec()`: Converts the coordinate system to a vector.
  - `rot(real angle, const vec3& axis)`: Rotates the coordinate system by an angle around an axis.
  - `rot(const quaternion& q)`: Rotates the coordinate system by a quaternion.
  - `equal_dirs(coord3 other)`: Checks if the directional axes are equal.
  - `hash()`: Returns a hash of the coordinate system.
  - `serialise()`: Serializes the coordinate system.
  - `dump()`: Dumps information about the coordinate system.
  - `cross(coord3 other)`: Computes the cross product with another coordinate system or vector.

## Usage

### Creating a Coordinate System

You can create a coordinate system using various constructors:

```python
from coordinate_system import coord3, vec3

# Create a coordinate system from three axes
C = coord3.from_axes(vec3(1, 0, 0), vec3(0, 1, 0), vec3(0, 0, 1))

# Create a coordinate system from an angle and axis
C_angle = coord3.from_angle(90, vec3(0, 0, 1))

# Create a coordinate system from a quaternion
C_quat = coord3(quaternion(1, 0, 0, 0))

# Create a coordinate system from a position, quaternion, and scale
C_full = coord3(vec3(1, 2, 3), quaternion(1, 0, 0, 0), vec3(1, 1, 1))
```

### Transforming Vectors

You can transform vectors between different coordinate systems:

```python
V1 = vec3(1, 2, 3)
C1 = coord3(1,2,3)  # Some coordinate system
C0 = coord3(1,2,3,90,45,0)  # Another coordinate system

# Transforming from local to parent coordinate system
V0 = V1 * C1

# Projecting from parent to local coordinate system
V1 = V0 / C1
```

### Common Scenarios

#### Converting Between Coordinate Systems

```python
# Convert a vector from world to local coordinates
VL = Vw / C  # World to Local
Vw = VL * C  # Local to World
```

#### Using in Multi-Node Hierarchies

```python
V1 = V4 * C4 * C3 * C2  # Transforming through multiple coordinate systems
V4 = V1 / C2 / C3 / C4  # Reversing the transformation
```

## Advanced Usage

### Interpolating Between Coordinate Systems

You can use the various interpolation methods provided in the package, such as linear and spherical linear interpolation, to smoothly transition between different coordinate systems or vectors.

```python
from coordinate_system import lerp, slerp

# Linear interpolation between two coordinate systems
C_interpolated = lerp(C1, C2, 0.5)

# Spherical linear interpolation between two quaternions
q_interpolated = slerp(q1, q2, 0.5)
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
```