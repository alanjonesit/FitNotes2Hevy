#!/usr/bin/env python3
"""Validate exercise mapping completeness."""

import json
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Load exercise lists
with open("data/exercises/fitnotes_default.txt", "r") as f:
    fitnotes_default = sorted(set(line.strip() for line in f if line.strip()))

with open("data/exercises/fitnotes_extra.txt", "r") as f:
    fitnotes_extra = sorted(set(line.strip() for line in f if line.strip()))

# Load mappings
with open("data/mappings/default.json", "r") as f:
    default_map = json.load(f)

with open("data/mappings/extra.json", "r") as f:
    extra_map = json.load(f)

# Report
print("Mapping validation:")
print(f"  Default: {len(default_map)}/{len(fitnotes_default)} exercises")
print(f"  Extra: {len(extra_map)}/{len(fitnotes_extra)} exercises")

# Check for missing
missing_default = set(fitnotes_default) - set(default_map.keys())
missing_extra = set(fitnotes_extra) - set(extra_map.keys())

if missing_default:
    print(f"\nMissing from default: {missing_default}")
if missing_extra:
    print(f"\nMissing from extra: {missing_extra}")

if not missing_default and not missing_extra:
    print("\n✓ All exercises are mapped!")
