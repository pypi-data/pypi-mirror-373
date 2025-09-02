import os
import shutil
import numpy as np
from typing import List
from tap import Tap
from typing import TypeAlias


class pyCFSParser(Tap):
    setup_type: str  # Which setup to generate. ('newsim', 'newopti', 'extract-snapshot')
    simulation_name: str = "my_simulation"  # Simulation name to be used.
    source_path: str = "./"  # Path to the source file (for snapshot extraction).
    config_file: str = "config.yaml"  # Name of yaml config file to use.
    cfs_path: str = "CFS_PATH"  # Path to OpenCFS on your system.
    mesher_alias: str = "MESHER_ALIAS"  # Path to mesher.
    opt: bool = False  # Flag to decide if sim or opt setup.

    def configure(self) -> None:
        self.add_argument("setup_type")
        self.add_argument("-n", "--simulation_name")
        self.add_argument("-s", "--source_path")


pyCFSParserArgs: TypeAlias = pyCFSParser

# Consts def :
TEMPLATES_DIR_NAME = "templates"
MAIN_XML_TEMPLATE_PATH = __file__[:-18] + "templates/sim.xml"
MAT_XML_TEMPLATE_PATH = __file__[:-18] + "templates/mat.xml"
JOU_TEMPLATE_PATH = __file__[:-18] + "templates/sim.jou"
SETUP_TEMPLATE_PATH = __file__[:-18] + "templates/sim_setup.py"
RUNNER_TEMPLATE_PATH = __file__[:-18] + "templates/run_sim.py"
OPTI_SETUP_TEMPLATE_PATH = __file__[:-18] + "templates/sim_setup_opti.py"
OPTIMIZATION_CONFIG_TEMPLATE_PATH = __file__[:-18] + "templates/config.yaml"

MODELS_DIR_NAME = "models"
DATADUMP_DIR_NAME = "data_dump"
OPTIMIZATION_DIR_NAME = "optimization"

PROJECT_NAME_TOKEN = "PROJECT_NAME"
CFS_PATH_TOKEN = "CFS_PATH"
MESHER_ALIAS_TOKEN = "MESHER_ALIAS"


def write_file_contents(file_path: str, contents: str) -> None:

    file = open(file_path, "w")
    file.write(contents)
    file.close()


def generate(args: pyCFSParserArgs) -> None:
    generators = {
        "newsim": sim_setup_generator,
        "newopti": opti_setup_generator,
    }

    generators[args.setup_type](args)

    print(f"\n  PyCFS : Generated '{args.setup_type}' setup for the current project. \n")


def sim_setup_generator(args: pyCFSParserArgs) -> None:

    sim_root_dir = f"./{args.simulation_name}"
    templates_dir = f"{sim_root_dir}/{TEMPLATES_DIR_NAME}"

    # make directories :
    os.mkdir(sim_root_dir)
    os.mkdir(templates_dir)

    # make template files :
    shutil.copy(
        MAIN_XML_TEMPLATE_PATH,
        f"{templates_dir}/{args.simulation_name}_init.xml",
    )
    shutil.copy(MAT_XML_TEMPLATE_PATH, f"{templates_dir}/mat_init.xml")
    shutil.copy(JOU_TEMPLATE_PATH, f"{templates_dir}/{args.simulation_name}_init.jou")
    shutil.copy(RUNNER_TEMPLATE_PATH, f"{sim_root_dir}/run_sim.py")

    # make setup file and runner:
    generate_setup_py(args, sim_root_dir)


def opti_setup_generator(args: pyCFSParserArgs) -> None:

    project_root_dir = "."
    models_root_dir = f"{project_root_dir}/{MODELS_DIR_NAME}"
    datadump_root_dir = f"{project_root_dir}/{DATADUMP_DIR_NAME}"
    optimization_root_dir = f"{project_root_dir}/{OPTIMIZATION_DIR_NAME}"

    # make directories :
    generate_dirs([models_root_dir, datadump_root_dir, optimization_root_dir])

    # initialize files :
    shutil.copy(OPTIMIZATION_CONFIG_TEMPLATE_PATH, f"{optimization_root_dir}/config.yaml")


def generate_setup_py(args: pyCFSParserArgs, sim_root_dir: str) -> None:

    setup_path = OPTI_SETUP_TEMPLATE_PATH if args.opt else SETUP_TEMPLATE_PATH

    # reads template for setup file :
    fid = open(setup_path, "r")
    setup_content = fid.read()
    fid.close()

    # edit template and write to current project :
    setup_content = setup_content.replace(PROJECT_NAME_TOKEN, args.simulation_name)
    setup_content = setup_content.replace(CFS_PATH_TOKEN, args.cfs_path)
    setup_content = setup_content.replace(MESHER_ALIAS_TOKEN, args.mesher_alias)

    fid = open(f"{sim_root_dir}/sim_setup.py", "w")
    fid.write(setup_content)
    fid.close()


def generate_dirs(dir_paths: List[str]) -> None:
    for path in dir_paths:
        if not os.path.exists(path):
            os.mkdir(path)


def extract_snapshot(args: pyCFSParserArgs) -> None:
    snapshot_path = args.source_path
    extraction_path = args.simulation_name

    snapshot = np.load(snapshot_path, allow_pickle=True)[()]

    # extract infos :
    sim_name = extraction_path.split("/")[-1]
    extraction_path += "/" if extraction_path[-1] != "/" else ""
    templates_path = f"{extraction_path}/templates/"

    # generate directories :
    if os.path.exists(extraction_path):
        raise FileExistsError(
            "The given path already exists - aborting extraction \
                              files might get overwritten!"
        )
    else:
        os.makedirs(templates_path)

        write_file_contents(f"{templates_path}{sim_name}_init.xml", snapshot["meta_data"]["xml_template"])
        write_file_contents(f"{templates_path}mat_init.xml", snapshot["meta_data"]["mat_template"])
        write_file_contents(f"{templates_path}{sim_name}_init.jou", snapshot["meta_data"]["jou_template"])

        for file, content in snapshot["meta_data"]["other_files"].items():
            f_path = file.replace("./", extraction_path)
            f_path_parts = f_path.split("/")
            f_path_parts.pop(-1)
            f_dir_path = "/".join(f_path_parts) + "/"

            if not os.path.exists(f_dir_path):
                os.makedirs(f_dir_path)

            if not os.path.exists(f_path):
                write_file_contents(f_path, content)


def main() -> None:

    # make functions dict
    functions = {"newsim": generate, "newopti": generate, "extract-snapshot": extract_snapshot}

    args = pyCFSParser().parse_args()

    functions[args.setup_type](args)
