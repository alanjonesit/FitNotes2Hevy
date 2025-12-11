"""Convert FitNotes workout data to Hevy-compatible CSV format.

This script reads a FitNotes CSV export and converts it to the format
required by Hevy app for importing workout history.
"""

import pandas as pd
import json
import pathlib
from datetime import datetime, timedelta
from typing_extensions import Annotated
import typer
from config import *

app = typer.Typer()

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def parse_time_to_seconds(time_str):
    """Convert time string (HH:MM:SS, MM:SS, or seconds) to integer seconds."""
    if pd.isna(time_str) or time_str == '':
        return 0
    try:
        parts = str(time_str).split(':')
        if len(parts) == 3:
            return int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2])
        elif len(parts) == 2:
            return int(parts[0]) * 60 + int(parts[1])
        else:
            return int(float(time_str))
    except:
        return 0

@app.command()
def main(
    input_file: Annotated[
        pathlib.Path,
        typer.Option(
            "--input-file", "-i", file_okay=True, dir_okay=False, help="Input FitNotes CSV filepath"
        ),
    ] = pathlib.Path(FIT_NOTES_PATH),
    output_file: Annotated[
        pathlib.Path,
        typer.Option(
            "--output-file", "-o", file_okay=True, dir_okay=False, help="Output Hevy CSV filepath"
        ),
    ] = None,
):
    if output_file is None:
        timestamp = datetime.now().strftime("%Y-%m-%dT%H-%M-%S")
        output_file = pathlib.Path(f"./files/output/fitnotes2hevy_{timestamp}.csv")
        output_file.parent.mkdir(parents=True, exist_ok=True)
    
    print(f"Reading input file: {input_file}")

    # Load exercise mappings (default -> extra -> custom, later overrides earlier)
    map_fn2hevy = {}
    for filename, label in [('default', 'default'), ('extra', 'extra'), ('custom', 'custom')]:
        try:
            with open(f'./files/map_fitnotes2hevy_{filename}.json', 'r', encoding='utf-8') as f:
                mapping = json.load(f)
                if filename == 'custom':
                    mapping = {k: v for k, v in mapping.items() if not k.startswith('_')}
                map_fn2hevy.update(mapping)
                if filename != 'default' and mapping:
                    print(f"Loaded {len(mapping)} {label} exercise mappings")
        except FileNotFoundError:
            if filename != 'custom':
                print(f"Warning: {filename} mappings file not found")

    # Read and prepare data
    df = pd.read_csv(input_file)
    df['first_appearance'] = df.groupby(['Date', 'Exercise']).cumcount()
    df['exercise_order'] = df.groupby(['Date', 'Exercise'])['first_appearance'].transform('idxmin')

    # Convert fields to Hevy format
    df['Workout #'] = df.groupby('Date').ngroup() + 1
    df['Date'] = (pd.to_datetime(df['Date'] + ' ' + DEFAULT_TRAINING_TIME) - 
                  timedelta(hours=TIMEZONE_OFFSET_HOURS)).dt.strftime('%Y-%m-%d %H:%M:%S')
    df['Workout Name'] = DEFAULT_WORKOUT_NAME
    
    duration_str = str(DEFAULT_DURATION).lower()
    duration_sec = (int(duration_str.replace('m', '')) * 60 if 'm' in duration_str else
                   int(duration_str.replace('s', '')) if 's' in duration_str else
                   int(duration_str))
    df['Duration (sec)'] = duration_sec

    df['Exercise Name'] = df['Exercise'].map(map_fn2hevy).fillna(df['Exercise'])
    
    unmapped = df[df['Exercise'].map(map_fn2hevy).isna()]['Exercise'].unique()
    if len(unmapped) > 0:
        print(f"Warning: {len(unmapped)} unmapped exercises will keep original names")
        print("Add them to map_fitnotes2hevy_custom.json to map them.\n")
    
    df = df.sort_values(['Date', 'exercise_order', 'first_appearance'])
    df['Set Order'] = df.groupby(['Date', 'Exercise Name']).cumcount() + 1
    df['Weight (kg)'] = df['Weight'].apply(lambda x: str(x) if pd.notna(x) and x != '' else '')

    # Define conversion rules for exercises
    time_to_reps_exercises = ['Bird Dog', 'Dead Bug', 'Deadbug', 'Flutter Kicks', 'Flutter Kick']
    time_to_distance_exercises = ['Farmers Walk', 'Farmer Walk', "Farmer's Walk", "Farmer's Carry"]
    reps_to_time_exercises = ['Warm Up']
    
    # Reps: can be blank, convert to int if present
    def convert_reps(row):
        if pd.notna(row['Reps']) and row['Reps'] != '':
            return int(row['Reps'])
        # If no reps but has time, and exercise should use reps, convert time to reps
        if row['Exercise Name'] in time_to_reps_exercises:
            secs = parse_time_to_seconds(row.get('Time', ''))
            if secs > 0:
                return max(1, secs // 10)  # 10 seconds = 1 rep
        return ''
    
    df['Reps'] = df.apply(convert_reps, axis=1)

    # Distance (meters): numeric only, or convert from time for certain exercises
    def convert_distance(row):
        # If distance already exists, use it
        if 'Distance' in row and pd.notna(row['Distance']) and row['Distance'] != '' and row['Distance'] != 0:
            return str(int(row['Distance']))
        # For exercises that track time but Hevy expects distance, estimate distance
        if row['Exercise Name'] in time_to_distance_exercises:
            secs = parse_time_to_seconds(row.get('Time', ''))
            if secs > 0:
                return str(secs)  # 1 second = 1 meter estimate
        return ''
    
    df['Distance (meters)'] = df.apply(convert_distance, axis=1)

    # Seconds: convert time to seconds, empty if 0
    # Don't populate seconds for exercises converted to reps or distance
    # Convert reps to seconds for Warm Up exercises
    def convert_seconds(row):
        # Convert reps to time for Warm Up exercises (1 rep = 1 second)
        if row['Exercise Name'] in reps_to_time_exercises:
            if pd.notna(row['Reps']) and row['Reps'] != '':
                return str(float(row['Reps']))
        
        # Skip if exercise was converted from time to reps or distance
        if row['Exercise Name'] in time_to_reps_exercises and pd.notna(row['Reps']) and row['Reps'] != '':
            return ''
        if row['Exercise Name'] in time_to_distance_exercises and pd.notna(row['Distance (meters)']) and row['Distance (meters)'] != '':
            return ''
        
        secs = parse_time_to_seconds(row.get('Time', ''))
        return str(float(secs)) if secs > 0 else ''
    
    df['Seconds'] = df.apply(convert_seconds, axis=1)
    df.loc[df['Exercise Name'].isin(reps_to_time_exercises), 'Reps'] = ''
    
    df['Notes'] = df['Comment'].fillna('') if 'Comment' in df.columns else ''
    
    # Add original exercise name to notes for specific renamed exercises
    def add_conversion_note(row):
        note = str(row['Notes']) if row['Notes'] else ''
        if row['Exercise'] != row['Exercise Name']:
            if (('backward' in row['Exercise'].lower() and 'walk' in row['Exercise'].lower()) or 
                row['Exercise Name'] in ['Warm Up', 'Stretching']):
                return f"{row['Exercise']}; {note}" if note else row['Exercise']
        return note
    
    df['Notes'] = df.apply(add_conversion_note, axis=1)
    df['Workout Notes'] = DEFAULT_WORKOUT_NOTES
    df['RPE'] = ''

    # Output in Strong format
    columns = ['Workout #', 'Date', 'Workout Name', 'Duration (sec)', 'Exercise Name', 
               'Set Order', 'Weight (kg)', 'Reps', 'RPE', 'Distance (meters)', 
               'Seconds', 'Notes', 'Workout Notes']
    df[columns].to_csv(output_file, index=False, sep=';', quoting=1)
    print(f"\nConversion complete! Output saved to: {output_file}")


if __name__ == "__main__":
    app()
