# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- ( new features )

### Changed

- ( changes in existing functionality )

### Deprecated

- ( soon-to-be removed features )

### Removed

- ( now removed features )

### Fixed

- ( any bug fixes )

### Security

- ( in case of vulnerabilities )

## [0.1.9] - 2025-09-01

### Added

- Dynamic Mode Decomposition (DMD)
- FieldFFT
- RBF Interpolator
- RBF Gradient Interpolator
- Generate structured mesh
- function 'get_external_filenames' to get external file names in case of hdf5 format with external files and a test
- function 'round_step_values' that rounds the values of all steps to specified digits and a test
- function 'add_steps_to_multistep' that allows adding additional steps to a multistep and a test
- nox based testing environment to run extended tests with different configurations
- ci job to run tests on windows 
- dependency checks in ci pipeline
- function 'rename_quantities' to rename result quantities in a given CFS hdf5 file, and a corresponding testcase.
- properties to manage shape of CFSMeshData.Types, CFSMeshData.Connectivity, and CFSMeshData.Coordinates
- utility to update pyCFS version
- application submodule
- module structure checks in ci pipeline
- pytest coverage configuration

### Changed

- Moved low level interpolation functions to separate hidden modules
- some functionalty changes to make things working when dealing with reader/writer using hdf with external files
- Vectorization and speedup for node/element extraction, improving performance significantly for large grids
- Changed shape of CFSMeshData.Types to (N,) with N being the number of elements in the mesh.

### Fixed

- Made path separators OS independent, also for tests
- Removed requirement for openGL on vtk package
- Skip ansys tests if ansys is not installed
- Prevent rename_quantities from creating empty datasets if they don't exist beforehand
- Disabled pip cache in ci pipeline to reduce disk space usage

## [0.1.8] - 2025-06-20

### Added

- SNGR Lighthill harmonic rhs source term
- Utility to convert *.encas files to *.case files

### Changed

- Vectorized SNGR computations
- Performance improvements for ensight reader
- Performance improvements for CGNS reader
- Various performance improvements for CFSReader, CFSWriter
- Renamed pyCFS.data.io submodeles to hide them

### Fixed

- Element centroid computation for non-ordered element ids
- Node to cell interpolation for multiple regions

## [0.1.7] - 2025-06-12

### Added

- Modal analysis operators (MAC, MACX, MSF, MCF)
- STL mesh reader
- Additional sanity checks for result container objects
- Automatic determination of complex-valued result arrays based on the specified analysis type
- Simple function to read file information from CFS files

### Changed

- Moved type conversion functions for extras module to type definition files

## [0.1.6] - 2025-05-19

### Added

- Region splitting define regions optionally by string
- Simple utility functions to read and write CFS files with single line commands

### Changed

- Changed CFSResultArray.DimNames to be a property automatically generating list if no data is defined
- Reimplemented `add_data` and `add_data_array` methods in `CFSResultContainer`

### Removed

- cfs_util library (moved functions to corresponding class definitions)

### Fixed

- CFSResultArray.require_shape support for all dimensions

## [0.1.5] - 2025-04-22

### Added

- Get region element quality
- Element quality support for linear hexahedral elements
- Exodus reader
- CGNS Mesh reader

### Removed

- CFSMeshData.Quality property
- CFSMeshData.ElementCentroids property

## [0.1.4] - 2025-03-02

### Added

- Added method to extract regions from a mesh object
- Added method to detect and correct CFSResultArray shape from meta data
- Input of list of CFSResultArrays to various CFSWriter methods
- Input of list of CFSResultArrays to interpolator functions
- interpolate_node_to_cell, interpolate_cell_to_node for all regions / quantities
- Utility function to refactor changes introduced in this version

### Changed

- renamed `CFSResultData` to `CFSResultContainer`
- moved `CFSRegData` to separate file
- renamed module files of pyCFS.data.io to distinguish from class names
- renamed attribute `result_data` to `result` in various CFSWriter methods to make clear they take 
a container or a list of CFSResultArrays
- renamed attribute `mesh_data` to `mesh` in CFSWriter methods
- Use metadata of first data array when initializing CFSResultContainer
- renamed attribute `mesh_data` to `mesh` in interpolate_node_to_cell, interpolate_cell_to_node, interpolate_distinct_nodes functions
- renamed attribute `result_data` to `result` in interpolate_node_to_cell, interpolate_cell_to_node, interpolate_distinct_nodes functions
- renamed attribute `data_src` to `result_src` in interpolate_nearest_neighbor function

### Removed

- `extract_quantity_region` no longer takes `data_ids` argument. Use array indexing instead.

### Fixed

- Fixed bug computing element centroids when region element ids are not ordered ascending.

## [0.1.3] - 2025-02-25

### Added 
- Topology optimization mode (accepting additional input specifying the setup and generating additional input file need by CFS)
- Windows support (tested manually - still needs actual tests in pipeline)

### Changed
- Paths to mesher and opencfs need to be specified fully now including the name of the binary or .exe file

## [0.1.2] - 2025-02-03

## Added

- `pyCFS` sensor arrays : replaces the standard `CFS` sensor arrays
  - Documentation regarding this new feature
- Extracting system matrices by setting flag when executing simulation
- a function 'get_result_arrays' that allows to get multiple result arrays at once
- a function 'interpolate_distinct_nodes' that allows to interpolate specific nodes by their nearest neighbors
- a test for 'interpolate_distinct_nodes'
- a sanity check in 'perform_interpolation'
- a test to check normal vector computation on centroids when specific elements are specified

### Changed

- Result handling : 
  - removed the `hdf5_io` module 
  - switched to internal `data.CFSReader` for handling the result data

### Removed

- `CFS` sensor arrays : not supported anymore (see `pyCFS` sensor arrays)

### Fixed

- Transient and harmonic simulation result handling
- Writer issue that prevented writing files when they are open in Paraview
- Indexation of normal vector computation on centroids when specific elements are specified

## [0.1.1] - 2025-01-16

## Added

- Check unv file for available PSV data
- Functionality to transform the mesh coordinates and corresponding testcase
- Functionality to separate mesh regions that consist of multiple non-separated regions into their connected subregions.
- CFSReader.ResultMeshData property replacing CFSReader.MultiStepData property

### Changed

- CFSReader.MultiStepData and CFSReader.read_multi_step_data now return both mesh result and history result data
- CFSReader.ResultQuantities property now returns both mesh result and history result quantities

### Fixed

- Inconsistent mesh type array definition
- SNGR test on windows
- psv_io.read_unv to read real data from unv file
- psv.io.read_unv correctly read 3D data
- Tests on Windows
- Automatic detection of ansys installation path for tests
- Fixed result type strings for history data
- Reading of history data defined on Nodes or Elements
- Handling of Files with only History or Mesh Result data

## [0.1.0] - 2024-11-27

## Added

- Drop nodes and elements from `CFSMeshData` object
- Extract nodes and elements from `CFSMeshData` object
- Selective reading of MultiStep data with `data.io.CFSReader`
- Read History data with `data.io.CFSReader`
- Write History data with `data.io.CFSWriter`
- Sanity check for `CFSResultArray` object

### Changed

- renamed `pyCFS.data.extras.psv_io.combine_frf_3D` to `pyCFS.data.extras.psv_io.combine_3D`
- renamed `pyCFS.data.io.MeshData._get_mesh_quality` to `pyCFS.data.io.MeshData.get_mesh_quality`

## [0.0.9] - 2024-11-13

### Added

- SNGR (Stochastic noise generation and radiation) operator
- Drop nodes from PSV data object

### Changed

- renamed `pyCFS.data.extras.psv_io.read_frf` to `pyCFS.data.extras.psv_io.read_unv`, 
changed input parameters to allow flexible input strings
  
## [0.0.8] - 2024-11-8

### Fixed

- Removed linux dependent commands to python functions such that data management works independent of the underlying system

## [0.0.7] - 2024-08-21

### Added

- Extruding mesh to transformation operators
- Revolving mesh to transformation operators
- Read and Interpolate point result from Ansys RST file
- Nearest neighbor, cell to node, and node to cell interpolation utility functions
- Read PSV export data from 3D scan
- pyCFS.data.io object check before writing

### Changed

- moved function `pyCFS.data.io.mesh_from_coordinates_connectivity`
to classmethod `pyCFS.data.io.CFSMeshData.from_coordinates_connectivity`

### Fixed

- Fixed ansys_io working with multiple Ansys Versions installed (currently working with Ansys 2022R2)
- Fixed reading of complex-valued history results
- Fixed Cell to Node / Node to Cell interpolation inconsistencies
- Fixed `AttributeError: pyCFS object has no attribute N` when invoking the `mesh_only` mode

## [0.0.6] - 2024-05-08

### Added

- Compute surface normal vectors
- Option for parallel reading of result data (default now)

### Changed

- Vectorized element centroid computation
- Renamed "pyCFS.data.operators.fit_geometry" submodule to "pyCFS.data.operators.transformation"
- Renamed "pyCFS.data.operators.projection_interpolation.interpolation_fe" submodule to
  "pyCFS.data.operators.projection_interpolation.interpolation_matrix_projection_based"

## [0.0.5] - 2024-04-08

### Added

- Support for Reading/Writing MultiStepIDs other than 1.
- Support for Reading MultiStep with unsorted StepValues (requires sort before writing)

### Changed

- CFSResultData to contain data of a single MultiStep only.
- Improved testing using numpy.testing
- Improved import for better usability of data submodule
- Renamed nearest neighbor interpolator based on search direction

## [0.0.4] - 2024-03-25

### Added

- Possibility to read Meshes with groups/regions that have only Nodes defined. (As occuring when defining a nodeList)
  in an openCFS simulation.
- Method to find closest node/element for CFSMeshData objects
- Warning when element quality and centroids are not computed automatically due to size.

### Changed

- Website URL to openCFS Homepage.
- Testing of CFSReader to check read mesh and data values

### Fixed

- Critical bug when reading MultiStepData

## [0.0.3] - 2024-03-20

### Added

- Possibility to just run the meshing for the given parameters.
- Additional meshing setup control with `remeshing_on` and `mesh_present`
- `track_results` property to choose which results from the hdf file to track.
- Getter functions for hdf and sensor array results.

### Changed

- Running simulations in parallel does not do an initial mesh generation if `remeshing_on = False`.

### Removed

- `init_params` that needed to be passed to the `pyCFS` constructor, it is no longer used.

### Fixed

- Data module import.

## [0.0.2] - 2024-03-18

### Added

- `pyCFS.data` package
    - code, tests and doc
- Sensor array result support
    - Because CFS currently does not write SA results into the `hdf` file

### Changed

- Extended dependencies to accommodate `pyCFS.data` package

## [0.0.1] - 2024-03-12

### Added

- Old `pycfs` package code (refactored)
- CI pipeline for automated testing
- GitLab pages for documentation

### Fixed

- Parallelization when meshing
- Type hints

### Removed

- History results are no longer supported
    - These are now to be written into the `hdf` file
- Sensor array results are the only exception
    - When CFS can directly write these to the `hdf` file this package will change accordingly
    - Users should not see much difference in behavior