from pyCFS.data import io

# Read file
with io.CFSReader(filename="file.cfs") as f:
    # Read mesh data
    mesh = f.MeshData
    # Read results of sequence step 1
    results = f.get_multi_step_data(multi_step_id=1)

# View connectivity array, get coordinates of V_air
conn = mesh.Connectivity
reg_coord = mesh.get_region_coordinates(region="V_air")

# Get data array of elecPotential in region V_air
elec_pot = results.get_data_array(quantity="elecPotential", region="V_air")

# Manipulate result
igte_factor = 1e0
elec_pot *= igte_factor

# Write "corrected" result to new sequence step
result_write = io.CFSResultContainer(data=[elec_pot], analysis_type=elec_pot.AnalysisType, multi_step_id=2)
with io.CFSWriter("file.cfs") as f:
    f.write_multistep(result=result_write)
