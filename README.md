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

   - Open FitNotes → Settings → Spreadsheet Export
   - Save the CSV file

2. **Clone and setup**

   ```sh
   git clone https://github.com/alanjonesit/FitNotes2Hevy.git
   cd FitNotes2Hevy
   pip install -r requirements.txt
   ```

3. **Configure** (edit `config.py`)

   ```python
   FIT_NOTES_PATH = './files/input/your_export.csv'
   DEFAULT_TRAINING_TIME = '07:00:00'  # Desired workout time
   TIMEZONE_OFFSET_HOURS = 10  # Your UTC offset (e.g., 10 for Sydney)
   ```

4. **Run conversion**

   ```sh
   python main.py
   ```

   Or with custom paths:

   ```sh
   python main.py -i path/to/fitnotes.csv -o path/to/output.csv
   ```

5. **Import to Hevy**
   - Open Hevy app → Settings → Export & Import Data → Import Data
   - Select the generated file from `files/output/`

## Configuration

### Timezone Setup

Hevy interprets timestamps as UTC. Set your timezone offset in `config.py`:

- **UTC+10** (Sydney, Melbourne): `TIMEZONE_OFFSET_HOURS = 10`
- **UTC-8** (Los Angeles): `TIMEZONE_OFFSET_HOURS = -8`
- **UTC+0** (London): `TIMEZONE_OFFSET_HOURS = 0`

### Custom Exercise Mappings

Add custom mappings in `files/map_fitnotes2hevy_custom.json`:

```json
{
  "Your FitNotes Exercise": "Hevy Exercise Name"
}
```

### Exercise Conversion Rules

Some exercises are automatically converted:

- **Time → Reps**: Bird Dog, Dead Bug, Flutter Kicks (10 seconds = 1 rep)
- **Time → Distance**: Farmer's Walk (1 second = 1 meter)

Edit these lists in `main.py` if needed.

## Files

- `main.py` - Main conversion script
- `config.py` - User configuration
- `files/map_fitnotes2hevy_default.json` - Default exercise mappings
- `files/map_fitnotes2hevy_custom.json` - Your custom mappings
- `files/fitnotes_exercises.txt` - All FitNotes exercises
- `files/hevy_exercises.txt` - All Hevy exercises

## Troubleshooting

**Workouts show wrong time in Hevy?**

- Adjust `TIMEZONE_OFFSET_HOURS` in `config.py`

**Exercise created as custom in Hevy?**

- Check exercise name matches exactly in `files/hevy_exercises.txt`
- Add mapping in `files/map_fitnotes2hevy_custom.json`
- The exercise could be measured differently between FitNotes and Hevy. For example, a custom exercise "Bird Dog" in FitNotes could be measured in time, but in Hevy it is measured in reps. This disparity will create a custom exercise.

**Missing exercises?**

- Unmapped exercises keep their FitNotes names
- Add them to `map_fitnotes2hevy_custom.json`
