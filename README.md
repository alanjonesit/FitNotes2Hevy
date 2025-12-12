# FitNotes2Hevy

Convert [FitNotes](https://www.fitnotesapp.com/) workout exports to [Hevy](https://www.hevyapp.com/)-compatible CSV format.

## Features

- **300+ Exercise Mappings**: Automatically converts FitNotes exercise names to Hevy equivalents
- **Custom Mappings**: Add, import, and export your own exercise mappings
- **Timezone Support**: Accurate workout timestamps for your location
- **Smart Conversions**: Automatically handles time-based exercises
- **Web & CLI**: [Streamlit](https://streamlit.io/) web interface or command-line tool

## Quick Start

### Web Interface (Easiest)

Visit **[fitnotes2hevy.streamlit.app](https://fitnotes2hevy.streamlit.app)** and upload your FitNotes export.

Or run the Streamlit app locally:

```sh
git clone https://github.com/alanjonesit/FitNotes2Hevy.git
cd FitNotes2Hevy
pip install -e ".[web]"
streamlit run app.py
```

### Command Line

1. **Export from FitNotes**

   - Open FitNotes → Settings → Spreadsheet Export → Workout Data → Save

2. **Install and convert**

   ```sh
   git clone https://github.com/alanjonesit/FitNotes2Hevy.git
   cd FitNotes2Hevy
   pip install -e .
   python scripts/convert.py -i your_export.csv --timezone 10
   ```

3. **Import to Hevy**

   - Open Hevy → Settings → Export & Import Data → Import Data
   - Select the generated CSV from `data/output/`

## Configuration

### Timezone

Set your UTC offset to ensure correct workout times:

```sh
python scripts/convert.py -i input.csv --timezone 10  # Sydney (UTC+10)
python scripts/convert.py -i input.csv --timezone -8  # Los Angeles (UTC-8)
```

### Custom Exercise Mappings

**Via Web Interface:** Use the Custom Mappings tab to add, import, or export mappings.

**Via JSON file:** Create `data/mappings/custom.json`:

```json
{
  "Your FitNotes Exercise": "Hevy Exercise Name"
}
```

## CLI Options

```sh
python scripts/convert.py \
  -i input.csv \           # Input FitNotes export
  -o output.csv \          # Output file (optional)
  --timezone 10 \          # UTC offset
  --time "07:00" \         # Default workout time
  --duration "60m" \       # Default duration
  --name "Workout" \       # Default workout name
  --notes "From FitNotes"  # Default notes
```

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

**Workouts showing wrong times?**

- Adjust the timezone offset to match your location (e.g., `--timezone 10` for Sydney)

**Exercise appears as custom in Hevy?**

- The exercise name doesn't match exactly, or uses different units (time vs reps)
- Add a custom mapping in the web interface or `data/mappings/custom.json`

**Missing exercises after import?**

- Unmapped exercises keep their FitNotes names and appear as custom exercises
- Add mappings for them to use Hevy's built-in exercises

## Development

Install development dependencies:

```sh
pip install -e ".[dev]"
```

Run linting:

```sh
black .
isort .
flake8 .
mypy .
bandit -r src/
```
