#!/usr/bin/env python3
"""Command-line interface for FitNotes to Hevy conversion."""

import pathlib
import sys
from datetime import datetime

import pandas as pd
import typer
from typing_extensions import Annotated

# Add src to path for imports
sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))

from fitnotes2hevy import convert_fitnotes_to_hevy, load_exercise_mappings
from fitnotes2hevy.config import (DEFAULT_TRAINING_TIME, INPUT_FILE_PATH,
                                  TIMEZONE_OFFSET_HOURS)

app = typer.Typer()


@app.command()
def main(
    input_file: Annotated[
        pathlib.Path,
        typer.Option("--input-file", "-i", file_okay=True, dir_okay=False, 
                    help="Input FitNotes CSV filepath"),
    ] = pathlib.Path(INPUT_FILE_PATH),
    output_file: Annotated[
        pathlib.Path | None,
        typer.Option("--output-file", "-o", file_okay=True, dir_okay=False, 
                    help="Output Hevy CSV filepath"),
    ] = None,
    timezone_offset: Annotated[
        int,
        typer.Option("--timezone", "-tz", help="Timezone offset from UTC in hours"),
    ] = TIMEZONE_OFFSET_HOURS,
    workout_time: Annotated[
        str,
        typer.Option("--time", "-t", help="Default workout time (HH:MM:SS)"),
    ] = DEFAULT_TRAINING_TIME,
):
    """Convert FitNotes CSV export to Hevy-compatible format."""
    
    if output_file is None:
        timestamp = datetime.now().strftime("%Y-%m-%dT%H-%M-%S")
        output_file = pathlib.Path(f"data/output/fitnotes2hevy_{timestamp}.csv")
        output_file.parent.mkdir(parents=True, exist_ok=True)
    
    print(f"Reading input file: {input_file}")
    
    # Load mappings
    mappings = load_exercise_mappings()
    print(f"Loaded {len(mappings)} exercise mappings")
    
    # Read and convert
    df = pd.read_csv(input_file)
    print(f"Processing {len(df)} sets from {df['Date'].nunique()} workouts")
    
    # Check for unmapped exercises
    unmapped = df[~df['Exercise'].isin(mappings.keys())]['Exercise'].unique()
    if len(unmapped) > 0:
        print(f"Warning: {len(unmapped)} unmapped exercises will keep original names")
        print("Add them to data/mappings/custom.json to map them.\n")
    
    # Convert
    output_df = convert_fitnotes_to_hevy(df, mappings, timezone_offset, workout_time)
    
    # Save
    output_df.to_csv(output_file, index=False, sep=';', quoting=1)
    print(f"\nConversion complete! Output saved to: {output_file}")
    print(f"Total workouts: {output_df['Workout #'].nunique()}")
    print(f"Total exercises: {output_df['Exercise Name'].nunique()}")
    print(f"Total sets: {len(output_df)}")


if __name__ == "__main__":
    app()
