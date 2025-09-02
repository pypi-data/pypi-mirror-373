import re
from datetime import datetime
from pathlib import Path


def update_version(new_version: str, changelog_path: str = "Changelog.md", init_path: str = "pyCFS/__init__.py"):
    """
    Update version in Changelog.md and __init__.py files.

    Parameters
    ----------
    new_version : str
        New version string (e.g., "0.1.9").
    changelog_path : str, optional
        Path to Changelog.md file. Default is "Changelog.md".
    init_path : str, optional
        Path to __init__.py file. Default is "pyCFS/__init__.py".
    """

    # Update __init__.py
    init_file = Path(init_path)
    if init_file.exists():
        content = init_file.read_text()
        updated_content = re.sub(r'__version__ = "[^"]*"', f'__version__ = "{new_version}"', content)
        init_file.write_text(updated_content)
        print(f"Updated version in {init_path}")

    # Update Changelog.md
    changelog_file = Path(changelog_path)
    if changelog_file.exists():
        content = changelog_file.read_text()
        current_date = datetime.now().strftime("%Y-%m-%d")

        # Create new unreleased section without placeholder bullets
        new_unreleased = """## [Unreleased]

### Added

- ( new features )

### Changed

- ( changes in existing functionality )

### Deprecated

- ( soon-to-be removed features )

### Removed

- ( now removed features )

### Fixed

- ( any bug fixes )

### Security

- ( in case of vulnerabilities )

"""

        # Replace [Unreleased] with new version and date
        updated_content = re.sub(r"## \[Unreleased\]", f"## [{new_version}] - {current_date}", content, count=1)

        # Remove placeholder bullet points from the new version section
        # Match from the version header to the next ## header
        pattern = rf"(## \[{re.escape(new_version)}\] - {current_date}.*?)(## \[[^\]]+\])"

        def clean_section(match):
            section_content = match.group(1)
            next_header = match.group(2)

            # Remove lines with placeholder bullets
            lines = section_content.split("\n")
            cleaned_lines = []
            for line in lines:
                if not re.match(r"^- \( .* \)$", line.strip()):
                    cleaned_lines.append(line)

            # Remove empty categories (categories with no content)
            final_lines = []
            skip_until_next_category = False

            for i, line in enumerate(cleaned_lines):
                if line.startswith("### "):
                    # Check if this category has content
                    has_content = False
                    for j in range(i + 1, len(cleaned_lines)):
                        next_line = cleaned_lines[j]
                        if next_line.startswith("### ") or next_line.startswith("## "):
                            break
                        if next_line.strip() and not next_line.strip() == "":
                            has_content = True
                            break

                    if has_content:
                        final_lines.append(line)
                        skip_until_next_category = False
                    else:
                        skip_until_next_category = True
                elif not skip_until_next_category:
                    final_lines.append(line)

            # Add extra newline before the next version section
            return "\n".join(final_lines) + "\n" + next_header

        updated_content = re.sub(pattern, clean_section, updated_content, flags=re.DOTALL)

        # Add new unreleased section at the top
        updated_content = re.sub(
            f"## \\[{re.escape(new_version)}\\] - {current_date}",
            new_unreleased + f"## [{new_version}] - {current_date}",
            updated_content,
            count=1,
        )

        changelog_file.write_text(updated_content)
        print(f"Updated version in {changelog_path}")


# Usage: update_version("0.1.9")
if __name__ == "__main__":
    update_version(new_version="0.1.9", changelog_path="../../Changelog.md", init_path="../../pyCFS/__init__.py")
