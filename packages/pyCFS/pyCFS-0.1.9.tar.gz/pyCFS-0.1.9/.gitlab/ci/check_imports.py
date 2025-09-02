"""
Check if all Python files (not starting with _) are imported in corresponding __init__.py files.
"""

from pathlib import Path
import ast
import re


def check_init_imports(root_dir: str = "pyCFS", exclude: list[str] = []) -> dict:
    """
    Check if all Python files (not starting with _) are imported in corresponding __init__.py files
    and if they are listed in __all__.

    Args:
        root_dir: Root directory to check (default: "pyCFS")
        exclude: List of directories/files to exclude

    Returns:
        dict: Results with missing imports, missing __all__ entries, and errors
    """
    results = {"directory_imports": {}, "errors": [], "total_files_checked": 0, "total_directories_checked": 0}

    root_path = Path(root_dir)

    if not root_path.exists():
        results["errors"].append(f"Root directory '{root_dir}' does not exist")
        return results

    # Walk through all directories
    for current_dir in root_path.rglob("*"):
        if not current_dir.is_dir():
            continue
        # Skip excluded directories
        if current_dir.name in exclude:
            continue

        results["total_directories_checked"] += 1
        init_file = current_dir / "__init__.py"

        # Get all Python files in current directory (excluding those starting with "_" or "debug")
        python_files = [
            f.stem
            for f in current_dir.iterdir()
            if f.is_file()
            and f.suffix == ".py"
            and not f.name.startswith("_")
            and not f.name.startswith("debug")
            and not f.name in exclude
            and f.name != "__init__.py"
        ]

        results["total_files_checked"] += len(python_files)

        if not python_files:
            continue

        # Check if __init__.py exists
        if not init_file.exists():
            results["directory_imports"][str(current_dir)] = {
                "missing_init": True,
                "missing_modules": python_files,
                "missing_all_entries": [],
                "all_variable": None,
            }
            continue

        # Parse __init__.py to find imports and __all__
        try:
            with open(init_file, "r", encoding="utf-8") as f:
                content = f.read()

            imported_modules = set()
            all_variable = None

            # Parse AST to find imports and __all__
            try:
                tree = ast.parse(content)

                def extract_all_from_list(list_node):
                    """Extract string values from a list node."""
                    items = []
                    for elt in list_node.elts:
                        if isinstance(elt, ast.Str):
                            items.append(elt.s)
                        elif isinstance(elt, ast.Constant) and isinstance(elt.value, str):
                            items.append(elt.value)
                    return items

                def find_all_assignments(node):
                    """Find __all__ assignments in any context (including if statements)."""
                    all_items = []

                    if isinstance(node, ast.Assign):
                        for target in node.targets:
                            if isinstance(target, ast.Name) and target.id == "__all__":
                                if isinstance(node.value, ast.List):
                                    all_items.extend(extract_all_from_list(node.value))

                    elif isinstance(node, ast.AugAssign):
                        # Handle __all__ += [...]
                        if isinstance(node.target, ast.Name) and node.target.id == "__all__":
                            if isinstance(node.value, ast.List):
                                all_items.extend(extract_all_from_list(node.value))

                    elif isinstance(node, ast.Expr) and isinstance(node.value, ast.Call):
                        # Handle __all__.extend([...]) or __all__.append(...)
                        if isinstance(node.value.func, ast.Attribute):
                            if isinstance(node.value.func.value, ast.Name) and node.value.func.value.id == "__all__":
                                if node.value.func.attr in ["extend", "append"]:
                                    for arg in node.value.args:
                                        if isinstance(arg, ast.List):
                                            all_items.extend(extract_all_from_list(arg))
                                        elif isinstance(arg, (ast.Str, ast.Constant)):
                                            if isinstance(arg, ast.Str):
                                                all_items.append(arg.s)
                                            elif isinstance(arg.value, str):
                                                all_items.append(arg.value)

                    return all_items

                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            imported_modules.add(alias.name.split(".")[0])
                    elif isinstance(node, ast.ImportFrom):
                        if node.level == 1:  # relative import from current package
                            for alias in node.names:
                                imported_modules.add(alias.name)
                        elif node.module:
                            # Handle absolute imports within the package
                            module_parts = node.module.split(".")
                            if len(module_parts) > 0:
                                imported_modules.add(module_parts[-1])

                    # Find all __all__ assignments (including conditional ones)
                    all_items = find_all_assignments(node)
                    if all_items:
                        if all_variable is None:
                            all_variable = []
                        all_variable.extend(all_items)

            except SyntaxError as e:
                results["errors"].append(f"Syntax error in {init_file}: {e}")
                continue

            # Also check for simple string-based imports (fallback)
            import_patterns = [
                r"from\s+\.(\w+)\s+import",  # from .module import
                r"import\s+\.(\w+)",  # import .module
                r"from\s+\.\s+import\s+(\w+)",  # from . import module
            ]

            for pattern in import_patterns:
                matches = re.findall(pattern, content)
                imported_modules.update(matches)

            # Find missing imports
            missing_imports = [module for module in python_files if module not in imported_modules]

            # Find missing __all__ entries
            missing_all_entries = []
            if all_variable is not None:
                # Remove duplicates from all_variable
                all_variable = list(set(all_variable))
                missing_all_entries = [module for module in python_files if module not in all_variable]
            else:
                # If __all__ doesn't exist, all modules are considered missing from __all__
                missing_all_entries = python_files.copy()

            results["directory_imports"][str(current_dir)] = {
                "missing_init": False,
                "missing_modules": missing_imports,
                "missing_all_entries": missing_all_entries,
                "imported_modules": list(imported_modules),
                "available_modules": python_files,
                "all_variable": all_variable,
            }

        except Exception as e:
            results["errors"].append(f"Error reading {init_file}: {e}")

    return results


def check_results(results: dict) -> bool:
    """Print the results of check_init_imports in a readable format."""
    return_value = True
    print("=== Python Module Import Check ===\n")

    print(f"Directories checked: {results['total_directories_checked']}")
    print(f"Python files checked: {results['total_files_checked']}\n")

    if results["errors"]:
        print("ERRORS:")
        for error in results["errors"]:
            print(f"  ❌ {error}")
        print()

    if results["directory_imports"]:
        print("Module structure:")
        for directory, info in results["directory_imports"].items():
            print(f"\n📁 {directory}")
            if info["missing_init"]:
                return_value = False
                print("  ❌ No __init__.py file found")
                print(f"  📄 Modules that should be imported: {', '.join(info['missing_modules'])}")
            else:
                if info["missing_modules"]:
                    return_value = False
                    print(f"  ❌ Missing imports: {', '.join(info['missing_modules'])}")

                if info["missing_all_entries"]:
                    return_value = False
                    if info["all_variable"] is None:
                        print("  ❌ No __all__ variable found")
                        print(f"  📄 Modules that should be in __all__: {', '.join(info['missing_all_entries'])}")
                    else:
                        print(f"  ❌ Missing from __all__: {', '.join(info['missing_all_entries'])}")

                if "imported_modules" in info:
                    print(
                        f"  ✅ Currently imported: {', '.join(info['imported_modules']) if info['imported_modules'] else 'None'}"
                    )

                if info["all_variable"] is not None:
                    print(
                        f"  ✅ Currently in __all__: {', '.join(info['all_variable']) if info['all_variable'] else 'None'}"
                    )

    if return_value:
        print("\n✅ All Python files are properly imported and listed in __all__ variables!")

    return return_value


# Usage example:
if __name__ == "__main__":
    # results = check_init_imports(root_dir="../../pyCFS", exclude=["templates"])
    results = check_init_imports(root_dir="pyCFS", exclude=["templates"])
    assert check_results(results), "Imports are missing or __all__ entries are incomplete!"
