# %%
# Import necessary modules
from pyCFS.data import io
from pyCFS.data.operators import interpolators

# %%
# Read source file
print(io.file_info("file.cfs"))
mesh = io.read_mesh("file.cfs")
results = io.read_data("file.cfs")

# %%
# Perform interpolation
results_interpolated = interpolators.interpolate_node_to_cell(
    mesh=mesh,
    result=results,
    regions=["V_air"],
    quantity_names={"elecPotential": "interpolated_elecPotential"},
)

# %%
# Add interpolated result to results container
results.combine_with(results_interpolated)

# Check results container
print(results)

# %%
# Write output file
io.write_file("file_out.cfs", mesh=mesh, result=results)
