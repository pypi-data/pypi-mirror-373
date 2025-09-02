---
theme: white
enableMenu: true
progress: true
# parallaxBackgroundImage:
# parallaxBackgroundSize: 2100px 900px
# parallaxBackgroundHorizontal: 0
# parallaxBackgroundVertical: 0
slideNumber: true
autoScale: true
title: "pyCFS: A companion library for openCFS (Data Manipulation)"
transition: slide
transitionSpeed: fast
overview: true
loop: false
enableChalkboard: false
cssvariables:
  --r-main-font-size: 2.3em
---

<!-- Left align bullet points -->
<style type="text/css">
  .reveal
  .slide p {    text-align: left;  }
  /* .reveal ul {    font-size: 0.85em; } */
  .reveal ul {    display: block; } 	
  /* .reveal ol {    display: block; } */
</style>

<img src="https://gitlab.com/openCFS/pycfs/-/raw/main/docs/source/_static/art/pyCFS_logo.png" width="40%"/>

<!-- [![openCFS logo](https://gitlab.com/openCFS/pycfs/-/raw/main/docs/source/_static/art/pyCFS_logo.png)](https://opencfs.gitlab.io/pycfs) {style="text-align: center"} -->

# `pyCFS`
## A companion library for [`openCFS`](https://opencfs.org)
#### Part 2: Data manipulation

--

## Focus

* Test case generation
  * Create `.cfs` files from scratch
* Pre-Processing 
  * Mesh preparation
  * Data processing
* Post-Processing 
  * Compare to analytic computations
  * Plot time series (faster than ParaView) 
* Small to medium size problems! 
  * Many parts are parallelized
  * Some Python operations are still slow for large problems

---

# Getting started

--

## Installation

* Install in `pip` environment

```pip
pip install pyCFS
```

<div class="fragment" data-markdown>
  #### Update from current main branch
  ```pip
  pip install git+https://gitlab.com/openCFS/pycfs@main --upgrade --force-reinstall
  ```
</div>

--

### Additional dependencies

* Large dependencies excluded from standard install
* Install dependencies for all functionality

```pip
pip install pyCFS[data]
```

--

## Documentation

* [Documentation](https://opencfs.gitlab.io/pycfs) page
  * Installation Guide
  * Basic usage Guide
    * Contains only some features
  * [API-Documenation](https://opencfs.gitlab.io/pycfs/api.html)

---

# Functionality

--

## Overview

Structured into submodules
```python
from pyCFS.data import io, operators, util, extras
```

* `io`
  * I/O operations for CFS type HDF5 format
* `operators` 
  * Basic mesh/data operations
* `util` 
  * Various useful functions when working with _pyCFS_
* `extras` 
  * I/O compatibilty methods to other file formats
  * Additional functionality not directly related to _openCFS_

--

## I/O `(CFSReader)`

```python
from pyCFS.data.io import CFSReader
``` 
- Reading CFS-type HDF5 files
  - Mesh
  - Data (on Nodes/Elements, History data)
  ```xml
  <surfRegionResult type="acouPower">
    <surfRegionList>
      <surfRegion name="S_body" outputIds="hdf5" writeAsHistResult="yes"/>
    </surfRegionList>
  </surfRegionResult>
  ```

--

## I/O `(CFSReader)`

Usage
```python {data-trim data-line-numbers="1-13|15-22"}
with CFSReader(filename="file.cfs") as reader:
    # Print file information
    print(reader)

    # Read the whole mesh
    mesh = reader.MeshData

    # Read coordinates, connectivity
    coordinates = reader.Coordinates
    connectivity = reader.Connectivity

    # Read node coordinates of a specific region
    reg_1 = reader.get_mesh_region_coordinates(region="S_CAPACITOR")

    # Read all result data for sequence step 2
    reader.set_multi_step(multi_step_id=2)
    results_2 = reader.MultiStepData

    # Read data for a specific quantity and region
    result_1 = reader.get_multi_step_data(multi_step_id=1, 
                                          quantities=["elecPotential"], 
                                          regions=["S_CAPACITOR"])
  
```

--

## I/O `(CFSWriter)`
```python
from pyCFS.data.io import CFSWriter
```
- Creating new CFS-type HDF5 files
- Writing to existing CFS-type HDF5 files

Usage

```python {data-trim}
with CFSWriter(filename="file.cfs") as writer:
  # Create new file
  writer.create_file(mesh=mesh, result=result_1)

  # Write additional squence step
  writer.write_multistep(result=results_2, multi_step_id=2)
```

--

## I/O `(CFSMeshData)`

```python
from pyCFS.data.io import CFSMeshData
```
* Container object for all mesh related data
* Various mesh operations

<img src="https://gitlab.com/openCFS/pycfs/-/raw/main/docs/source/resources/data_structures_CFSMeshData.png" width="100%"/>

--

## I/O `(CFSMeshData)`

Usage examples
```python {data-trim data-line-numbers="1-19|21-29"}
# Create mesh object of point cloud
mesh_points = CFSMeshData.from_coordinates_connectivity(
    coordinates=coordinates,
    region_name="P_measurement"
)

# Create mesh object from coordinates and connectivity
mesh = CFSMeshData.from_coordinates_connectivity(
    coordinates=coordinates, 
    connectivity=connectivity, 
    element_dimension=2,
    region_name="S_plate"
)

# Merge mesh objects
mesh = mesh + mesh_points

# Print information
print(mesh)

# Compute element normals for a region
mesh.get_region_centroids(region="S_plate")

# Get closest node/element to a coordinate
mesh.get_closest_node(coordinate=[0.1, 0.2, 0.3], region="S_plate")
mesh.get_closest_element(coordinate=[0.1, 0.2, 0.3], region="S_plate")

# Split mesh into regions by element clusters
mesh.split_regions_by_connectivity()
```

--

## I/O `(CFSRegData)`

```python
from pyCFS.data.io import CFSRegData
```
* Container object for all region related data

<img src="https://gitlab.com/openCFS/pycfs/-/raw/main/docs/source/resources/data_structures_CFSRegData.png" width="100%"/>

--

## I/O `(CFSResultArray)`

```python
from pyCFS.data.io import CFSResultArray
```

* Custom numpy array type \
(compatible with all operations numpy.ndarray is compatible!)
* Including all meta data for write operations

<img src="https://gitlab.com/openCFS/pycfs/-/raw/main/docs/source/resources/data_structures_CFSResultArray.png" width="100%"/>

--

## I/O `(CFSResultArray)`

Usage examples {data-trim}
```python
# Create a result array object
np_array = np.ones((5, 10, 3))
cfs_array = CFSResultArray(np_array)

# Set meta data for the result array
cfs_array.set_meta_data(
    quantity="elecPotential",
    region="S_CAPACITOR",
    step_values=np.array([0, 1, 2, 3]),
    # dim_names=["-"],
    res_type=cfs_result_type.NODE,
    # is_complex=False,
    # multi_step_id=1,
    analysis_type=cfs_analysis_type.TRANSIENT,
)
```

--

## I/O `(CFSResultContainer)`

```python
from pyCFS.data.io import CFSResultContainer
```

* Container object for data of a single multistep / sequence step

<img src="https://gitlab.com/openCFS/pycfs/-/raw/main/docs/source/resources/data_structures_CFSResultData.png" width="100%"/>

--

## I/O `(CFSResultContainer)`

Usage examples
```python {data-trim data-line-numbers="1-6|8-12|14-15"}
# Create a result container object
result = CFSResultContainer(analysis_type=cfs_analysis_type.TRANSIENT,
                            multi_step_id=2, data=[array_1, array_2])

# Print information
print(result)

# Extract certain time steps
result_1 = result[0:5]

# Extract certain region and quantity
result_2 = result.extract_quantity_region(quantity="elecPotential", region="S_CAPACITOR")

# Add data to result object (define different multi step ID)
result.add_data_array(data=cfs_array, multi_step_id=2)
```

--

## I/O (Other)

```python
from pyCFS.data.io import cfs_types, cfs_util
```
* `cfs_types`
  * Enum definitions based on *openCFS* source code
* `cfs_util` 
  * Functions to check object validity

--

## Operators

```python
from pyCFS.data.operators import (transformation, interpolators,
                                  _projection_interpolation, sngr)
```

* `interpolators` 
  * Basic interpolators
    - Node2Cell
    - Cell2Node
    - Nearest Neighbor (bidirectional)
* `projection_interpolation` 
  * Projection-based interpolation

--

## Operators

```python
from pyCFS.data.operators import (transformation, interpolators,
                                  _projection_interpolation, sngr)
```

* `transformation`
  * Translate / rotate / extrude / revolve mesh
  * Fit mesh onto target mesh
* `sngr` 
  * Compute fluctuating flow field from stationary RANS solution

--

## Extra functionality {.smaller}


* Read mesh and data from various formats
  * `ansys_io` (Ansys Mechanical: `.rst`) 
  * `ensight_io` (various CFD software: `.case`) 
  * `psv_io` (Polytec PSV export: `.unv`)
  * `nihu_io` (NiHu simulation export: `.mat`) 
  * _Planned:_ `exodus_io` (Cubit mesh export) 

---

# Example workflow 
# `I/O`

--

### Tasks

1. Read mesh and result data
2. View connectivity array and node coordinates of a specific region
3. Multiply result with factor
4. Add result to existing file as a new sequence step (multi step)

--

### Code

```python {data-trim data-line-numbers="1-9|11-13|15-16|18-20|22-26"}
# Import necessary modules
from pyCFS.data import io

# Read file
with io.CFSReader(filename="file.cfs") as f:
  # Read mesh data
  mesh = f.MeshData
  # Read results of sequence step 1
  results = f.get_multi_step_data(multi_step_id=1)

# View connectivity array, get coordinates of V_air
conn = print(mesh.Connectivity)
reg_coord = mesh.get_region_coordinates(region="V_air")

# Get data array of elecPotential in region V_air
elec_pot = results.get_data_array(quantity="elecPotential", region="V_air")

# Manipulate result
igte_factor = 1e0
elec_pot *= igte_factor

# Write "corrected" result to new sequence step
result_write = io.CFSResultContainer(data=[elec_pot], multi_step_id=2,
                                     analysis_type=elec_pot.AnalysisType)
with io.CFSWriter("file.cfs") as f:
  f.write_multistep(result=result_write)
```

--

### Debugging in PyCharm (1)

<!-- <img src="img/pycharm1.png" style="width: 100%; height: auto;" /> -->
![](img/pycharm1.png)

--

### Debugging in PyCharm (2)

![](img/pycharm2.png)

---

# Example workflow 
# `Operators`

--

### Tasks

1. Read mesh and result data
2. Perform Node-to-Cell interpolation
3. Add interpolated data to existing results
4. Write mesh and results to a new file

--

### Code

```python {data-trim data-line-numbers="1-9|11-17|19-23|25-28"}
# Import necessary modules
from pyCFS.data import io
from pyCFS.data.operators import interpolators

# Read source file
with io.CFSReader(filename="file.cfs") as h5r:
  print(h5r)
  mesh = h5r.MeshData
  results = h5r.MultiStepData

# Perform interpolation
results_interpolated = interpolators.interpolate_node_to_cell(
  mesh=mesh, 
  result=results, 
  regions=["V_air"],
  quantity_names={"elecPotential": "interpolated_elecPotential"},
)

# Add interpolated result to results container
results.combine_with(results_interpolated)

# Check results container
print(results)

# Write output file
with io.CFSWriter("file_out.cfs") as h5w:
  # Write mesh and results to new file
  h5w.create_file(mesh=mesh, result=results)
```

--

### Interactive mode in VS Code (1)

![](img/vsc1.png)

--

### Interactive mode in VS Code (2)

![](img/vsc2.png)

--

### Interactive mode in VS Code (3)

![](img/vsc3.png)