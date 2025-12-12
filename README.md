# Fitnotes2Hevy

Python tool to convert FitNotes workout exports to Hevy-compatible CSV format (Strong app format).

Key features:

- Exercise name mapping between FitNotes and Hevy
- Automatic timezone adjustment for correct workout timestamps
- Smart conversion of time-based exercises to reps or distance
- Customizable exercise mappings

## Features

- **Exercise Mapping**: 187+ pre-mapped exercises from FitNotes to Hevy names
- **Timezone Support**: Configurable timezone offset for accurate workout times
- **Smart Conversions**:
  - Time → Reps (e.g., Bird Dog, Flutter Kicks)
  - Time → Distance (e.g., Farmer's Walk)
- **Custom Mappings**: Add your own exercise mappings via `map_fitnotes2hevy_custom.json`

## Quick Start

1. **Export your FitNotes data**
   - Open FitNotes → Settings → Spreadsheet Export → select Workout Data → Save Export

2. **Clone and setup**

   ```sh
   git clone https://github.com/alanjonesit/FitNotes2Hevy.git
   cd FitNotes2Hevy
   pip install -e .
   ```

3. **Configure** (edit `src/fitnotes2hevy/config.py`)

   ```python
   DEFAULT_TRAINING_TIME = '07:00:00'  # Desired workout time
   TIMEZONE_OFFSET_HOURS = 10  # Your UTC offset (e.g., 10 for Sydney)
   ```

4. **Run conversion**

   ```sh
   python scripts/convert.py -i data/input/your_export.csv
   ```

   Or with custom options:

   ```sh
   python scripts/convert.py -i path/to/fitnotes.csv -o path/to/output.csv --timezone 10
   ```

5. **Import to Hevy**
   - Open Hevy app → Settings → Export & Import Data → Import Data
   - Select the generated file from `data/output/`

## Web Interface

Run the Streamlit web app for easier conversion:

```sh
pip install -e ".[web]"
streamlit run app.py
```

Or use the hosted version: [Coming soon]

## Configuration

### Timezone Setup

Hevy interprets timestamps as UTC. Set your timezone offset in `src/fitnotes2hevy/config.py` or via CLI:

- **UTC+10** (Sydney, Melbourne): `--timezone 10`
- **UTC-8** (Los Angeles): `--timezone -8`
- **UTC+0** (London): `--timezone 0`

### Custom Exercise Mappings

Add custom mappings in `data/mappings/custom.json`:

```json
{
  "Your FitNotes Exercise": "Hevy Exercise Name"
}
```

### Exercise Conversion Rules

Some exercises are automatically converted:

- **Time → Reps**: Bird Dog, Dead Bug, Flutter Kicks (10 seconds = 1 rep)
- **Time → Distance**: Farmer's Walk (1 second = 1 meter)

Edit these lists in `src/fitnotes2hevy/config.py` if needed.

## Project Structure

```txt
FitNotes2Hevy/
├── src/fitnotes2hevy/      # Core package
│   ├── converter.py        # Conversion logic
│   ├── mappings.py         # Mapping utilities
│   └── config.py           # Configuration
├── data/
│   ├── mappings/           # Exercise mappings
│   ├── exercises/          # Exercise lists
│   └── input/              # Input data files
├── scripts/
│   ├── convert.py          # Conversion script
│   └── validate_mappings.py # Validation utility
├── docs/                   # Documentation
├── app.py                  # Streamlit web app
└── requirements.txt        # Dependencies
```

## Troubleshooting

**Workouts show wrong time in Hevy?**

- Adjust timezone offset: `--timezone 10` or edit `src/fitnotes2hevy/config.py`

**Exercise created as custom in Hevy?**

- Check exercise name matches exactly in `data/exercises/hevy.txt`
- Add mapping in `data/mappings/custom.json`
- The exercise could be measured differently between FitNotes and Hevy. For example, a custom exercise "Bird Dog" in FitNotes could be measured in time, but in Hevy it is measured in reps. This disparity will create a custom exercise.

**Missing exercises?**

- Unmapped exercises keep their FitNotes names
- Add them to `data/mappings/custom.json`

## Documentation

- [Usage Guide](docs/usage.md) - Detailed usage instructions
- [Deployment Guide](docs/deployment.md) - How to deploy the web app
