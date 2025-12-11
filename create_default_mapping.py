"""Generate default exercise mappings from FitNotes to Hevy.

This script is a utility for maintaining the mapping files.
The actual mappings used by the converter are in:
- files/map_fitnotes2hevy_default.json (95 default FitNotes exercises)
- files/map_fitnotes2hevy_extra.json (30 common custom exercises)
- files/map_fitnotes2hevy_custom.json (user customizations)

This script is NOT required for normal operation.
"""

import json
from difflib import get_close_matches

# Load exercise lists
with open('files/fitnotes_exercises_default.txt', 'r') as f:
    fitnotes_default = sorted(set(line.strip() for line in f if line.strip()))

with open('files/fitnotes_exercises_extra.txt', 'r') as f:
    fitnotes_extra = sorted(set(line.strip() for line in f if line.strip()))

with open('files/hevy_exercises.txt', 'r') as f:
    hevy_exercises = [line.strip() for line in f if line.strip()]

# Load current mappings
with open('files/map_fitnotes2hevy_default.json', 'r') as f:
    default_map = json.load(f)

with open('files/map_fitnotes2hevy_extra.json', 'r') as f:
    extra_map = json.load(f)

# Report
print("Current mapping status:")
print(f"  Default: {len(default_map)}/{len(fitnotes_default)} exercises")
print(f"  Extra: {len(extra_map)}/{len(fitnotes_extra)} exercises")

# Check for missing mappings
missing_default = set(fitnotes_default) - set(default_map.keys())
missing_extra = set(fitnotes_extra) - set(extra_map.keys())

if missing_default:
    print(f"\nMissing from default map: {missing_default}")
if missing_extra:
    print(f"\nMissing from extra map: {missing_extra}")

if not missing_default and not missing_extra:
    print("\n✓ All exercises are mapped!")
