# Ngawari

Ngawari is a Python-based toolkit for simplifying operations in data analysis and processing, particularly focused on medical imaging and computational geometry. It is built heavily on top of the [VTK library](https://vtk.org/).

## Features

- Advanced geometric calculations and transformations
- Medical imaging data processing
- Statistical analysis tools
- 3D visualization capabilities

## Installation

To install Ngawari, run the following command:

```bash
pip install ngawari
```

## Usage

Here's a quick example of how to use Ngawari:

```python
from ngawari import ftk, fIO, vtkfilters
import numpy as np

# Create a simple sphere
sphere = vtkfilters.buildSphereSource([0, 0, 0], radius=1.0)

# Get points as numpy array
points = vtkfilters.getPtsAsNumpy(sphere)

# Add a scalar array
vtkfilters.setArrayFromNumpy(sphere, points[:, 0], "x_coords", SET_SCALAR=True)

# Apply a filter
smoothed = vtkfilters.smoothTris(sphere, iterations=10)

# Write to file
fIO.writeVTKFile(smoothed, "smoothed_sphere.vtp")

# Build image over sphere:
image = vtkfilters.buildRawImageDataFromPolyData(smoothed, res=[0.1,0.1,0.1])

# Add a scalar array to the image
vtkfilters.setArrayFromNumpy(image, np.random.rand(image.GetNumberOfPoints()), "random_scalar", SET_SCALAR=True)

# Null scalars outside sphere
image_nulled = vtkfilters.filterNullOutsideSurface(image, smoothed)

# Write to file
fIO.writeVTKFile(image_nulled, "image_over_sphere.vti")
```

For more detailed usage instructions, please refer to the documentation.

## Documentation 

Full documentation is available at [https://fraser29.github.io/ngawari/](https://fraser29.github.io/ngawari/)

## Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for more details.

## License

Ngawari is released under the MIT License. See the [LICENSE](LICENSE) file for more details.

## Contact

For any questions or support, please open an issue on our [GitHub repository](https://github.com/fraser29/ngawari) or contact us at support@ngawari.com.

## Dependencies

This project uses the following major dependencies:
- VTK (BSD 3-Clause License) - https://vtk.org/ 