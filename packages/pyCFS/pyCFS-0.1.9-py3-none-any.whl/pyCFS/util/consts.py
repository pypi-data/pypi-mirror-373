# Constants :
WIN_ID = "nt"
UNIX_ID = "posix"
N_PARAM_GROUPS = 4
CFS_EXT = "cfs"
XML_EXT = "xml"
JOU_EXT = "jou"
CDB_EXT = "cdb"
SA_NAME_SEPARATOR = "-"
SA_COORD_KEYS = ["origElemNum", "globCoord", "locCoord"]
LAST_EXEC_START = "last_exec_start"
LAST_EXEC_STOP = "last_exec_stop"
SIM_NAME_TOKEN = "SIM_NAME"
EXPORT_MATRICES_TOKEN = "<standard>"
LINEAR_SYSTEMS_TOKEN = "</sequenceStep>"
INSERT = "INSERT"
VEC_TOKEN = "vec"
SOL_TOKEN = "sol"
RHS_TOKEN = "rhs"
MAT_TOKEN = "sys"
MTX_TOKEN = "mtx"

INFO_BOX_WIDTH = 90
INFO_BOX_CHAR = "#"

# Regex pattern
RESLIST_PATTERN = r"((?:\w+_)+(?:NODELIST|ELEMLIST))"

# Templates
ITEM_TEMPLATE = """<ITEMs name="NAME"><coord x="X_COORD" y="Y_COORD" z="Z_COORD"/></ITEMs>"""
ITEM_RES_TEMPLATE = """<ITEMs name="NAME" outputIds="hdf5"/>"""

LIST_TEMPLATE = """
<!-- inserted by pyCFS -->
<ITEMList>
    INSERT
</ITEMList>
"""
EXPORT_MATRICES_TEMPLATE = """
<exportLinSys format="matrix-market" mass="true" system="true" rhs="true" baseName="SIM_NAME" />
<matrix reordering="noReordering"/>
"""

LINEAR_SYSTEMS_TEMPLATE = """
<!-- inserted by pyCFS -->
    <linearSystems>
        <system>
            <solutionStrategy>
                <standard>
                    INSERT
                </standard>
            </solutionStrategy>
        </system>
    </linearSystems>
</sequenceStep>
"""

MESH_CONVERT_TEMPLATE = """<?xml version="1.0" encoding="UTF-8"?>
<cfsSimulation xmlns="http://www.cfs++.org/simulation"
xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
xsi:schemaLocation="http://www.cfs++.org/simulation
https://opencfs.gitlab.io/cfs/xml/CFS-Simulation/CFS.xsd">
    <!-- define which files are needed for simulation input & output-->
    <fileFormats>
        <input>
        <cdb fileName="CDB_FILE_NAME.cdb"/>
        </input>
        <output>
            <hdf5/>
        </output>
        <materialData file="MAT_FILE_NAME.xml" format="xml"/>
    </fileFormats>
    <!-- material assignment -->
    <domain geometryType="GEOMETRY_TYPE">
    </domain>
</cfsSimulation>
"""

MESH_CONVERT_MAT_TEMPLATE = """<cfsMaterialDataBase xmlns="http://www.cfs++.org/material"
xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
xsi:schemaLocation="http://www.cfs++.org/material
https://opencfs.gitlab.io/cfs/xml/CFS-Material/CFS_Material.xsd" >
<material name="air"></material>
</cfsMaterialDataBase>
"""

CDB_FILENAME = "CDB_FILE_NAME"
MAT_FILENAME = "MAT_FILE_NAME"
GEOMETRY_TYPE = "GEOMETRY_TYPE"
MESHCONVERT_XML_NAME = "mesh_convert"
MESHCONVERT_MAT_NAME = "mesh_convert_mat"
TOPOPT_PARAM_FILE_NAME = "topopt_parameters"

X_COORD_SA = "X_COORD"
Y_COORD_SA = "Y_COORD"
Z_COORD_SA = "Z_COORD"
ITEM = "ITEM"
ITEM_NAME = "NAME"
NODE = "node"
ELEM = "elem"
NODES = "nodes"
ELEMS = "elems"
RES_NODES = "res_nodes"
RES_ELEMS = "res_elems"

# Paths :
RESULTS_HDF_DIR = "results_hdf5"
HISTORY_DIR = "history"
LOGS_DIR = "logs"
SA_STORAGE_DIR = f"{HISTORY_DIR}"
DATA_DUMP_DIR = "data_dump"
