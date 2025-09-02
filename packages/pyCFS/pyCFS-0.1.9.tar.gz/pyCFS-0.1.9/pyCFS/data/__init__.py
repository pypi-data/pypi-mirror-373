"""
pyCFS.data
==========

Data processing framework for openCFS (www.opencfs.org). This project
contains Python libraries to easily create and manipulate data stored in
openCFS type HDF5 file format (``*.cfs``).

CFS IO
------------------------------------------

-  Reader class containing
   top and low-level methods for reading
-  Writer class containing
   top and low-level methods for writing

Example
~~~~~~~

.. code:: python

   from pyCFS.data.io import CFSReader, CFSWriter

   with CFSReader('file.cfs') as f:
       mesh = f.MeshData
       results = f.MultiStepData
   with CFSWriter('file.cfs') as f:
       f.create_file(mesh=mesh, result=results)

Operators
----------------------------------------------------

Utility functions for performing mesh and/or data manipulation

-  Fit geometry based on minimizing the squared source nodal distances
   to target nearest neighbor nodes.
-  Interpolators:
   Node2Cell, Cell2Node, Nearest Neighbor (bidirectional)
-  Projection based linear Interpolation

Extra functionality
-----------------------------------------------------------

*Extras* provides Python libraries to easily manipulate data from
various formats including

-  EnSight Case Gold (``*.case``).
-  Ansys result file (``*.rst``). Requires additional dependencies,
   which can be installed via pip

.. code:: sh

   pip install pycfs[data]

-  PSV measurement data export file (``*.unv``).
-  MATLAB data files of NiHu structures and simulation results
   (``*.mat``).

EnSight Case Gold
~~~~~~~~~~~~~~~~~

-  Utility functions for reading using *vtkEnSightGoldBinaryReader* and
   writing to *CFS HFD5*

Ansys
~~~~~

-  Utility functions for reading using *pyAnsys (ansys-dpf-core)* and
   writing to *CFS HFD5*
-  Requires a licensed ANSYS DPF server installed on the system!

   -  Check if the environment variable ``ANSYSLMD_LICENSE_FILE`` is set
      to the license server)!
   -  Check if the environment variable ``AWP_ROOTXXX`` is set to the
      ANSYS installation root folder of the version you want to use
      (``vXXX`` folder).

.. code:: sh

   export ANSYSLMD_LICENSE_FILE=1055@my_license_server.ansys.com
   export AWP_ROOTXXX=/usr/ansys_inc/vXXX

PSV - Measurement data
~~~~~~~~~~~~~~~~~~~~~~

-  Utility functions for reading ``*.unv`` export files using *pyUFF*
   and writing to *CFS HFD5*
-  Utility functions for manipulating data dictionary:

   -  Interpolate data points from neighboring data points
   -  Combine 3 measurements to 3D measurement

NiHu
~~~~

-  Utility functions for reading ``*.mat`` MATLAB data files of NiHu
   structures and simulation results and writing to *CFS HFD5*


"""

from ._v_def import v_def  # noqa

from . import io  # noqa
from . import util  # noqa
from . import extras  # noqa
from . import operators  # noqa

__all__ = ["io", "util", "extras", "operators", "v_def"]
