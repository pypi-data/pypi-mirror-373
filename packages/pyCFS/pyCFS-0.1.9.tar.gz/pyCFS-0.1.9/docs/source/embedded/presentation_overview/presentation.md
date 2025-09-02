---
theme: white
enableMenu: true
progress: true
# parallaxBackgroundImage: https://gitlab.com/openCFS/pycfs/-/raw/main/docs/source/_static/art/pyCFS_logo.svg
# parallaxBackgroundSize: 300px 100px
# parallaxBackgroundHorizontal: 0
# parallaxBackgroundVertical: 0
slideNumber: true
autoScale: true
title: "pyCFS: A companion library for openCFS"
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
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css">


<img src="https://gitlab.com/openCFS/pycfs/-/raw/main/docs/source/_static/art/pyCFS_logo.svg" width="40%" style="margin-bottom:-1em;"/>

<small style="line-height:1.1;">_v0.1.8_</small>

## A companion library for [`openCFS`](https://opencfs.org)


Andreas Wurzinger, Eniz Mušeljić

--

# What is `pyCFS`

`pyCFS` is a companion project to `openCFS` written in Python, accumulating useful tools for incorporating `openCFS` in Python-based workflows.

- Run simulations from python script / notebook for 
  - parameter optimization, 
  - sensitivity analysis, 
  - convergence studies, etc.
- Pre- and postprocessing of simulation data
  - Manipulate mesh and data
- Interface to other software packages


--

## Why use `pyCFS`

* Easy install via [PyPI](https://pypi.org/project/pyCFS/)
* Easy modification / addition of new features
* Flexibility, interface to other Python packages
  * Make use of `numpy`, `scipy`, `pytorch`, etc.
* Comprehensive [documentation](https://opencfs.gitlab.io/pycfs/index.html)!

---

# Getting started

--

## Installation

* Install latest version in `pip` environment

```pip
python -m pip install pyCFS
```

----

<div class="fragment" data-markdown>
> Update from current main branch
```pip
pip install git+https://gitlab.com/openCFS/pycfs@main --upgrade --force-reinstall
```
</div>

--

### Additional dependencies

* Large dependencies are excluded from the standard install
* Install dependencies for individual modules

```pip
pip install pyCFS[ansys]
pip install pyCFS[vtk]
```

* Install all dependencies (not recommended)

```pip
pip install pyCFS[all]
```

--

## Documentation

* [Documentation](https://opencfs.gitlab.io/pycfs) page
  * Installation Guide
  * Basic usage Guide
    * Covers only selected features
  * [API-Documentation](https://opencfs.gitlab.io/pycfs/api.html)\
    <img src="img/API_doc.png" style="height: 40%;" />

---

# Overview

![](img/pycfs_structure.drawio.svg)

---

# `pyCFS`

```python
import pyCFS
```

- Data management for automated simulation setup and execution
- `openCFS` simulation abstracted as function evaluation

--

Initialize project

```bash
pycfs newsim -n capacitor2d
```

Root directory structure

```bash
capacitor2d
  |-- sim_setup.py
  |-- run_sim.py
  |-- templates
    |-- capacitor2d_init.xml
    |-- mat_init.xml
    |-- capacitor2d_init.jou
```
![](img/pycfs_structure-Page-2.drawio.svg)


--

Define variable names

```python
cfs_params = ["V_TOP", "V_BOTTOM"]
mat_params = ["MAT_AIR", "MAT_DIELEC"]
geo_params = ["R_DOMAIN", "P_DIST"]
```

Set variables in tempate files

```xml
<bcsAndLoads>                    
    <potential name="S_top" value="V_TOP"/>
    <potential name="S_bottom" value="V_BOTTOM"/>
</bcsAndLoads>
```

![](img/domain.svg)

--

Construct pyCFS object

```python {data-trim data-line-numbers="1-10|12-19|21-31"}
import pyCFS

# Set project name and cfs path :
project_name = "capacitor2d"
cfs_path = "/home/Devel/CFS/bin/cfs"

# Define variable names
cfs_params = ["V_TOP", "V_BOTTOM"]
mat_params = ["MAT_AIR", "MAT_DIELEC"]
geo_params = ["R_DOMAIN", "P_DIST"]

# Consctruct pyCFS object :
cap_sim = pyCFS(
  project_name,
  cfs_path,
  cfs_params_names=cfs_params,
  mat_params_names=mat_params,
  trelis_params_names=geo_params,
)

# Generate parameter vector : 
p = np.array([[10.0, 0.0, 1.0, 
               1000, 3.0, 0.5]])

# Run the simulation : 
cap_sim(p)

# Obtain results : 
es = cap_sim.get_all_results_for(
    "elecFieldIntensity"
    )
```

--

## Additional features

- Result handling
  - Track certain results
  - Create senor arrays (`openCFS` sensor arrays are currently not supported!)
- Parallelization (run concurrent `openCFS` simulations)

---

# `pyCFS.data`

```python
from pyCFS.data import io, operators, util, extras
```


* Pre-Processing
  * Create `.cfs` files from scratch
  * Mesh and data preparation
* Post-Processing
  * Post-processing routines, e.g. FFT, MAC, MSE, etc. 
  * Plot time series (significantly faster than ParaView) 
* Interface to external packages
  * numpy, scipy, pyTorch, etc.

_Intended for small to medium size problems. Partly vectorized and parallelized, but not always RAM efficient._{class="fragment"}

--

Structured into submodules
```python
from pyCFS.data import io, operators, util, extras
```

* `io`
  * I/O operations for _CFS type HDF5_ format
* `operators`
  * Basic mesh/data operations
* `util`
  * Various useful functions when working with `pyCFS`
* `extras`
  * I/O compatibilty methods to other file formats
  * Additional functionality not directly related to `openCFS`

---

## I/O

```python
from pyCFS.data import io
```

* Top level functions
  
```python
file = "file.cfs"

# Print information about the file content
print(io.file_info(file))

# Read the file
mesh, data = io.read_file(file)
mesh = io.read_mesh(file)
data = io.read_data(file, quantities=['acouPressure'])

# Creat a new file
io.write_file(file, mesh=mesh, result=data)
```
* Reader and writer classes
* Data structures for mesh, and data

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
    writer.create_file(mesh_data=mesh, result_data=result_1)

    # Write additional squence step
    writer.write_multistep(result_data=results_2, multi_step_id=2)
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

## I/O `(CFSResultData)`

```python
from pyCFS.data.io import CFSResultData
```

* Container object for data of a single multistep / sequence step

<img src="https://gitlab.com/openCFS/pycfs/-/raw/main/docs/source/resources/data_structures_CFSResultData.png" width="100%"/>

--

## I/O `(CFSResultData)`

Usage examples
```python {data-trim data-line-numbers="1-6|8-12|14-15"}
# Create a result container object
result = CFSResultData(analysis_type=cfs_analysis_type.TRANSIENT, 
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
from pyCFS.data.io import cfs_types
```
* `cfs_types`
  * Enum definitions based on `openCFS` source code

---

## Operators

```python
from pyCFS.data.operators import (interpolators, _projection_interpolation,
                                  modal_analysis, sngr, transformation)
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
from pyCFS.data.operators import (interpolators, _projection_interpolation,
                                  modal_analysis, sngr, transformation)
```


* `modal_analysis`
  * Dynamic mode decomposition
  * Field FFT
  * Various metrics used in experimental modal analysis
* `sngr`
  * Compute fluctuating flow field from stationary RANS solution
* `transformation`
  * Translate / rotate / extrude / revolve mesh
  * Fit mesh onto target mesh

---

## Extra functionality {.smaller}


* Read mesh and data from various formats
  * `ansys_io` _(Ansys Mechanical: `.rst`)_ $\rightarrow$ `pyCFS[ansys]`
  * `cgns_io` _(various CFD/FEM software: `.cgns`)_
  * `ensight_io` _(various CFD software: `.case`)_ $\rightarrow$ `pyCFS[vtk]`
  * `exodus_io` _(Cubit mesh export: `.e`)_
  * `nihu_io` _(NiHu simulation export: `.mat`)_
  * `psv_io` _(Polytec PSV export: `.unv`)_
  * `stl_io` _(Surface mesh: `.stl`)_

---

# Example workflows {.smaller}

--

## `I/O`

Tasks

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
result_write = io.CFSResultData(data=[elec_pot], multi_step_id=2, 
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

--

## `Operators`

Tasks

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
print(io.file_info("file.cfs"))
mesh = io.read_mesh("file.cfs")
results = io.read_data("file.cfs")

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
io.write_file("file_out.cfs", mesh=mesh, result=results)
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