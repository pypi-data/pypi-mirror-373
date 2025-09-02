import os
from pathlib import Path


src_dir = Path("docs/source/generated")
for file in src_dir.iterdir():
    print("Processed RST file:", file)

    module_name = os.path.split(os.path.splitext(file)[0])[1]

    # Remove junk strings
    with open(file, "r") as f:
        lines = f.readlines()

    # Shorten title
    if lines:
        for module_part in module_name.split("."):
            lines[0] = lines[0].replace(f"{module_part}.", "")
        lines[0] = lines[0].replace(" module\n", "\n")
        lines[0] = lines[0].replace(" package\n", "\n")

    lines = "".join(lines)
    junk_strs = ["Submodules\n----------", "Subpackages\n-----------"]

    for junk in junk_strs:
        lines = lines.replace(junk, "")

    with open(file, "w") as f:
        f.write(lines)
