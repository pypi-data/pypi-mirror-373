# pyCFS-data

Data processing framework for openCFS (www.opencfs.org). This project contains Python libraries to easily create and
manipulate data stored in openCFS type HDF5 file format (`*.cfs`).

:::{note}
Documentation can be found in the [API Documentation](./generated/pyCFS.data.rst).
:::

```{toctree}
examples/data_tutorial/data_tutorial.md
```

A small tutorial can be found [here](./examples/data_tutorial/data_tutorial.md). 
Also [this presentation](./embedded/presentation_overview/presentation.pdf) gives a good overview of the capabilities of the `pyCFS.data` module:

<iframe src="./embedded/presentation_overview/export/index.html" width="100%" height="600px"></iframe>

### [CFS IO](./generated/pyCFS.data.io.rst)

- [Reader class](./generated/pyCFS.data.io.CFSReader.rst) containing top and low-level methods for reading,
- [Writer class](./generated/pyCFS.data.io.CFSWriter.rst) containing top and low-level methods for writing,
- Data structure definitions for
    - [mesh](./generated/pyCFS.data.io.CFSMeshData.rst), containing description of the computational grid,
    - [result data](./generated/pyCFS.data.io.CFSResultData.rst), containing description of the result data,
    - [data array](./generated/pyCFS.data.io.CFSArray.rst), an overloaded numpy.ndarray.

#### Example

```python
from pyCFS.data.io import CFSReader, CFSWriter

with CFSReader('file.cfs') as f:
  mesh = f.MeshData
  results = f.MultiStepData
with CFSWriter('file.cfs') as f:
  f.create_file(mesh=mesh, result=results)
```

### [Operators](./generated/pyCFS.data.operators.rst)

Utility functions for performing mesh and/or data manipulation

- [Transformation operators](./generated/pyCFS.data.operators.transformation.rst)
    - Fit geometry based on minimizing the squared source nodal distances to target nearest neighbor nodes.
- [Interpolators](./generated/pyCFS.data.operators.interpolators.rst): Node2Cell, Cell2Node, Nearest Neighbor (bidirectional), Projection-based linear interpolation

### [Extra functionality](./generated/pyCFS.data.extras.rst)

*Extras* provides Python libraries to easily manipulate data from various formats including

- [CGNS](./generated/pyCFS.data.extras.cgns_io.rst) (`*.cgns`).
- [EnSight Case Gold](./generated/pyCFS.data.extras.ensight_io.rst) (`*.case`). Requires additional dependencies, which can be installed via pip

```sh
pip install pycfs[vtk]
```

- [Exodus](./generated/pyCFS.data.extras.exodus_io.rst) (`*.e`). Usage tutorial can be found [here](./examples/data_tutorial/exodus_io_tutorial/exodus_io_tutorial.md).

- [Ansys result file](./generated/pyCFS.data.extras.ansys_io.rst) (`*.rst`). Requires additional dependencies, which can be installed via pip

```sh
pip install pycfs[ansys]
```

- [PSV measurement data export file](./generated/pyCFS.data.extras.psv_io.rst) (`*.unv`).
- [MATLAB data files of NiHu structures and simulation results](./generated/pyCFS.data.extras.nihu_io.rst) (`*.mat`).

#### EnSight Case Gold

- Utility functions for reading using *vtkEnSightGoldBinaryReader* and writing to *CFS HFD5*

#### Exodus

- Utility functions for reading using *netCDF4* and writing to *CFS HFD5*
- Tutorial for using the Exodus I/O functionality can be found [here](./examples/data_tutorial/exodus_io_tutorial/exodus_io_tutorial.md).

#### Ansys

- Utility functions for reading using *pyAnsys (ansys-dpf-core)* and writing to *CFS HFD5*
- Requires a licensed ANSYS DPF server installed on the system!
    - Check if the environment variable `ANSYSLMD_LICENSE_FILE` is set to the license server)!
    - Check if the environment variable `AWP_ROOTXXX` is set to the ANSYS installation root folder of the version you
      want to use (`vXXX` folder).

```sh
export ANSYSLMD_LICENSE_FILE=1055@my_license_server.ansys.com
export AWP_ROOTXXX=/usr/ansys_inc/vXXX
```

#### PSV - Measurement data

- Utility functions for reading `*.unv` export files using *pyUFF* and writing to *CFS HFD5*
- Utility functions for manipulating data dictionary:
    - Interpolate data points from neighboring data points
    - Combine 3 measurements to 3D measurement

#### NiHu

- Utility functions for reading `*.mat` MATLAB data files of NiHu structures and simulation results and writing to *CFS
  HFD5*