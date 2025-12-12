"""Core conversion logic for FitNotes to Hevy format."""

from datetime import timedelta

import pandas as pd

from .config import *


def validate_fitnotes_dataframe(df):
    """Validate that DataFrame matches FitNotes export format.

    Args:
        df: DataFrame to validate

    Raises:
        ValueError: If validation fails with descriptive message
    """
    # Check required columns
    required_columns = [
        "Date",
        "Exercise",
        "Category",
        "Weight",
        "Weight Unit",
        "Reps",
        "Distance",
        "Distance Unit",
        "Time",
    ]
    missing_columns = [col for col in required_columns if col not in df.columns]

    if missing_columns:
        raise ValueError(
            f"Invalid file format. This doesn't appear to be a FitNotes export. "
            f"Missing columns: {', '.join(missing_columns)}.\n\n"
            f"Please upload a CSV file exported from FitNotes. "
            f"Go to FitNotes → Settings → Spreadsheet Export → Workout Data."
        )

    # Check if DataFrame is empty
    if df.empty:
        raise ValueError(
            "The file is empty. Please upload a FitNotes export with workout data."
        )

    # Check if required fields have data
    if df["Date"].isna().all():
        raise ValueError("No valid dates found in the file.")

    if df["Exercise"].isna().all():
        raise ValueError("No exercises found in the file.")


def parse_time_to_seconds(time_str):
    """Convert time string (HH:MM:SS, MM:SS, or seconds) to integer seconds."""
    if pd.isna(time_str) or time_str == "":
        return 0
    try:
        parts = str(time_str).split(":")
        if len(parts) == 3:
            return int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2])
        elif len(parts) == 2:
            return int(parts[0]) * 60 + int(parts[1])
        else:
            return int(float(time_str))
    except:
        return 0


def convert_fitnotes_to_hevy(
    df,
    mappings,
    timezone_offset=TIMEZONE_OFFSET_HOURS,
    workout_time=DEFAULT_TRAINING_TIME,
    workout_name=DEFAULT_WORKOUT_NAME,
    workout_duration=DEFAULT_DURATION,
    workout_notes=DEFAULT_WORKOUT_NOTES,
):
    """Convert FitNotes DataFrame to Hevy format.

    Args:
        df: FitNotes DataFrame
        mappings: Exercise name mappings dict
        timezone_offset: Timezone offset in hours
        workout_time: Default workout time string
        workout_name: Workout name
        workout_duration: Workout duration
        workout_notes: Workout notes

    Returns:
        DataFrame in Hevy format

    Raises:
        ValueError: If input data is invalid
    """
    # Validate input
    validate_fitnotes_dataframe(df)

    # Normalize workout time format (add :00 if only HH:MM)
    if workout_time.count(":") == 1:
        workout_time = workout_time + ":00"

    # Prepare data
    df["first_appearance"] = df.groupby(["Date", "Exercise"]).cumcount()
    df["exercise_order"] = df.groupby(["Date", "Exercise"])[
        "first_appearance"
    ].transform("idxmin")

    # Convert fields
    df["Workout #"] = df.groupby("Date").ngroup() + 1
    df["Date"] = (
        pd.to_datetime(df["Date"] + " " + workout_time)
        - timedelta(hours=timezone_offset)
    ).dt.strftime("%Y-%m-%d %H:%M:%S")
    df["Workout Name"] = workout_name

    duration_str = str(workout_duration).lower()
    duration_sec = (
        int(duration_str.replace("m", "")) * 60
        if "m" in duration_str
        else (
            int(duration_str.replace("s", ""))
            if "s" in duration_str
            else int(duration_str)
        )
    )
    df["Duration (sec)"] = duration_sec

    df["Exercise Name"] = df["Exercise"].map(mappings).fillna(df["Exercise"])

    df = df.sort_values(["Date", "exercise_order", "first_appearance"])
    df["Set Order"] = df.groupby(["Date", "Exercise Name"]).cumcount() + 1
    df["Weight (kg)"] = df["Weight"].apply(
        lambda x: str(x) if pd.notna(x) and x != "" else ""
    )

    # Convert reps
    def convert_reps(row):
        if pd.notna(row["Reps"]) and row["Reps"] != "":
            return int(row["Reps"])
        if row["Exercise Name"] in TIME_TO_REPS_EXERCISES:
            secs = parse_time_to_seconds(row.get("Time", ""))
            if secs > 0:
                return max(1, secs // 10)
        return ""

    df["Reps"] = df.apply(convert_reps, axis=1).astype(object)

    # Convert distance
    def convert_distance(row):
        if (
            "Distance" in row
            and pd.notna(row["Distance"])
            and row["Distance"] != ""
            and row["Distance"] != 0
        ):
            return str(int(row["Distance"]))
        if row["Exercise Name"] in TIME_TO_DISTANCE_EXERCISES:
            secs = parse_time_to_seconds(row.get("Time", ""))
            if secs > 0:
                return str(secs)
        return ""

    df["Distance (meters)"] = df.apply(convert_distance, axis=1)

    # Convert seconds
    def convert_seconds(row):
        if row["Exercise Name"] in REPS_TO_TIME_EXERCISES:
            if pd.notna(row["Reps"]) and row["Reps"] != "":
                return str(float(row["Reps"]))

        if (
            row["Exercise Name"] in TIME_TO_REPS_EXERCISES
            and pd.notna(row["Reps"])
            and row["Reps"] != ""
        ):
            return ""
        if (
            row["Exercise Name"] in TIME_TO_DISTANCE_EXERCISES
            and pd.notna(row["Distance (meters)"])
            and row["Distance (meters)"] != ""
        ):
            return ""

        secs = parse_time_to_seconds(row.get("Time", ""))
        return str(float(secs)) if secs > 0 else ""

    df["Seconds"] = df.apply(convert_seconds, axis=1)
    # Convert Reps to empty string for time-based exercises
    mask = df["Exercise Name"].isin(REPS_TO_TIME_EXERCISES)
    df.loc[mask, "Reps"] = ""

    df["Notes"] = df["Comment"].fillna("") if "Comment" in df.columns else ""

    # Add conversion notes
    def add_conversion_note(row):
        note = str(row["Notes"]) if row["Notes"] else ""
        if row["Exercise"] != row["Exercise Name"]:
            if (
                "backward" in row["Exercise"].lower()
                and "walk" in row["Exercise"].lower()
            ) or row["Exercise Name"] in ["Warm Up", "Stretching"]:
                return f"{row['Exercise']}; {note}" if note else row["Exercise"]
        return note

    df["Notes"] = df.apply(add_conversion_note, axis=1)
    df["Workout Notes"] = workout_notes
    df["RPE"] = ""

    # Return formatted columns
    columns = [
        "Workout #",
        "Date",
        "Workout Name",
        "Duration (sec)",
        "Exercise Name",
        "Set Order",
        "Weight (kg)",
        "Reps",
        "RPE",
        "Distance (meters)",
        "Seconds",
        "Notes",
        "Workout Notes",
    ]
    return df[columns]
