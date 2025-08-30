"""Documentation utilities for error patterns and resolutions."""

from typing import Any

from .migration_errors import get_all_error_patterns


def print_error_documentation():
    """Print comprehensive documentation of all error patterns and resolutions."""
    patterns = get_all_error_patterns()

    print("# Morpheus Migration Error Patterns and Resolutions\n")
    print(
        "This document describes all known error patterns and their automatic resolutions.\n"
    )

    for error_class_name, info in patterns.items():
        print(f"## {info['name']}")
        print(f"**Class:** `{error_class_name}`\n")

        print(f"**Description:** {info['description']}\n")

        print("**Detection Patterns:**")
        for pattern in info["patterns"]:
            print(f"- `{pattern}`")
        print()

        print(f"**Automatic Resolution:** {info['solution']}\n")

        print("---\n")


def get_error_patterns_json() -> dict[str, Any]:
    """Get error patterns as JSON-serializable dictionary for API/tooling."""
    return get_all_error_patterns()


if __name__ == "__main__":
    print_error_documentation()
