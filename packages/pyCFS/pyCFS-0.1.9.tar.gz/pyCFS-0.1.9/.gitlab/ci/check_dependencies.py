import os
import sys
import glob
import re


def parse_requirements(file_path):
    reqs = set()
    with open(file_path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or line.startswith("-r"):
                continue
            reqs.add(line)
    return reqs


def parse_toml_list(content, key):
    match = re.search(rf"{key}\s*=\s*\[(.*?)\]", content, re.DOTALL)
    deps = set()
    if match:
        deps_block = match.group(1)
        for dep in re.split(r",|\n", deps_block):
            dep = dep.strip().strip('"').strip("'")
            if dep and not dep.startswith("#"):
                deps.add(dep)
    return deps


def print_aligned(left, right, left_title, right_title):
    max_len = max([len(dep) for dep in left] + [len(left_title)])
    print(f"{left_title.ljust(max_len)} | {right_title}")
    for l, r in zip(sorted(left), sorted(right)):
        line = f"{l.ljust(max_len)} | {r}"
        if l != r:
            print(f"\033[31m{line}\033[0m")  # Red color for mismatches
        else:
            print(line)


if __name__ == "__main__":
    # Parse requirements/*.txt except common.txt and dev.txt
    files = [f for f in glob.glob("requirements/*.txt") if os.path.basename(f) not in ("common.txt", "dev.txt")]
    reqs = set()
    for file in files:
        reqs.update(parse_requirements(file))

    # Parse dev.txt
    dev_reqs = parse_requirements("requirements/dev.txt")

    # Parse pyproject.toml
    with open("pyproject.toml") as f:
        content = f.read()
    all_tag = parse_toml_list(content, "all")
    dev_tag = parse_toml_list(content, "dev")

    print_aligned(
        sorted(reqs),
        sorted(all_tag),
        "requirements/*.txt (excluding common.txt and dev.txt)",
        "[project.optional-dependencies].all",
    )

    print_aligned(sorted(dev_reqs), sorted(dev_tag), "requirements/dev.txt", "[project.optional-dependencies].dev")

    assert {r.lower() for r in reqs} == {
        a.lower() for a in all_tag
    }, "Mismatch between requirements/*.txt and [project.optional-dependencies].all"
    assert {d.lower() for d in dev_reqs} == {
        v.lower() for v in dev_tag
    }, "Mismatch between requirements/dev.txt and [project.optional-dependencies].dev"
