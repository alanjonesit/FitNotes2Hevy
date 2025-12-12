# Usage Guide

## Command Line Interface

### Basic Usage

```bash
python scripts/convert.py -i data/input/your_export.csv
```

### With Custom Options

```bash
python scripts/convert.py \
  -i data/input/your_export.csv \
  -o data/output/converted.csv \
  --timezone 10 \
  --time "07:00:00"
```

### Options

- `-i, --input-file`: Path to FitNotes CSV export
- `-o, --output-file`: Path for output file (optional, auto-generated if not provided)
- `-tz, --timezone`: Timezone offset from UTC in hours (default: 10)
- `-t, --time`: Default workout time in HH:MM:SS format (default: 07:00:00)

## Web Interface

### Local Development

```bash
streamlit run app.py
```

Then open http://localhost:8501 in your browser.

### Features

- Drag-and-drop file upload
- Exercise mapping preview
- Real-time conversion
- Download converted file
- Summary statistics

## Python API

### As a Module

```python
from src.fitnotes2hevy import convert_fitnotes_to_hevy, load_exercise_mappings
import pandas as pd

# Load data
df = pd.read_csv('data/input/fitnotes_export.csv')

# Load mappings
mappings = load_exercise_mappings()

# Convert
output_df = convert_fitnotes_to_hevy(df, mappings, timezone_offset=10)

# Save
output_df.to_csv('output.csv', index=False, sep=';', quoting=1)
```

## Custom Exercise Mappings

Add your custom mappings to `data/mappings/custom.json`:

```json
{
  "Your FitNotes Exercise": "Hevy Exercise Name",
  "Another Exercise": "Mapped Name"
}
```

The converter loads mappings in this order (later overrides earlier):

1. `default.json` - Standard FitNotes exercises
2. `extra.json` - Common custom exercises
3. `custom.json` - Your personal mappings
