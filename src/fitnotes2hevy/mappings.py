"""Exercise mapping utilities."""

import json
from pathlib import Path


def load_exercise_mappings(data_dir="data/mappings"):
    """Load exercise mappings from JSON files.

    Loads in order: default -> extra -> custom (later overrides earlier).

    Args:
        data_dir: Directory containing mapping JSON files

    Returns:
        dict: Combined exercise mappings
    """
    mappings = {}
    data_path = Path(data_dir)

    for filename in ["default.json", "extra.json", "custom.json"]:
        filepath = data_path / filename
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                mapping = json.load(f)
                # Filter out comment keys in custom mappings
                if filename == "custom.json":
                    mapping = {
                        k: v for k, v in mapping.items() if not k.startswith("_")
                    }
                mappings.update(mapping)
        except FileNotFoundError:
            if filename != "custom.json":
                print(f"Warning: {filepath} not found")

    return mappings
