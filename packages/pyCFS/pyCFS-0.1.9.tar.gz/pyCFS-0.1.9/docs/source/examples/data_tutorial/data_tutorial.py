"""
Tutorial for using the main features of the pyCFS-data project.

- Read file
- Apply time blending
- Add additional result steps
- Drop unused regions
- Write file
"""

# %% Import CFS reader and writer classes
from pyCFS.data.io import CFSReader, CFSWriter

# %% Read mesh and result data of demo file
file_read = "tutorial_input.cfs"

with CFSReader(filename=file_read) as f:
    mesh = f.MeshData
    result_read = f.MultiStepData

# %% Print information about mesh and result
print(mesh)
print(result_read)

# %% Extract result
data_read = result_read.get_data_array(quantity="quantity", region="Vol")
# (optional) copy object to not edit the read structure
data_blended = data_read.copy()

# %% Apply simple time blending: Multiply with step value
for i in range(data_read.shape[0]):
    data_blended[i, :, :] *= data_blended.StepValues[i]

# %% Extend result
import numpy as np
from pyCFS.data.io import CFSResultArray

# Extend step values array
step_values = np.append(data_blended.StepValues, data_blended.StepValues + 1.0)
# Extend data array
data_new = np.tile(np.ones(data_blended.shape[1:], dtype=complex), (5, 1, 1))
data_write = np.concatenate([data_blended, data_new], axis=0)
# Convert to CFSResultArray and reset MetaData
data_write = CFSResultArray(data_write)
data_write.MetaData = data_blended.MetaData
data_write.StepValues = step_values

# %% Create new result structure
from pyCFS.data.io import CFSResultContainer, cfs_types

result_write = CFSResultContainer(data=[data_write], analysis_type=cfs_types.cfs_analysis_type.HARMONIC)

# %% Drop unused regions
regions_write = [mesh.get_region(region="Vol")]

mesh.drop_unused_nodes_elements(reg_data_list=regions_write)

# %% Write mesh and result data to a new file
file_write = "tutorial_output.cfs"

with CFSWriter(filename=file_write) as f:
    f.create_file(mesh=mesh, result=result_write)
