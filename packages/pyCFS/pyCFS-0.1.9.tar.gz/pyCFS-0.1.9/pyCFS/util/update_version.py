"""
pyCFS.util.update_version

Refactors pyCFS scripts files to tackle changes introduced in newer versions of the library.

Usage:
    python update_version.py path/to/your/source_file.py
"""

import re
import argparse


def _refactor_CFSResultContainer_class(file_path: str):
    with open(file_path, "r") as file:
        content = file.read()

    # Replace references to the class
    content = re.sub(r"\bCFSResultData\b", "CFSResultContainer", content)

    with open(file_path, "w") as file:
        file.write(content)


def _refactor_CFSResultContainer_create_file_kwargs(file_path: str):
    with open(file_path, "r") as file:
        content = file.read()

    # Replace keyword arguments in CFSWriter.create_file()
    content = re.sub(r"(create_file\([^)]*)\bmesh_data=\b", r"\1mesh=", content)
    content = re.sub(r"(create_file\([^)]*)\bresult_data=\b", r"\1result=", content)

    with open(file_path, "w") as file:
        file.write(content)


def _refactor_interpolator_kwargs(file_path: str):
    with open(file_path, "r") as file:
        content = file.read()

    # Replace keyword arguments in CFSWriter.create_file()
    content = re.sub(r"(create_file\([^)]*)\bmesh_data=\b", r"\1mesh=", content)
    content = re.sub(r"(create_file\([^)]*)\bresult_data=\b", r"\1result=", content)
    content = re.sub(r"(create_file\([^)]*)\bdata_src=\b", r"\1result_src=", content)

    with open(file_path, "w") as file:
        file.write(content)


def update_to_version_0_1_4(file_path: str):
    print(f"Refactoring class CFSResultData to CFSResultContainer in {file_path}")
    _refactor_CFSResultContainer_class(file_path)
    print(f"Refactoring keyword arguments in CFSWriter.create_file() in {file_path}")
    _refactor_CFSResultContainer_create_file_kwargs(file_path)
    print(f"Refactoring keyword arguments for interpolators in {file_path}")
    _refactor_interpolator_kwargs(file_path)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Refactor CFSResultData class to CFSResultContainer and update keyword arguments."
    )
    parser.add_argument("file_path", type=str, help="Path to the source file to be refactored")
    args = parser.parse_args()

    update_to_version_0_1_4(args.file_path)
